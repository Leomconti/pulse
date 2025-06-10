import json

from app.llm_clients.openai_client import openai_client
from app.models import Context, MapperOutput

# Agent dependency requirements
requires: list[str] = ["planner_output"]


async def mapper_agent(ctx: Context) -> Context:
    """
    Mapper agent: Map planner output to database schema.

    This agent takes the structured representation from the planner and maps
    it to actual database tables and columns using the provided schema.
    """

    if not ctx.planner_output:
        raise ValueError("Planner output is required but not found in context")

    # Build system prompt for the mapper
    system_prompt = f"""You are a database schema mapper that takes structured query components and maps them to specific database tables and columns.

Your task is to map the planner's structured output to the actual database schema:
1. Map entities to specific database tables and columns
2. Map filters to the correct database columns with proper table prefixes
3. Map aggregations to the correct database columns with proper table prefixes
4. Map order_by to the correct database column with proper table prefix

Available database schema:
{json.dumps(ctx.schema, indent=2)}

Mapping Rules:
- For entities of type "table", set column to None and map to the actual table name
- For entities of type "column", map to the specific table.column combination
- For filters, map column names to their full table.column format
- For aggregations, map column names to their full table.column format (use "*" for COUNT(*))
- For order_by, map to the full table.column format
- Use the exact table and column names from the schema
- If a mapping is ambiguous, choose the most relevant table based on the query context
"""

    # Build user prompt with planner output
    user_prompt = f"""Map these planner components to the database schema:

Original Query: "{ctx.query}"

Planner Output:
{json.dumps(ctx.planner_output.model_dump(), indent=2)}

Map each component to the correct database tables and columns based on the provided schema."""

    try:
        # Call OpenAI with structured output
        mapper_output = await openai_client.call_structured(
            model="gpt-4o-mini", system_prompt=system_prompt, user_prompt=user_prompt, output_model=MapperOutput
        )

        # Update context
        ctx.mapper_output = mapper_output
        ctx.current_step = "mapper"
        ctx.update_timestamp()

        return ctx

    except Exception as e:
        raise ValueError(f"Mapper agent failed: {str(e)}")

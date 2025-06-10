import json

from app.llm_clients.openai_client import openai_client
from app.models import ComposerOutput, Context

# Agent dependency requirements
requires: list[str] = ["mapper_output"]


async def composer_agent(ctx: Context) -> Context:
    """
    Composer agent: Construct SQL query from mapper output.

    This agent takes the mapped entities, filters, and aggregations and
    constructs a complete SQL query string.
    """

    if not ctx.mapper_output:
        raise ValueError("Mapper output is required but not found in context")

    # Build system prompt for the composer
    system_prompt = f"""You are a SQL query composer that generates valid SQL queries from mapped database components.

Your task is to construct a complete, syntactically correct SQL query using the mapped components:
1. Build SELECT clause from mapped entities and aggregations
2. Build FROM clause from mapped entities (tables)
3. Build WHERE clause from mapped filters
4. Build ORDER BY clause from mapped order_by
5. Add LIMIT clause if specified in the original planner output

Available database schema:
{json.dumps(ctx.schema, indent=2)}

SQL Generation Rules:
- Use proper SQL syntax and formatting
- Join tables correctly when multiple tables are involved
- Handle aggregations properly (GROUP BY when needed)
- Use appropriate quotes for string values in WHERE clauses
- Generate clean, readable SQL
- Ensure the query is executable and valid
"""

    # Build user prompt with mapper output and original query context
    user_prompt = f"""Generate a SQL query from these mapped components:

Original Query: "{ctx.query}"

Planner Output:
{json.dumps(ctx.planner_output.model_dump() if ctx.planner_output else {}, indent=2)}

Mapper Output:
{json.dumps(ctx.mapper_output.model_dump(), indent=2)}

Generate a complete, valid SQL query that fulfills the original request."""

    try:
        # Call OpenAI with structured output
        composer_output = await openai_client.call_structured(
            model="gpt-4o-mini", system_prompt=system_prompt, user_prompt=user_prompt, output_model=ComposerOutput
        )

        # Update context
        ctx.composer_output = composer_output
        ctx.current_step = "composer"
        ctx.update_timestamp()

        return ctx

    except Exception as e:
        raise ValueError(f"Composer agent failed: {str(e)}")

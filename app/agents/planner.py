import json

from app.llm_clients.openai_client import openai_client
from app.models import Context, PlannerOutput

# Agent dependency requirements
requires: list[str] = []  # Planner is the first agent, no dependencies


async def planner_agent(ctx: Context) -> Context:
    """
    Planner agent: Parse natural language input into structured representation.

    This agent identifies the intent, entities, filters, and aggregations from
    the user's query and populates ctx.planner_output.
    """

    # Build system prompt for the planner
    system_prompt = f"""You are a SQL query planner that analyzes natural language queries about healthcare processes and extracts structured information.

Your task is to parse the user's natural language query and identify:
1. Intent: The type of operation (select, aggregate, filter)
2. Entities: Tables or columns mentioned (name and type)
3. Filters: Conditions to apply (column, operator, value)
4. Aggregations: Mathematical operations to perform (function, column)
5. Limit: Number of results to return (if specified)
6. Order by: Column to sort results by (if specified)

Available database schema:
{json.dumps(ctx.schema, indent=2)}

Instructions:
- For intent: use "select" for basic queries, "aggregate" for COUNT/SUM/AVG operations, "filter" for WHERE conditions
- For entities: identify table names and column references, specify type as "table" or "column"
- For filters: extract WHERE conditions with proper operators (=, >, <, LIKE, etc.)
- For aggregations: identify functions like COUNT, SUM, AVG, MAX, MIN and their target columns
- Extract LIMIT values and ORDER BY columns when mentioned
- Be precise and only extract what is clearly mentioned in the query
"""

    # Build user prompt with the actual query
    user_prompt = f"""Parse this natural language query:

Query: "{ctx.query}"

Extract the structured components following the schema requirements."""

    try:
        # Call OpenAI with structured output
        planner_output = await openai_client.call_structured(
            model="gpt-4o-mini", system_prompt=system_prompt, user_prompt=user_prompt, output_model=PlannerOutput
        )

        # Update context
        ctx.planner_output = planner_output
        ctx.current_step = "planner"
        ctx.update_timestamp()

        return ctx

    except Exception as e:
        raise ValueError(f"Planner agent failed: {str(e)}")

import json

from app.llm_clients.openai_client import openai_client
from app.models import Context, ValidatorOutput

# Agent dependency requirements
requires: list[str] = ["composer_output"]


async def validator_agent(ctx: Context) -> Context:
    """
    Validator agent: Validate SQL query and provide feedback.

    This agent checks the SQL query for correctness, validates it against
    the original intent, and provides feedback for improvements if needed.
    """

    if not ctx.composer_output:
        raise ValueError("Composer output is required but not found in context")

    # Build system prompt for the validator
    system_prompt = f"""You are a SQL query validator that ensures generated queries are correct, secure, and align with the original intent.

Your task is to validate the SQL query comprehensively:
1. Syntax validation: Check for proper SQL syntax and structure
2. Security validation: Check for SQL injection vulnerabilities
3. Schema validation: Verify tables and columns exist in the schema
4. Intent alignment: Ensure the query matches the original natural language request
5. Logical validation: Check for logical errors and potential issues

Available database schema:
{json.dumps(ctx.schema, indent=2)}

Validation Criteria:
- SQL must be syntactically correct
- All tables and columns must exist in the schema
- No dangerous SQL patterns (DROP, DELETE without WHERE, etc.)
- Query should match the original intent (SELECT vs AGGREGATE vs FILTER)
- Aggregations should have proper GROUP BY when needed
- JOINs should be correct when multiple tables are involved
- Data types should be compatible in comparisons

Provide detailed feedback if issues are found, including specific suggestions for fixes."""

    # Build user prompt with all context
    user_prompt = f"""Validate this SQL query:

Original Query: "{ctx.query}"

Schema: {json.dumps(ctx.schema, indent=2)}

Generated SQL Query:
{ctx.composer_output.sql_query}

Perform comprehensive validation and provide detailed feedback if any issues are found."""

    try:
        # Call OpenAI with structured output
        validator_output = await openai_client.call_structured(
            model="gpt-4o-mini", system_prompt=system_prompt, user_prompt=user_prompt, output_model=ValidatorOutput
        )

        # Update context
        ctx.validator_output = validator_output
        ctx.current_step = "validator"
        ctx.update_timestamp()

        # If validation failed, set feedback for potential retry
        if not validator_output.validation.is_valid:
            ctx.feedback = validator_output.validation.feedback

        return ctx

    except Exception as e:
        raise ValueError(f"Validator agent failed: {str(e)}")

from app.models import Context, ValidationResult, ValidatorOutput

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

    sql_query = ctx.composer_output.sql_query
    planner_output = ctx.planner_output

    # Validation logic
    errors = []
    feedback = None
    is_valid = True
    query_output = None

    # Basic SQL syntax validation
    sql_lower = sql_query.lower().strip()

    if not sql_lower.startswith("select"):
        errors.append("Query must start with SELECT")
        is_valid = False

    if "from" not in sql_lower:
        errors.append("Query must include FROM clause")
        is_valid = False

    # Check for SQL injection patterns (basic)
    dangerous_patterns = [";--", "; --", "drop table", "delete from", "update set"]
    for pattern in dangerous_patterns:
        if pattern in sql_lower:
            errors.append(f"Potentially dangerous SQL pattern detected: {pattern}")
            is_valid = False

    # Validate against original intent
    if planner_output:
        # Check if aggregations match intent
        if planner_output.intent == "aggregate":
            agg_functions = ["count(", "sum(", "avg(", "max(", "min("]
            if not any(func in sql_lower for func in agg_functions):
                errors.append("Query should include aggregation functions based on intent")
                is_valid = False

        # Check if filters are present when expected
        if planner_output.filters and "where" not in sql_lower:
            errors.append("Query should include WHERE clause for filters")
            is_valid = False

        # Check if LIMIT is present when specified
        if planner_output.limit and "limit" not in sql_lower:
            errors.append("Query should include LIMIT clause as requested")
            is_valid = False

    # Mock query execution validation
    try:
        # In a real implementation, this would execute the query against the database
        # For now, we'll simulate some basic execution results
        if is_valid:
            query_output = "Query executed successfully (mock result)"
        else:
            query_output = "Query validation failed"
    except Exception as e:
        errors.append(f"Query execution error: {str(e)}")
        is_valid = False
        query_output = f"Execution error: {str(e)}"

    # Generate feedback for improvements
    if not is_valid:
        feedback_parts = []

        if errors:
            feedback_parts.append("Issues found:")
            feedback_parts.extend([f"- {error}" for error in errors])

        # Provide specific suggestions
        if planner_output:
            if planner_output.intent == "aggregate" and not any(
                func in sql_lower for func in ["count(", "sum(", "avg("]
            ):
                feedback_parts.append("Suggestion: Add appropriate aggregation functions (COUNT, SUM, AVG)")

            if planner_output.filters and "where" not in sql_lower:
                feedback_parts.append("Suggestion: Add WHERE clause to apply filters")

        feedback = "\n".join(feedback_parts)

    # Create validation result
    validation_result = ValidationResult(
        is_valid=is_valid, errors=errors if errors else None, feedback=feedback, query_output=query_output
    )

    # Create validator output
    validator_output = ValidatorOutput(validation=validation_result)

    # Update context
    ctx.validator_output = validator_output
    ctx.current_step = "validator"
    ctx.update_timestamp()

    # If validation failed, set feedback for potential retry
    if not is_valid:
        ctx.feedback = feedback

    return ctx

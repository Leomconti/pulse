from app.models import ComposerOutput, Context

# Agent dependency requirements
requires: list[str] = ["mapper_output"]


def composer_agent(ctx: Context) -> Context:
    """
    Composer agent: Construct SQL query from mapper output.

    This agent takes the mapped entities, filters, and aggregations and
    constructs a complete SQL query string.
    """

    if not ctx.mapper_output:
        raise ValueError("Mapper output is required but not found in context")

    mapper_output = ctx.mapper_output
    planner_output = ctx.planner_output

    # Start building the SQL query
    query_parts = []

    # SELECT clause
    if mapper_output.mapped_aggregations:
        # Build aggregation SELECT
        select_parts = []
        for mapped_agg in mapper_output.mapped_aggregations:
            agg = mapped_agg.aggregation
            col = mapped_agg.mapped_column
            select_parts.append(f"{agg.function}({col})")
        select_clause = f"SELECT {', '.join(select_parts)}"
    else:
        # Build regular SELECT
        if mapper_output.mapped_entities:
            table_columns = []
            for entity in mapper_output.mapped_entities:
                if entity.column:
                    table_columns.append(f"{entity.table}.{entity.column}")
                else:
                    table_columns.append(f"{entity.table}.*")
            select_clause = f"SELECT {', '.join(table_columns) if table_columns else '*'}"
        else:
            select_clause = "SELECT *"

    query_parts.append(select_clause)

    # FROM clause
    if mapper_output.mapped_entities:
        tables = list({entity.table for entity in mapper_output.mapped_entities})
        from_clause = f"FROM {', '.join(tables)}"
    else:
        from_clause = "FROM users"  # Default table

    query_parts.append(from_clause)

    # WHERE clause
    if mapper_output.mapped_filters:
        where_conditions = []
        for mapped_filter in mapper_output.mapped_filters:
            filter_obj = mapped_filter.filter
            column = mapped_filter.mapped_column
            operator = filter_obj.operator
            value = filter_obj.value

            # Handle different value types
            if operator.upper() == "LIKE":
                condition = f"{column} {operator} '%{value}%'"
            elif value.isdigit():
                condition = f"{column} {operator} {value}"
            else:
                condition = f"{column} {operator} '{value}'"

            where_conditions.append(condition)

        where_clause = f"WHERE {' AND '.join(where_conditions)}"
        query_parts.append(where_clause)

    # ORDER BY clause
    if mapper_output.mapped_order_by:
        order_clause = f"ORDER BY {mapper_output.mapped_order_by}"
        query_parts.append(order_clause)

    # LIMIT clause
    if planner_output and planner_output.limit:
        limit_clause = f"LIMIT {planner_output.limit}"
        query_parts.append(limit_clause)

    # Combine all parts
    sql_query = " ".join(query_parts)

    # Create composer output
    composer_output = ComposerOutput(sql_query=sql_query)

    # Update context
    ctx.composer_output = composer_output
    ctx.current_step = "composer"
    ctx.update_timestamp()

    return ctx

from app.models import Context, MappedAggregation, MappedEntity, MappedFilter, MapperOutput

# Agent dependency requirements
requires: list[str] = ["planner_output"]


def mapper_agent(ctx: Context) -> Context:
    """
    Mapper agent: Map planner output to database schema.

    This agent takes the structured representation from the planner and maps
    it to actual database tables and columns using the provided schema.
    """

    if not ctx.planner_output:
        raise ValueError("Planner output is required but not found in context")

    # Get schema and planner output
    schema = ctx.schema
    planner_output = ctx.planner_output

    # Map entities to database tables and columns
    mapped_entities = []
    for entity in planner_output.entities:
        # Mock mapping logic - in real scenario, this would use schema analysis
        if entity.name.lower() == "users":
            mapped_entities.append(
                MappedEntity(
                    entity_name=entity.name, table="users", column=None if entity.type == "table" else "user_id"
                )
            )
        elif entity.name.lower() == "orders":
            mapped_entities.append(
                MappedEntity(
                    entity_name=entity.name, table="orders", column=None if entity.type == "table" else "order_id"
                )
            )
        elif entity.name.lower() == "products":
            mapped_entities.append(
                MappedEntity(
                    entity_name=entity.name, table="products", column=None if entity.type == "table" else "product_id"
                )
            )

    # Map filters to database columns
    mapped_filters = []
    for filter_obj in planner_output.filters:
        # Mock column mapping
        mapped_column = filter_obj.column
        if filter_obj.column == "status" and any(e.table == "users" for e in mapped_entities):
            mapped_column = "users.status"
        elif filter_obj.column == "age" and any(e.table == "users" for e in mapped_entities):
            mapped_column = "users.age"

        mapped_filters.append(MappedFilter(filter=filter_obj, mapped_column=mapped_column))

    # Map aggregations to database columns
    mapped_aggregations = []
    for agg in planner_output.aggregations:
        # Mock column mapping for aggregations
        mapped_column = agg.column
        if agg.column == "*":
            mapped_column = "*"
        elif agg.column == "price" and any(e.table == "products" for e in mapped_entities):
            mapped_column = "products.price"
        elif agg.column == "age" and any(e.table == "users" for e in mapped_entities):
            mapped_column = "users.age"

        mapped_aggregations.append(MappedAggregation(aggregation=agg, mapped_column=mapped_column))

    # Map order_by column
    mapped_order_by = None
    if planner_output.order_by:
        if planner_output.order_by == "name" and any(e.table == "users" for e in mapped_entities):
            mapped_order_by = "users.name"
        elif planner_output.order_by == "created_at":
            # Find the main table to use for ordering
            main_table = mapped_entities[0].table if mapped_entities else "users"
            mapped_order_by = f"{main_table}.created_at"
        else:
            mapped_order_by = planner_output.order_by

    # Create mapper output
    mapper_output = MapperOutput(
        mapped_entities=mapped_entities,
        mapped_filters=mapped_filters,
        mapped_aggregations=mapped_aggregations,
        mapped_order_by=mapped_order_by,
    )

    # Update context
    ctx.mapper_output = mapper_output
    ctx.current_step = "mapper"
    ctx.update_timestamp()

    return ctx

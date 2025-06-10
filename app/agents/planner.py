from app.models import Aggregation, Context, Entity, Filter, PlannerOutput

# Agent dependency requirements
requires: list[str] = []  # Planner is the first agent, no dependencies


def planner_agent(ctx: Context) -> Context:
    """
    Planner agent: Parse natural language input into structured representation.

    This agent identifies the intent, entities, filters, and aggregations from
    the user's query and populates ctx.planner_output.
    """

    # Mock implementation - in real scenario, this would use LLM
    # For now, we'll create a simple mock based on query keywords
    query = ctx.query.lower()

    # Mock intent detection
    if any(word in query for word in ["count", "sum", "average", "avg", "total"]):
        intent = "aggregate"
    elif any(word in query for word in ["where", "filter", "only"]):
        intent = "filter"
    else:
        intent = "select"

    # Mock entity extraction
    entities = []
    if "users" in query or "user" in query:
        entities.append(Entity(name="users", type="table"))
    if "orders" in query or "order" in query:
        entities.append(Entity(name="orders", type="table"))
    if "products" in query or "product" in query:
        entities.append(Entity(name="products", type="table"))

    # Mock filter extraction
    filters = []
    if "active" in query:
        filters.append(Filter(column="status", operator="=", value="active"))
    if "age" in query and ">" in query:
        filters.append(Filter(column="age", operator=">", value="18"))

    # Mock aggregation extraction
    aggregations = []
    if "count" in query:
        aggregations.append(Aggregation(function="COUNT", column="*"))
    if "sum" in query and "price" in query:
        aggregations.append(Aggregation(function="SUM", column="price"))
    if "average" in query or "avg" in query:
        if "age" in query:
            aggregations.append(Aggregation(function="AVG", column="age"))
        elif "price" in query:
            aggregations.append(Aggregation(function="AVG", column="price"))

    # Mock limit and order_by extraction
    limit = None
    if "limit" in query:
        words = query.split()
        try:
            limit_idx = words.index("limit")
            if limit_idx + 1 < len(words):
                limit = int(words[limit_idx + 1])
        except (ValueError, IndexError):
            pass

    order_by = None
    if "order by" in query:
        if "name" in query:
            order_by = "name"
        elif "date" in query:
            order_by = "created_at"

    # Create planner output
    planner_output = PlannerOutput(
        intent=intent, entities=entities, filters=filters, aggregations=aggregations, limit=limit, order_by=order_by
    )

    # Update context
    ctx.planner_output = planner_output
    ctx.current_step = "planner"
    ctx.update_timestamp()

    return ctx

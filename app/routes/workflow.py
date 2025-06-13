import json
from datetime import datetime
from typing import Optional

from app.orchestrator import get_workflow_status
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# Add custom filters for workflow templates
def timestamp_to_datetime(timestamp: float) -> str:
    """Convert Unix timestamp to readable datetime format."""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, OSError):
        return "Invalid datetime"


def tojsonpretty_filter(value) -> str:
    """Convert value to pretty printed JSON."""
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


# Register the filters
templates.env.filters["timestamp_to_datetime"] = timestamp_to_datetime
templates.env.filters["tojsonpretty"] = tojsonpretty_filter


class WorkflowRequest(BaseModel):
    query: str
    schema: dict
    user_id: Optional[str] = None


class WorkflowResponse(BaseModel):
    request_id: str


class WorkflowStatusResponse(BaseModel):
    status: str
    current: Optional[str]


class StepOutput(BaseModel):
    name: str
    status: str  # "pending", "running", "done", "failed"
    output: Optional[dict] = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None


@router.post("/workflows")
async def start_workflow(request: WorkflowRequest):
    """Start a new workflow (API version) and immediately return the request_id.

    Unlike the HTMX helpers, this endpoint is meant for programmatic access (e.g. the
    NextJS frontend in `frontend/`).  We **must not** await the full execution of the
    workflow here – doing so would block the response until all agents finish running
    and would prevent the client from polling the `/steps` and `/status` endpoints in
    real-time.

    The strategy is therefore:
      1. Create the initial Context.
      2. Persist it to Redis so that the polling endpoints can immediately return a
         "pending" workflow.
      3. Spawn the long-running execution in the background with
         `asyncio.create_task`.
      4. Return the freshly generated `request_id` to the caller.
    """

    try:
        # Lazily import heavy deps to keep module import fast
        import asyncio

        from app.models import Context
        from app.orchestrator import create_orchestrator

        # 1. Create the initial context
        ctx = Context(query=request.query, schema=request.schema, user_id=request.user_id)

        # 2. Persist immediately so that status/steps endpoints work right away
        orchestrator = create_orchestrator()
        await orchestrator.save_context(ctx)

        # 3. Trigger background execution (fire-and-forget)
        asyncio.create_task(orchestrator.execute_workflow(ctx))

        # 4. Return the request id for the client to start polling
        return WorkflowResponse(request_id=str(ctx.request_id))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")


@router.post("/workflows/start-htmx", response_class=HTMLResponse)
async def start_workflow_htmx(request: Request, query: str = Form(...), schema: str = Form(...)):
    """Start workflow for HTMX frontend - expects form data."""
    try:
        print(f"DEBUG: Received query: {query}")
        print(f"DEBUG: Received schema: {schema[:100]}...")  # First 100 chars

        if not query or not schema:
            return templates.TemplateResponse(
                "partials/workflow_panel.html", {"request": request, "error": "Missing query or schema"}
            )

        # Parse schema JSON
        try:
            schema_dict = json.loads(schema)
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            return templates.TemplateResponse(
                "partials/workflow_panel.html", {"request": request, "error": "Invalid JSON schema format"}
            )

        # Create context immediately and save to Redis
        import asyncio

        from app.models import Context
        from app.orchestrator import create_orchestrator

        ctx = Context(query=query, schema=schema_dict)
        orchestrator = create_orchestrator()

        # Save initial context
        await orchestrator.save_context(ctx)

        request_id_str = str(ctx.request_id)
        print(f"DEBUG: Generated request_id: {request_id_str}")

        # Start workflow execution in background (fire and forget)
        asyncio.create_task(orchestrator.execute_workflow(ctx))

        # Return template immediately with request_id
        return templates.TemplateResponse(
            "partials/workflow_panel.html", {"request": request, "request_id": request_id_str}
        )

    except Exception as e:
        print(f"DEBUG: Error in start_workflow_htmx: {e}")
        import traceback

        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "partials/workflow_panel.html", {"request": request, "error": f"Failed to start workflow: {str(e)}"}
        )


@router.post("/workflows/start-with-connection", response_class=HTMLResponse)
async def start_workflow_with_connection(request: Request, query: str = Form(...), connection_id: str = Form(...)):
    """Start workflow for HTMX frontend using a database connection ID to get schema."""
    try:
        print(f"DEBUG: Received query: {query}")
        print(f"DEBUG: Received connection_id: {connection_id}")

        if not query or not connection_id:
            return templates.TemplateResponse(
                "partials/workflow_panel.html", {"request": request, "error": "Missing query or connection ID"}
            )

        # Get schema from database connection
        from app.models import DatabaseConnection
        from app.services.redis_ops import get_data
        from app.services.sql_runner import get_database_schema

        try:
            connection = await get_data(connection_id, DatabaseConnection)
            schema_dict = await get_database_schema(connection)
        except KeyError:
            return templates.TemplateResponse(
                "partials/workflow_panel.html", {"request": request, "error": "Database connection not found"}
            )
        except Exception as e:
            print(f"DEBUG: Error getting schema: {e}")
            return templates.TemplateResponse(
                "partials/workflow_panel.html",
                {"request": request, "error": f"Failed to get database schema: {str(e)}"},
            )

        # Create context immediately and save to Redis
        import asyncio

        from app.models import Context
        from app.orchestrator import create_orchestrator

        ctx = Context(query=query, schema=schema_dict)
        orchestrator = create_orchestrator()

        # Save initial context
        await orchestrator.save_context(ctx)

        request_id_str = str(ctx.request_id)
        print(f"DEBUG: Generated request_id: {request_id_str}")

        # Start workflow execution in background (fire and forget)
        asyncio.create_task(orchestrator.execute_workflow(ctx))

        # Return template immediately with request_id
        return templates.TemplateResponse(
            "partials/workflow_panel.html", {"request": request, "request_id": request_id_str}
        )

    except Exception as e:
        print(f"DEBUG: Error in start_workflow_with_connection: {e}")
        import traceback

        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "partials/workflow_panel.html", {"request": request, "error": f"Failed to start workflow: {str(e)}"}
        )


@router.get("/workflows/{request_id}/status", response_model=WorkflowStatusResponse)
async def get_status(request_id: str):
    """Get the overall workflow status."""
    try:
        status_info = await get_workflow_status(request_id)
        if not status_info:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return WorkflowStatusResponse(status=status_info["status"], current=status_info.get("current_step"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


@router.get("/workflows/{request_id}/steps", response_model=list[StepOutput])
async def get_workflow_steps(request_id: str):
    """Get detailed step information for a workflow."""
    try:
        status_info = await get_workflow_status(request_id)
        if not status_info:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Define the workflow steps in order
        step_names = ["planner", "mapper", "composer", "validator"]
        steps = []

        current_step = status_info.get("current_step")
        workflow_status = status_info.get("status", "pending")

        for i, step_name in enumerate(step_names):
            step_status = _determine_step_status(step_name, current_step, workflow_status, status_info)

            output = _get_step_output(step_name, status_info)

            # For simplicity, we'll use created_at and updated_at from the workflow
            # In a real implementation, you'd want to track individual step timings
            started_at = status_info.get("created_at") if step_status in ["running", "done"] else None
            finished_at = status_info.get("updated_at") if step_status == "done" else None

            steps.append(
                StepOutput(
                    name=step_name, status=step_status, output=output, started_at=started_at, finished_at=finished_at
                )
            )

        return steps

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow steps: {str(e)}")


@router.get("/workflows/{request_id}/steps-htmx", response_class=HTMLResponse)
async def get_workflow_steps_htmx(request: Request, request_id: str):
    """Get workflow steps for HTMX frontend."""
    try:
        print(f"DEBUG: Fetching steps for request_id: '{request_id}'")

        status_info = await get_workflow_status(request_id)
        if not status_info:
            print(f"DEBUG: No workflow found for request_id: '{request_id}'")
            return templates.TemplateResponse(
                "partials/workflow_steps.html", {"request": request, "steps": [], "error": "Workflow not found"}
            )

        print(f"DEBUG: Found workflow status: {status_info}")

        # Create steps data for template
        step_names = ["planner", "mapper", "composer", "validator"]
        steps = []

        current_step = status_info.get("current_step")
        workflow_status = status_info.get("status", "pending")

        for step_name in step_names:
            step_status = _determine_step_status(step_name, current_step, workflow_status, status_info)
            output = _get_step_output(step_name, status_info)

            # Use workflow timestamps for simplicity
            started_at = status_info.get("created_at") if step_status in ["running", "done"] else None
            finished_at = status_info.get("updated_at") if step_status == "done" else None

            step_data = {
                "name": step_name,
                "status": step_status,
                "output": output,
                "started_at": started_at,
                "finished_at": finished_at,
            }

            print(f"DEBUG: Step {step_name} -> status: {step_status}, output: {output}")
            steps.append(step_data)

        print(f"DEBUG: Total steps created: {len(steps)}")
        print(f"DEBUG: Steps data: {steps}")

        # Double-check the steps right before template response
        print(f"DEBUG: About to render template with {len(steps)} steps")
        print(f"DEBUG: Template context: request={request}, steps={steps}")

        template_response = templates.TemplateResponse(
            "partials/workflow_steps.html", {"request": request, "steps": steps}
        )
        print(f"DEBUG: Template response created successfully")

        return template_response

    except Exception as e:
        print(f"DEBUG: Exception in get_workflow_steps_htmx: {e}")
        import traceback

        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return templates.TemplateResponse(
            "partials/workflow_steps.html",
            {"request": request, "steps": [], "error": f"Failed to get workflow steps: {str(e)}"},
        )


def _determine_step_status(step_name: str, current_step: Optional[str], workflow_status: str, status_info: dict) -> str:
    """Determine the status of an individual step."""
    step_order = ["planner", "mapper", "composer", "validator"]

    if workflow_status == "failed":
        return "failed"

    if not current_step:
        return "pending"

    current_index = step_order.index(current_step) if current_step in step_order else -1
    step_index = step_order.index(step_name)

    if step_index > current_index:
        return "pending"
    elif step_index == current_index:
        if workflow_status in ["running", "retrying"]:
            return "running"
        elif workflow_status == "completed":
            return "done"
        else:
            return "pending"
    else:  # step_index < current_index
        return "done"


def _get_step_output(step_name: str, status_info: dict) -> Optional[dict]:
    """Get the output for a specific step."""
    output_mapping = {
        "planner": "planner_output",
        "mapper": "mapper_output",
        "composer": "composer_output",
        "validator": "validator_output",
    }

    # For the status info response, we need to check if outputs exist
    if step_name == "planner" and status_info.get("has_planner_output"):
        return {"intent": "aggregate", "entities": ["users"], "filters": []}  # Simplified
    elif step_name == "mapper" and status_info.get("has_mapper_output"):
        return {"mapped_entities": [], "mapped_filters": []}  # Simplified
    elif step_name == "composer" and status_info.get("has_composer_output"):
        sql_query = status_info.get("sql_query")
        return {"sql_query": sql_query} if sql_query else None
    elif step_name == "validator" and status_info.get("has_validator_output"):
        is_valid = status_info.get("is_valid")
        return {"validation": {"is_valid": is_valid}} if is_valid is not None else None

    return None

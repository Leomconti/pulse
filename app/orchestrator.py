import asyncio
import json
from typing import Optional

import logfire

from app.agents import composer_agent, mapper_agent, planner_agent, validator_agent
from app.models import Context, WorkflowStatus
from app.services.redis import redis


class WorkflowOrchestrator:
    """
    Simplified workflow orchestrator for agentic workflows.

    Executes agents in a linear sequence: planner -> mapper -> composer -> validator
    with retry logic on composer -> validator if validation fails.
    """

    def __init__(self):
        self.redis_client = redis

    async def save_context(self, ctx: Context):
        """Save context to Redis."""
        key = f"workflow:{ctx.request_id}"
        data = ctx.to_dict()
        await self.redis_client.setex(key, 3600, json.dumps(data))  # 1 hour TTL

    async def load_context(self, request_id: str) -> Optional[Context]:
        """Load context from Redis."""
        key = f"workflow:{request_id}"
        data = await self.redis_client.get(key)

        if data:
            if isinstance(data, bytes):
                data_str = data.decode("utf-8")
            else:
                data_str = str(data)
            return Context.from_dict(json.loads(data_str))
        return None

    async def execute_agent_with_delay(self, agent_func, ctx: Context, agent_name: str) -> Context:
        """Execute an agent with simulated processing delay for better UX."""
        logfire.info(f"Starting {agent_name} agent processing...")

        updated_ctx = await agent_func(ctx)

        # Ensure we have a Context object
        if not isinstance(updated_ctx, Context):
            raise ValueError(f"Agent {agent_name} must return a Context object")

        # Save context after each step
        await self.save_context(updated_ctx)
        logfire.info(f"Completed {agent_name} agent")

        return updated_ctx

    def should_retry(self, ctx: Context) -> bool:
        """Determine if the workflow should retry based on validator feedback."""
        if not ctx.validator_output:
            return False

        # Check if validation failed and we haven't exceeded retry limit
        validation_failed = not ctx.validator_output.validation.is_valid
        under_retry_limit = ctx.retry_count < ctx.max_retries

        return validation_failed and under_retry_limit

    async def execute_workflow(self, ctx: Context) -> Context:
        """
        Execute the complete workflow: planner -> mapper -> composer -> validator
        with retry logic on composer -> validator if validation fails.
        """
        # Set initial status
        ctx.status = WorkflowStatus.RUNNING
        await self.save_context(ctx)

        try:
            # Execute main workflow sequence
            logfire.info("Starting workflow execution")

            # Step 1: Planner
            ctx.current_step = "planner"
            ctx = await self.execute_agent_with_delay(planner_agent, ctx, "planner")

            # Step 2: Mapper
            ctx.current_step = "mapper"
            ctx = await self.execute_agent_with_delay(mapper_agent, ctx, "mapper")

            # Step 3: Composer
            ctx.current_step = "composer"
            ctx = await self.execute_agent_with_delay(composer_agent, ctx, "composer")

            # Step 4: Validator
            ctx.current_step = "validator"
            ctx = await self.execute_agent_with_delay(validator_agent, ctx, "validator")

            # Handle retry loop if validation failed
            while self.should_retry(ctx):
                logfire.info(f"Validation failed, retrying... (attempt {ctx.retry_count + 1})")
                ctx.retry_count += 1
                ctx.status = WorkflowStatus.RETRYING
                await self.save_context(ctx)

                # Re-execute composer and validator
                ctx.current_step = "composer"
                ctx = await self.execute_agent_with_delay(composer_agent, ctx, "composer")

                ctx.current_step = "validator"
                ctx = await self.execute_agent_with_delay(validator_agent, ctx, "validator")

            # Set final status
            if ctx.validator_output and ctx.validator_output.validation.is_valid:
                ctx.status = WorkflowStatus.COMPLETED
                logfire.info("Workflow completed successfully!")
            else:
                ctx.status = WorkflowStatus.FAILED
                logfire.info("Workflow failed after maximum retries")

        except Exception as e:
            logfire.error(f"Workflow execution error: {e}")
            ctx.status = WorkflowStatus.FAILED
            ctx.feedback = f"Execution error: {str(e)}"

        finally:
            # Always save final context
            ctx.update_timestamp()
            await self.save_context(ctx)

        return ctx

    async def get_workflow_status(self, request_id: str) -> Optional[dict]:
        """Get the current status of a workflow."""
        ctx = await self.load_context(request_id)
        if not ctx:
            return None

        return {
            "request_id": str(ctx.request_id),
            "status": ctx.status.value,
            "current_step": ctx.current_step,
            "retry_count": ctx.retry_count,
            "created_at": ctx.created_at,
            "updated_at": ctx.updated_at,
            "feedback": ctx.feedback,
            "has_planner_output": ctx.planner_output is not None,
            "has_mapper_output": ctx.mapper_output is not None,
            "has_composer_output": ctx.composer_output is not None,
            "has_validator_output": ctx.validator_output is not None,
            "sql_query": ctx.composer_output.sql_query if ctx.composer_output else None,
            "is_valid": ctx.validator_output.validation.is_valid if ctx.validator_output else None,
        }


# Convenience functions for external use
def create_orchestrator() -> WorkflowOrchestrator:
    """Create a new workflow orchestrator instance."""
    return WorkflowOrchestrator()


async def execute_workflow(query: str, schema: dict, user_id: Optional[str] = None) -> Context:
    """Execute a complete workflow with the given query and schema."""
    orchestrator = create_orchestrator()

    # Create initial context
    ctx = Context(
        query=query,
        schema=schema,
        user_id=user_id,
    )

    # Execute workflow
    return await orchestrator.execute_workflow(ctx)


async def get_workflow_status(request_id: str) -> Optional[dict]:
    """Get the status of a workflow by request ID."""
    orchestrator = create_orchestrator()
    return await orchestrator.get_workflow_status(request_id)

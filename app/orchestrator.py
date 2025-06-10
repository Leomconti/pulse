import asyncio
import importlib
import inspect
import json
from collections.abc import Awaitable, Callable
from typing import Optional, Union

import logfire

from app.models import Context, WorkflowStatus
from app.services.redis import redis


class WorkflowOrchestrator:
    """
    DAG-based workflow orchestrator for agentic workflows.

    Manages the execution of agent nodes in a directed acyclic graph,
    handles dependencies, supports feedback loops, and persists state to Redis.
    """

    def __init__(self):
        self.redis_client = redis

        # Define the workflow DAG - adjacency list representation
        self.workflow_dag = {
            "planner": ["mapper"],
            "mapper": ["composer"],
            "composer": ["validator"],
            "validator": [],  # End node
        }

        # Agent registry - maps agent names to their functions (sync or async)
        self.agents: dict[str, Union[Callable[[Context], Context], Callable[[Context], Awaitable[Context]]]] = {}
        self._register_agents()

    def _register_agents(self):
        """Register all agent functions from the agents module."""
        agent_modules = {
            "planner": "app.agents.planner",
            "mapper": "app.agents.mapper",
            "composer": "app.agents.composer",
            "validator": "app.agents.validator",
        }

        for agent_name, module_path in agent_modules.items():
            try:
                module = importlib.import_module(module_path)
                agent_func = getattr(module, f"{agent_name}_agent")
                self.agents[agent_name] = agent_func
            except (ImportError, AttributeError) as e:
                logfire.info(f"Warning: Could not register agent {agent_name}: {e}")

    def get_agent_requirements(self, agent_name: str) -> list[str]:
        """Get the requirements for a specific agent."""
        try:
            module_path = f"app.agents.{agent_name}"
            module = importlib.import_module(module_path)
            return getattr(module, "requires", [])
        except (ImportError, AttributeError):
            return []

    def check_requirements(self, ctx: Context, agent_name: str) -> bool:
        """Check if all requirements for an agent are satisfied."""
        requirements = self.get_agent_requirements(agent_name)

        for req in requirements:
            if not hasattr(ctx, req) or getattr(ctx, req) is None:
                return False

        return True

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

    async def execute_agent(self, ctx: Context, agent_name: str) -> Context:
        """Execute a single agent."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")

        # Check requirements
        if not self.check_requirements(ctx, agent_name):
            missing_reqs = [
                req
                for req in self.get_agent_requirements(agent_name)
                if not hasattr(ctx, req) or getattr(ctx, req) is None
            ]
            raise ValueError(f"Missing requirements for {agent_name}: {missing_reqs}")

        # Add sleep to simulate processing time for better UX
        logfire.info(f"Starting {agent_name} agent processing...")
        await asyncio.sleep(2)  # 2 second delay for each agent

        # Execute the agent (handle both sync and async functions)
        agent_func = self.agents[agent_name]

        # Check if the agent function is async
        if inspect.iscoroutinefunction(agent_func):
            updated_ctx = await agent_func(ctx)
        else:
            updated_ctx = agent_func(ctx)

        # Ensure we have a Context object
        if not isinstance(updated_ctx, Context):
            raise ValueError(f"Agent {agent_name} must return a Context object")

        # Save context after each step
        await self.save_context(updated_ctx)

        return updated_ctx

    def should_retry(self, ctx: Context) -> bool:
        """Determine if the workflow should retry based on validator feedback."""
        if not ctx.validator_output:
            return False

        # Check if validation failed and we haven't exceeded retry limit
        validation_failed = not ctx.validator_output.validation.is_valid
        under_retry_limit = ctx.retry_count < ctx.max_retries

        return validation_failed and under_retry_limit

    def get_retry_path(self) -> list[str]:
        """Get the path of agents to re-execute during retry (composer -> validator)."""
        return ["composer", "validator"]

    async def execute_workflow(self, ctx: Context) -> Context:
        """
        Execute the complete workflow.

        Follows the DAG, handles dependencies, supports feedback loops,
        and persists state at each step.
        """

        # Set initial status
        ctx.status = WorkflowStatus.RUNNING
        await self.save_context(ctx)

        try:
            # Execute the main workflow path
            execution_order = self._get_execution_order()

            for agent_name in execution_order:
                logfire.info(f"Executing agent: {agent_name}")
                ctx.current_step = agent_name
                await self.save_context(ctx)
                ctx = await self.execute_agent(ctx, agent_name)
                logfire.info(f"Completed agent: {agent_name}")

            # Handle feedback loop if validation failed
            while self.should_retry(ctx):
                logfire.info(f"Validation failed, retrying... (attempt {ctx.retry_count + 1})")
                ctx.retry_count += 1
                ctx.status = WorkflowStatus.RETRYING
                await self.save_context(ctx)

                # Execute only the retry path (composer -> validator)
                retry_path = self.get_retry_path()
                for agent_name in retry_path:
                    logfire.info(f"Re-executing agent: {agent_name}")
                    ctx.current_step = agent_name
                    await self.save_context(ctx)
                    ctx = await self.execute_agent(ctx, agent_name)
                    logfire.info(f"Re-completed agent: {agent_name}")

            # Set final status
            if ctx.validator_output and ctx.validator_output.validation.is_valid:
                ctx.status = WorkflowStatus.COMPLETED
                logfire.info("Workflow completed successfully!")
            else:
                ctx.status = WorkflowStatus.FAILED
                logfire.info("Workflow failed after maximum retries")

        except Exception as e:
            logfire.info(f"Workflow execution error: {e}")
            ctx.status = WorkflowStatus.FAILED
            ctx.feedback = f"Execution error: {str(e)}"

        finally:
            # Always save final context
            ctx.update_timestamp()
            await self.save_context(ctx)

        return ctx

    def _get_execution_order(self) -> list[str]:
        """Get the topological order of agent execution."""
        # For this simple DAG, we can use a fixed order
        # In a more complex scenario, you'd implement topological sorting
        return ["planner", "mapper", "composer", "validator"]

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

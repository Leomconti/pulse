#!/usr/bin/env python3
"""
Test script for the agentic workflow system.

This script demonstrates how to use the orchestrator and agents
to process natural language queries into SQL.
"""

import json

from app.orchestrator import execute_workflow, get_workflow_status


def test_basic_workflow():
    """Test a basic workflow execution."""
    print("=" * 60)
    print("TEST: Basic Workflow Execution")
    print("=" * 60)

    # Mock database schema
    schema = {
        "tables": {
            "users": {
                "columns": ["id", "name", "email", "age", "status", "created_at"],
                "types": {
                    "id": "int",
                    "name": "varchar",
                    "email": "varchar",
                    "age": "int",
                    "status": "varchar",
                    "created_at": "timestamp",
                },
            },
            "orders": {
                "columns": ["id", "user_id", "product_id", "quantity", "price", "created_at"],
                "types": {
                    "id": "int",
                    "user_id": "int",
                    "product_id": "int",
                    "quantity": "int",
                    "price": "decimal",
                    "created_at": "timestamp",
                },
            },
            "products": {
                "columns": ["id", "name", "price", "category", "created_at"],
                "types": {
                    "id": "int",
                    "name": "varchar",
                    "price": "decimal",
                    "category": "varchar",
                    "created_at": "timestamp",
                },
            },
        }
    }

    # Test query
    query = "count all active users"

    print(f"Query: {query}")
    print(f"Schema: {json.dumps(schema, indent=2)}")
    print("\nExecuting workflow...")

    # Execute workflow
    try:
        result_ctx = execute_workflow(query, schema, user_id="test_user")

        print(f"\nWorkflow completed!")
        print(f"Request ID: {result_ctx.request_id}")
        print(f"Status: {result_ctx.status}")
        print(f"Current Step: {result_ctx.current_step}")
        print(f"Retry Count: {result_ctx.retry_count}")

        # Show agent outputs
        if result_ctx.planner_output:
            print(f"\n--- Planner Output ---")
            print(f"Intent: {result_ctx.planner_output.intent}")
            print(f"Entities: {[e.name for e in result_ctx.planner_output.entities]}")
            print(f"Filters: {[(f.column, f.operator, f.value) for f in result_ctx.planner_output.filters]}")
            print(f"Aggregations: {[(a.function, a.column) for a in result_ctx.planner_output.aggregations]}")

        if result_ctx.mapper_output:
            print(f"\n--- Mapper Output ---")
            print(f"Mapped Entities: {[(e.entity_name, e.table) for e in result_ctx.mapper_output.mapped_entities]}")
            print(
                f"Mapped Filters: {[(mf.filter.column, mf.mapped_column) for mf in result_ctx.mapper_output.mapped_filters]}"
            )
            print(
                f"Mapped Aggregations: {[(ma.aggregation.function, ma.mapped_column) for ma in result_ctx.mapper_output.mapped_aggregations]}"
            )

        if result_ctx.composer_output:
            print(f"\n--- Composer Output ---")
            print(f"SQL Query: {result_ctx.composer_output.sql_query}")

        if result_ctx.validator_output:
            print(f"\n--- Validator Output ---")
            print(f"Is Valid: {result_ctx.validator_output.validation.is_valid}")
            if result_ctx.validator_output.validation.errors:
                print(f"Errors: {result_ctx.validator_output.validation.errors}")
            if result_ctx.validator_output.validation.feedback:
                print(f"Feedback: {result_ctx.validator_output.validation.feedback}")
            print(f"Query Output: {result_ctx.validator_output.validation.query_output}")

        return result_ctx

    except Exception as e:
        print(f"Error executing workflow: {e}")
        return None


def test_workflow_with_filters():
    """Test workflow with filters that might trigger retry."""
    print("\n" + "=" * 60)
    print("TEST: Workflow with Filters (Complex Query)")
    print("=" * 60)

    schema = {
        "tables": {
            "users": {
                "columns": ["id", "name", "email", "age", "status", "created_at"],
                "types": {
                    "id": "int",
                    "name": "varchar",
                    "email": "varchar",
                    "age": "int",
                    "status": "varchar",
                    "created_at": "timestamp",
                },
            }
        }
    }

    query = "show all users where age > 18 and status is active order by name limit 10"

    print(f"Query: {query}")
    print("\nExecuting workflow...")

    try:
        result_ctx = execute_workflow(query, schema, user_id="test_user_2")

        print(f"\nWorkflow completed!")
        print(f"Status: {result_ctx.status}")
        print(f"Retry Count: {result_ctx.retry_count}")

        if result_ctx.composer_output:
            print(f"Final SQL: {result_ctx.composer_output.sql_query}")

        if result_ctx.validator_output:
            print(f"Validation: {result_ctx.validator_output.validation.is_valid}")
            if result_ctx.feedback:
                print(f"Feedback: {result_ctx.feedback}")

        return result_ctx

    except Exception as e:
        print(f"Error executing workflow: {e}")
        return None


def test_status_retrieval():
    """Test workflow status retrieval."""
    print("\n" + "=" * 60)
    print("TEST: Status Retrieval")
    print("=" * 60)

    # First, execute a workflow
    schema = {"tables": {"users": {"columns": ["id", "name"]}}}
    query = "count users"

    result_ctx = execute_workflow(query, schema)

    if result_ctx:
        print(f"Executed workflow with request_id: {result_ctx.request_id}")

        # Retrieve status
        status = get_workflow_status(str(result_ctx.request_id))

        if status:
            print("\nWorkflow Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        else:
            print("Could not retrieve workflow status")

    return result_ctx


def main():
    """Main test function."""
    print("Starting Agentic Workflow Tests")
    print("=" * 60)

    # Test 1: Basic workflow
    ctx1 = test_basic_workflow()

    # Test 2: Complex query with filters
    ctx2 = test_workflow_with_filters()

    # Test 3: Status retrieval
    ctx3 = test_status_retrieval()

    print("\n" + "=" * 60)
    print("All tests completed!")

    # Summary
    successful_tests = sum([1 for ctx in [ctx1, ctx2, ctx3] if ctx is not None])
    print(f"Successful tests: {successful_tests}/3")

    if successful_tests == 3:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()

import asyncio

from agents.planner_agent import planner_agent
from agents.execution_agent import execution_agent


async def main():

    # Initial user request
    initial_state = {"user_request": "Test SauceDemo login functionality"}

    # Agent 1: Generate test scenarios
    planner_result = planner_agent(initial_state)

    # Share planner output with execution agent
    shared_state = {**initial_state, **planner_result}

    # Agent 2: Execute test scenarios
    execution_result = await execution_agent(shared_state)

    # Update shared state
    shared_state.update(execution_result)

    # Display final execution summary
    print("\n===== QA EXECUTION SUMMARY =====")

    for result in shared_state["execution_results"]:

        print("\nTest Case:", result["scenario_id"])
        print("Scenario:", result["scenario"])
        print("Status:", result["actual_status"])
        print("Message:", result["actual_message"])

    print("\nWorkflow Status:", shared_state["status"])


if __name__ == "__main__":
    asyncio.run(main())

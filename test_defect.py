import asyncio

from agents.planner_agent import planner_agent
from agents.execution_agent import execution_agent
from agents.defect_agent import defect_analyzer_agent


async def main():

    # Initial user request
    initial_state = {"user_request": "Test SauceDemo login functionality"}

    # Agent 1: Test Planner
    planner_result = planner_agent(initial_state)

    shared_state = {**initial_state, **planner_result}

    # Agent 2: Execution Agent
    execution_result = await execution_agent(shared_state)

    shared_state.update(execution_result)

    # Agent 3: Defect Analyzer
    defect_result = defect_analyzer_agent(shared_state)

    shared_state.update(defect_result)

    # Final output
    print("\n===== COMPLETE QA ANALYSIS =====")

    print("\nTest Cases:", len(shared_state["test_plan"]))

    print("Execution Results:", len(shared_state["execution_results"]))

    print("Defect Count:", shared_state["bug_report"]["defect_count"])

    print("Workflow Status:", shared_state["status"])


if __name__ == "__main__":
    asyncio.run(main())

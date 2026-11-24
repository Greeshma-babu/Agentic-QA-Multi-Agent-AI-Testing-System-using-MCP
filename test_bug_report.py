import asyncio

from agents.planner_agent import planner_agent
from agents.execution_agent import execution_agent
from agents.defect_agent import defect_analyzer_agent
from agents.bug_reporter_agent import bug_reporter_agent


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

    # Agent 4: Bug Reporter
    reporter_result = bug_reporter_agent(shared_state)

    shared_state.update(reporter_result)

    # Final summary
    print("\n===== COMPLETE MULTI-AGENT QA SUMMARY =====")

    print("Test cases:", len(shared_state["test_plan"]))

    print("Executed tests:", len(shared_state["execution_results"]))

    print("Identified defects:", shared_state["bug_report"]["total_defects"])

    print("Status:", shared_state["status"])


if __name__ == "__main__":
    asyncio.run(main())

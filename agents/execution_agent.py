import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agents.state import QAAgentState

# --------------------------------------------------
# 1. VALIDATE TEST EXECUTION RESULTS
# --------------------------------------------------


def validate_test_result(scenario, actual_status, actual_message):

    scenario = scenario.strip().lower()
    message = actual_message.strip().lower()
    actual_status = actual_status.strip().upper()

    print("\n--- VALIDATION DEBUG ---")
    print("Scenario:", scenario)
    print("Application status:", actual_status)
    print("Application message:", message)

    if actual_status == "ERROR":
        return "ERROR"

    # IMPORTANT:
    # Check INVALID login before VALID login.
    # Otherwise, "invalid login" also matches "valid login".

    if "invalid login" in scenario:

        if actual_status == "FAIL" and "do not match" in message:
            return "PASS"

        return "FAIL"

    elif "empty login" in scenario:

        if actual_status == "FAIL" and "username is required" in message:
            return "PASS"

        return "FAIL"

    elif "valid login" in scenario:

        if actual_status == "PASS":
            return "PASS"

        return "FAIL"

    return "NOT_EVALUATED"


# --------------------------------------------------
# 2. EXECUTION AGENT
# --------------------------------------------------


async def execution_agent(state: QAAgentState) -> dict:

    print("\n===== EXECUTION AGENT =====")

    test_plan = state.get("test_plan", [])

    print(f"Received {len(test_plan)} test scenarios.")

    if not test_plan:
        return {"execution_results": [], "status": "EXECUTION_FAILED"}

    # MCP server file location

    project_root = Path(__file__).resolve().parent.parent

    server_path = project_root / "mcp_servers" / "playwright" / "playwright_server.py"

    if not server_path.exists():

        raise FileNotFoundError(f"Playwright MCP server not found: {server_path}")

    # Configure MCP server

    server_params = StdioServerParameters(
        command=sys.executable, args=[str(server_path)], env=None
    )

    execution_results = []

    # Connect to Playwright MCP server

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("\nConnected to Playwright MCP Server.")

            # Discover available MCP tools

            tools_response = await session.list_tools()

            available_tools = [tool.name for tool in tools_response.tools]

            print("Available MCP tools:", available_tools)

            tool_name = "test_saucedemo_login"

            if tool_name not in available_tools:

                raise RuntimeError(f"MCP tool not available: {tool_name}")

            # Execute every generated test case

            for test_case in test_plan:

                scenario_id = test_case.get("scenario_id", "UNKNOWN")

                scenario = test_case.get("scenario", "Unknown Scenario")

                expected_result = test_case.get("expected_result", "")

                username = test_case.get("username", "")
                password = test_case.get("password", "")

                print(f"\nExecuting: {scenario_id} - {scenario}")

                actual_status = "ERROR"
                actual_message = "Execution not completed"
                actual_url = ""

                try:

                    # Invoke Playwright MCP tool

                    response = await session.call_tool(
                        tool_name,
                        arguments={"username": username, "password": password},
                    )

                    # Extract MCP tool response

                    if response.structuredContent:

                        result = response.structuredContent

                    elif response.content:

                        result_text = response.content[0].text
                        result = json.loads(result_text)

                    else:

                        result = {
                            "status": "ERROR",
                            "message": "Empty MCP response",
                            "url": "",
                        }

                    actual_status = str(result.get("status", "ERROR")).upper()

                    actual_message = str(result.get("message", ""))

                    actual_url = str(result.get("url", ""))

                except Exception as error:

                    actual_status = "ERROR"
                    actual_message = str(error)

                    print("Execution error:", error)

                # Determine QA test verdict

                test_verdict = validate_test_result(
                    scenario, actual_status, actual_message
                )

                print("\nApplication response:", actual_status)
                print("QA test verdict:", test_verdict)

                # Store execution result

                execution_record = {
                    "scenario_id": scenario_id,
                    "scenario": scenario,
                    "expected_result": expected_result,
                    "actual_status": actual_status,
                    "actual_message": actual_message,
                    "actual_url": actual_url,
                    "test_verdict": test_verdict,
                }

                execution_results.append(execution_record)

    # --------------------------------------------------
    # 3. EXECUTION SUMMARY
    # --------------------------------------------------

    total_tests = len(execution_results)

    passed_tests = sum(
        1 for result in execution_results if result["test_verdict"] == "PASS"
    )

    failed_tests = sum(
        1 for result in execution_results if result["test_verdict"] == "FAIL"
    )

    error_tests = sum(
        1 for result in execution_results if result["test_verdict"] == "ERROR"
    )

    print("\n===== QA EXECUTION SUMMARY =====")

    print("Total tests:", total_tests)
    print("Passed:", passed_tests)
    print("Failed:", failed_tests)
    print("Errors:", error_tests)

    print("\n===== DETAILED TEST RESULTS =====")

    for result in execution_results:

        print("\nTest Case:", result["scenario_id"])
        print("Scenario:", result["scenario"])
        print("Application Status:", result["actual_status"])
        print("Application Message:", result["actual_message"])
        print("QA Test Verdict:", result["test_verdict"])

    return {"execution_results": execution_results, "status": "EXECUTION_COMPLETED"}

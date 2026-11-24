import json
import re

from langchain_ollama import ChatOllama
from agents.state import QAAgentState

# Initialize local Qwen model
llm = ChatOllama(model="qwen2.5:0.5b", temperature=0)


def planner_agent(state: QAAgentState) -> dict:

    user_request = state["user_request"]

    print("\n===== TEST PLANNER AGENT =====")
    print("Analyzing requirement:", user_request)

    prompt = f"""
You are an experienced Senior QA Test Planning Agent.

Application: SauceDemo login page.

User requirement:
{user_request}

Generate exactly 3 login test scenarios.

Use these scenarios:
1. Valid login: standard_user / secret_sauce
2. Invalid login: invalid_user / wrong_password
3. Empty login: empty username / empty password

Return ONLY a valid JSON array.

Required format:
[
  {{
    "scenario_id": "TC001",
    "scenario": "Valid Login",
    "username": "standard_user",
    "password": "secret_sauce",
    "expected_result": "User should navigate to inventory page"
  }},
  {{
    "scenario_id": "TC002",
    "scenario": "Invalid Login",
    "username": "invalid_user",
    "password": "wrong_password",
    "expected_result": "Error message should be displayed"
  }},
  {{
    "scenario_id": "TC003",
    "scenario": "Empty Login",
    "username": "",
    "password": "",
    "expected_result": "Validation error should be displayed"
  }}
]
"""

    response = llm.invoke(prompt)

    print("\nQwen generated test scenarios.")

    try:
        # Extract JSON array from response
        match = re.search(r"\[.*\]", response.content, re.DOTALL)

        if not match:
            raise ValueError("No JSON array found")

        test_plan = json.loads(match.group())

        # Validate generated scenarios
        required_fields = [
            "scenario_id",
            "scenario",
            "username",
            "password",
            "expected_result",
        ]

        if not isinstance(test_plan, list) or not test_plan:
            raise ValueError("Invalid test plan")

        for test_case in test_plan:
            if not all(field in test_case for field in required_fields):
                raise ValueError("Missing required test case fields")

        print("\nGenerated Test Cases:")

        for test_case in test_plan:
            print(test_case["scenario_id"], "-", test_case["scenario"])

    except (ValueError, json.JSONDecodeError, TypeError) as error:

        print("Qwen response could not be parsed:", error)
        print("Using predefined fallback scenarios.")

        test_plan = [
            {
                "scenario_id": "TC001",
                "scenario": "Valid Login",
                "username": "standard_user",
                "password": "secret_sauce",
                "expected_result": "User should navigate to inventory page",
            },
            {
                "scenario_id": "TC002",
                "scenario": "Invalid Login",
                "username": "invalid_user",
                "password": "wrong_password",
                "expected_result": "Error message should be displayed",
            },
            {
                "scenario_id": "TC003",
                "scenario": "Empty Login",
                "username": "",
                "password": "",
                "expected_result": "Validation error should be displayed",
            },
        ]

    # Return updated shared state
    return {"test_plan": test_plan, "status": "PLANNING_COMPLETED"}

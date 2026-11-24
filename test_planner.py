from agents.planner_agent import planner_agent

# Sample user request
initial_state = {"user_request": "Test SauceDemo login functionality"}

# Invoke Test Planner Agent
result = planner_agent(initial_state)

# Display generated test plan
print("\n===== FINAL TEST PLAN =====")

for test in result["test_plan"]:
    print("\nScenario ID:", test["scenario_id"])
    print("Scenario:", test["scenario"])
    print("Username:", test["username"])
    print("Expected:", test["expected_result"])

print("\nStatus:", result["status"])

import json

from langchain_ollama import ChatOllama
from agents.state import QAAgentState

# Initialize Qwen
llm = ChatOllama(model="qwen2.5:0.5b", temperature=0)


def defect_analyzer_agent(state: QAAgentState) -> dict:

    print("\n===== DEFECT ANALYZER AGENT =====")

    execution_results = state.get("execution_results", [])

    if not execution_results:
        raise ValueError("No execution results received")

    # Send execution results to Qwen
    prompt = f"""
You are an experienced Senior QA Defect Analysis Agent.

Analyze the following SauceDemo login test execution results.

Execution results:
{json.dumps(execution_results, indent=2)}

Rules:
1. PASS means login succeeded.
2. For invalid credentials, an error message is expected.
3. For empty credentials, a validation error is expected.
4. An expected error message is NOT an application defect.
5. An unexpected ERROR or missing application behavior should be investigated.
6. Do not invent defects without evidence.

Return ONLY valid JSON using this format:

{{
    "overall_analysis": "Summary of test execution",
    "defects": [
        {{
            "scenario_id": "TC001",
            "title": "Defect title",
            "severity": "High",
            "reason": "Evidence-based explanation",
            "recommendation": "Suggested investigation"
        }}
    ],
    "defect_count": 0
}}

If no defects are identified, return an empty defects array.
"""

    response = llm.invoke(prompt)

    print("\nQwen is analyzing execution results...")

    try:
        # Parse JSON response
        content = response.content.strip()

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("Invalid JSON response")

        analysis = json.loads(content[start : end + 1])

        if not isinstance(analysis.get("defects"), list):
            raise ValueError("Invalid defects list")

        # Validate that reported defects refer to executed tests
        executed_ids = {item["scenario_id"] for item in execution_results}

        for defect in analysis["defects"]:
            if defect.get("scenario_id") not in executed_ids:
                raise ValueError("Unknown scenario in defect report")

        print("\nDefect analysis completed.")

    except (ValueError, json.JSONDecodeError, TypeError) as error:

        print("Qwen analysis could not be parsed:", error)

        analysis = {
            "overall_analysis": (
                "AI analysis could not be parsed. " "Manual review is required."
            ),
            "defects": [],
            "defect_count": 0,
        }

    print("\n===== DEFECT ANALYSIS =====")
    print(analysis["overall_analysis"])

    print("\nIdentified Defects:", analysis["defect_count"])

    for defect in analysis["defects"]:
        print("\nScenario:", defect["scenario_id"])
        print("Title:", defect["title"])
        print("Severity:", defect["severity"])
        print("Reason:", defect["reason"])

    return {
        "defect_analysis": analysis["overall_analysis"],
        "bug_report": analysis,
        "status": "DEFECT_ANALYSIS_COMPLETED",
    }

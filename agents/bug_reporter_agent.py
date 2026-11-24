import json
import re
from pathlib import Path
from datetime import datetime

from langchain_ollama import ChatOllama
from agents.state import QAAgentState

llm = ChatOllama(model="qwen2.5:0.5b", temperature=0)


def bug_reporter_agent(state: QAAgentState) -> dict:

    print("\n===== BUG REPORTER AGENT =====")

    analysis = state.get("bug_report", {})
    defects = analysis.get("defects", [])
    execution_results = state.get("execution_results", [])

    reports = []

    for index, defect in enumerate(defects, start=1):

        scenario_id = defect.get("scenario_id")

        execution = next(
            (item for item in execution_results if item["scenario_id"] == scenario_id),
            None,
        )

        if execution is None:
            continue

        prompt = f"""
You are a Senior QA Bug Reporting Agent.

Create a professional software defect report.

Defect information:
{json.dumps(defect, indent=2)}

Execution evidence:
{json.dumps(execution, indent=2)}

Return only valid JSON using this format:

{{
    "title": "Clear defect title",
    "severity": "High",
    "priority": "High",
    "steps_to_reproduce": [
        "Step 1",
        "Step 2"
    ],
    "expected_result": "Expected behavior",
    "actual_result": "Observed behavior",
    "recommendation": "Suggested investigation"
}}

Use only the supplied evidence.
Do not invent steps, results or application behavior.
"""

        response = llm.invoke(prompt)

        try:
            match = re.search(r"\{.*\}", response.content, re.DOTALL)

            if not match:
                raise ValueError("No JSON found")

            report = json.loads(match.group())

            required_fields = [
                "title",
                "severity",
                "priority",
                "steps_to_reproduce",
                "expected_result",
                "actual_result",
                "recommendation",
            ]

            if not all(field in report for field in required_fields):
                raise ValueError("Missing report fields")

        except (ValueError, json.JSONDecodeError, TypeError):

            # Safe fallback using supplied defect evidence
            report = {
                "title": defect.get("title", "Suspected application defect"),
                "severity": defect.get("severity", "Unassigned"),
                "priority": "Requires QA review",
                "steps_to_reproduce": [
                    "Open SauceDemo",
                    "Execute the affected test scenario",
                    "Observe the reported behavior",
                ],
                "expected_result": execution["expected_result"],
                "actual_result": execution["actual_message"],
                "recommendation": defect.get(
                    "recommendation", "Investigate the reported behavior"
                ),
            }

        reports.append(
            {
                "defect_id": f"BUG-{index:03d}",
                "scenario_id": scenario_id,
                "title": report["title"],
                "severity": report["severity"],
                "priority": report["priority"],
                "steps_to_reproduce": report["steps_to_reproduce"],
                "expected_result": report["expected_result"],
                "actual_result": report["actual_result"],
                "recommendation": report["recommendation"],
            }
        )

    # Prepare final report
    final_report = {
        "application": "SauceDemo",
        "generated_at": datetime.now().isoformat(),
        "total_defects": len(reports),
        "defects": reports,
    }

    # Save JSON report
    project_path = Path(__file__).resolve().parent.parent

    reports_folder = project_path / "reports"
    reports_folder.mkdir(exist_ok=True)

    report_path = reports_folder / "bug_report.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(final_report, file, indent=4)

    print("\n===== BUG REPORT SUMMARY =====")
    print("Total defects:", len(reports))

    for report in reports:
        print("\nDefect ID:", report["defect_id"])
        print("Title:", report["title"])
        print("Severity:", report["severity"])

    print("\nReport saved at:", report_path)

    return {
        "bug_report": final_report,
        "final_report": json.dumps(final_report, indent=4),
        "status": "BUG_REPORT_COMPLETED",
    }

from typing import TypedDict, List, Dict, Any


class QAAgentState(TypedDict, total=False):

    # Original user request
    user_request: str

    # Test Planner Agent output
    test_plan: List[Dict[str, Any]]

    # Execution Agent output
    execution_results: List[Dict[str, Any]]

    # Defect Analyzer Agent output
    defect_analysis: str

    # Bug Reporter Agent output
    bug_report: Dict[str, Any]

    # Final report
    final_report: str

    # Workflow status
    status: str

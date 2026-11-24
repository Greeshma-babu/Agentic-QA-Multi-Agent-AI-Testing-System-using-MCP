# Agentic QA – Multi-Agent AI Testing System using MCP

An AI-powered test automation framework that uses multiple specialized AI agents, Model Context Protocol (MCP), Playwright, LangGraph, and a locally hosted LLM to automate software testing activities.

## 1. Project Overview

The Agentic QA system aims to automate the software testing lifecycle using a multi-agent architecture.

Instead of relying on a single AI agent, the framework divides testing responsibilities among specialized agents.

Each agent performs a specific task and shares information through a common state.

The system is designed to:

- Understand testing requirements.
- Generate test scenarios using an LLM.
- Execute browser automation through Playwright.
- Communicate with automation tools using MCP.
- Analyze test execution results.
- Identify genuine application defects.
- Generate structured bug reports.
- Orchestrate the workflow using LangGraph.

**Current demonstration:** Automated login testing of [SauceDemo](https://www.saucedemo.com/).

## 2. Architecture

```text
                    USER
                      |
                      v
              Testing Requirement
                      |
                      v
              SUPERVISOR AGENT
                  LangGraph
                      |
                      v
              TEST PLANNER AGENT
                  Qwen + Ollama
                      |
                      v
                TEST PLAN
                      |
                      v
              EXECUTION AGENT
                      |
                      v
                  MCP CLIENT
                      |
                      v
             PLAYWRIGHT MCP SERVER
                      |
                      v
                PLAYWRIGHT
                      |
                      v
              BROWSER AUTOMATION
                      |
                      v
              EXECUTION RESULTS
                      |
                      v
              DEFECT ANALYZER
                      |
                      v
              BUG REPORTER AGENT
                      |
                      v
                FINAL QA REPORT
```

**Architecture components:**

- LLM: Understands requirements and generates or analyzes information.
- Agents: Perform specialized testing activities.
- MCP: Provides standardized communication between the MCP client and external tools.
- Playwright: Executes browser automation.
- LangGraph: Orchestrates agent execution and manages workflow state.
- Shared State: Transfers structured information between agents.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10 | Primary programming language |
| Qwen 2.5 0.5B | Local Large Language Model |
| Ollama | Local LLM runtime |
| LangChain | LLM integration |
| LangGraph | Multi-agent orchestration |
| Model Context Protocol (MCP) | Tool communication |
| FastMCP | MCP server implementation |
| Playwright | Browser automation |
| Streamlit | Planned user interface |
| JSON | Structured test results and reports |

## 4. Multi-Agent Components

### 4.1 Test Planner Agent

File: `agents/planner_agent.py`

Responsibilities:

- Understand the user's testing requirement.
- Use Qwen to generate test scenarios.
- Generate structured test cases.
- Pass test scenarios to the Execution Agent.

Example generated test scenarios:

| Test ID | Scenario | Expected Behavior |
|---|---|---|
| TC001 | Valid Login | User should log in successfully |
| TC002 | Invalid Login | Application should reject invalid credentials |
| TC003 | Empty Login | Application should display a validation message |

### 4.2 Execution Agent

File: `agents/execution_agent.py`

Responsibilities:

- Read generated test scenarios from shared state.
- Connect to the Playwright MCP server.
- Discover available MCP tools.
- Invoke browser automation tools.
- Capture application responses.
- Compare actual behavior against expected behavior.
- Store execution results and QA test verdicts.

The Execution Agent distinguishes between application status and QA test verdict.

Example:

| Scenario | Application Status | QA Verdict |
|---|---|---|
| Valid Login | PASS | PASS |
| Invalid Login | FAIL | PASS |
| Empty Login | FAIL | PASS |

An application-level failure is not necessarily a QA failure. The test passes when the application behaves as expected.

### 4.3 Defect Analyzer Agent

File: `agents/defect_agent.py`

Responsibilities:

- Analyze execution results.
- Identify genuine test failures.
- Differentiate expected application behavior from actual defects.
- Generate structured defect analysis.

The intended classification is:

- PASS: No defect.
- FAIL: Analyze as a potential application defect.
- ERROR: Investigate execution or environment issues.

Deterministic test verdicts are used as the source of truth; the LLM assists with analysis and explanation.

### 4.4 Bug Reporter Agent

File: `agents/bug_reporter_agent.py`

Responsibilities:

- Consume defect analysis.
- Generate structured bug reports.
- Include defect details, severity, priority, expected results and actual results.
- Save the report in JSON format.

Output location:

`reports/bug_report.json`

### 4.5 Supervisor Agent

File: `agents/supervisor.py`

Responsibilities:

- Coordinate specialized agents using LangGraph.
- Define the execution sequence.
- Pass shared state between agents.
- Manage the workflow.

The initial workflow is sequential. Conditional routing, retries and human approval are planned enhancements.

## 5. MCP Integration

The project uses Model Context Protocol to connect AI-driven execution logic with browser automation tools.

### MCP Server

File: `mcp_servers/playwright/playwright_server.py`

The Playwright MCP server exposes the following tool:

`test_saucedemo_login(username, password)`

The tool:

1. Opens SauceDemo.
2. Enters login credentials.
3. Clicks the login button.
4. Validates the application response.
5. Returns structured execution results.

### MCP Client

The Execution Agent acts as the MCP client.

It:

1. Starts the MCP server using standard input/output transport.
2. Initializes an MCP session.
3. Discovers available tools.
4. Invokes the required tool.
5. Receives the execution response.

### MCP Communication Flow

```text
Execution Agent
      |
      v
MCP Client
      |
      | Tool Discovery
      v
MCP Server
      |
      | Tool Invocation
      v
Playwright Automation
      |
      v
Browser
      |
      v
Structured Response
```

MCP standardizes how the client communicates with tools. It does not itself perform browser automation or provide the agent's reasoning.

## 6. Shared State Management

File: `agents/state.py`

The project uses a shared state structure based on Python's `TypedDict`.

The state carries information between agents.

Important state fields:

| Field | Description |
|---|---|
| `user_request` | Original testing requirement |
| `test_plan` | Generated test scenarios |
| `execution_results` | Browser execution results |
| `defect_analysis` | Defect analysis |
| `bug_report` | Structured bug report |
| `final_report` | Final QA summary |
| `status` | Current workflow status |

This allows agents to access the output of previous agents without independently repeating the same work.

## 7. Project Structure

```text
Agentic_QA_MCP/
│
├── agents/
│   ├── __init__.py
│   ├── state.py
│   ├── planner_agent.py
│   ├── execution_agent.py
│   ├── defect_agent.py
│   ├── bug_reporter_agent.py
│   └── supervisor.py
│
├── mcp_servers/
│   └── playwright/
│       └── playwright_server.py
│
├── reports/
│   └── bug_report.json
│
├── test_llm.py
├── test_mcp_client.py
├── ai_mcp_agent.py
├── test_execution.py
├── test_defect.py
├── test_bug_report.py
├── test_multi_agent.py
│
├── requirements.txt
└── README.md
```

Note: The Supervisor and complete multi-agent entry point are part of the planned integration. The project structure may evolve as development progresses.

## 8. Installation and Setup

### Prerequisites

- Python 3.10
- VS Code
- Git
- Ollama
- Playwright-compatible browser installation

### Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Agentic_QA_MCP
```

### Step 2: Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

Install the packages used by the project:

```powershell
pip install langchain langchain-ollama langgraph
pip install mcp playwright
```

If your project uses FastMCP separately, install it if it is not already provided by your MCP package:

```powershell
pip install fastmcp
```

Install any additional dependencies required by the current source files.

### Step 4: Install Ollama

Download Ollama:

https://ollama.com/

Pull the Qwen model:

```powershell
ollama pull qwen2.5:0.5b
```

Verify the model:

```powershell
ollama list
```

### Step 5: Install Playwright browsers

```powershell
python -m playwright install chromium
```

## 9. Running the Project

Run the following scripts individually to validate the components during development.

### Test 1: Verify Qwen connection

```powershell
python test_llm.py
```

### Test 2: Verify MCP client-server connection

```powershell
python test_mcp_client.py
```

### Test 3: Test the single AI-driven MCP agent

```powershell
python ai_mcp_agent.py
```

### Test 4: Test Planner and Execution Agents

```powershell
python test_execution.py
```

### Test 5: Test Defect Analyzer

```powershell
python test_defect.py
```

### Test 6: Test Bug Reporter

```powershell
python test_bug_report.py
```

### Complete multi-agent workflow

Once Supervisor integration is completed and verified:

```powershell
python test_multi_agent.py
```

## 10. Expected Execution Results

For the SauceDemo login demonstration:

| Test Case | Input | Expected Result | QA Verdict |
|---|---|---|---|
| TC001 | Valid credentials | Login successful | PASS |
| TC002 | Invalid credentials | Login rejected | PASS |
| TC003 | Empty credentials | Validation message | PASS |

Expected execution summary:

```text
===== QA EXECUTION SUMMARY =====

Total tests: 3
Passed: 3
Failed: 0
Errors: 0

Workflow Status: EXECUTION_COMPLETED
```

These results represent the verified Planner and Execution Agent demonstration. Full end-to-end Supervisor integration requires separate verification.

## 11. Design Principles

### Separation of Responsibilities

Each agent has one defined responsibility, improving maintainability and debugging.

### Tool-Based Automation

Browser automation is exposed through MCP tools instead of tightly coupling every agent to Playwright implementation details.

### Shared State

Structured state allows agents to exchange information consistently.

### Deterministic Test Validation

Application responses are compared against expected behavior to prevent false-positive defect reporting.

### Local LLM Execution

Ollama enables local model execution without requiring a hosted LLM API for the current demonstration.

## 12. Current Development Status

| Component | Status |
|---|---|
| Ollama and Qwen connection | Completed |
| Playwright MCP server | Completed |
| MCP client connection | Completed |
| Single AI-driven MCP agent | Tested |
| Shared QA state | Completed |
| Test Planner Agent | Tested |
| Execution Agent | Tested |
| Test result validation | Tested |
| Defect Analyzer | Requires integration improvement |
| Bug Reporter | Initial implementation available |
| LangGraph Supervisor | Integration pending verification |
| Complete multi-agent workflow | Pending verification |
| Streamlit dashboard | Planned |

## 13. Future Enhancements

- Dynamic test case generation from user stories and acceptance criteria.
- AI-generated Playwright automation scripts.
- Screenshot-based visual defect analysis.
- Intelligent failure classification.
- Automatic retry for flaky tests.
- Conditional agent routing using LangGraph.
- Human approval before defect creation.
- GitHub issue integration.
- JIRA defect management integration.
- Streamlit dashboard for test execution monitoring.
- Support for multiple web applications and test suites.
- RAG-based retrieval of historical defects and test cases.

## 14. Learning Outcomes

This project demonstrates practical implementation of:

- Agentic AI concepts.
- Multi-agent architecture.
- Model Context Protocol.
- MCP client-server integration.
- LLM integration using LangChain and Ollama.
- LangGraph orchestration.
- Playwright browser automation.
- AI-assisted test planning.
- Deterministic test result validation.
- Automated defect analysis and reporting.

## 15. Project Objective

The long-term objective is to build an intelligent QA automation platform where AI agents collaborate to understand requirements, plan tests, execute automation, analyze failures and generate actionable defect reports.

The framework combines traditional automation engineering with modern Agentic AI and MCP-based tool integration.

---

**Project:** Agentic QA – Multi-Agent AI Testing System using MCP

**Primary Technologies:** Python, Playwright, MCP, LangGraph, LangChain, Ollama and Qwen.

**Application Under Test:** SauceDemo.
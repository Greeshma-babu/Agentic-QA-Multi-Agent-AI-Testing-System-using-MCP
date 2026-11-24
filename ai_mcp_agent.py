import asyncio
import json
import re
import sys
from pathlib import Path

from langchain_ollama import ChatOllama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to local Qwen model
llm = ChatOllama(model="qwen2.5:0.5b", temperature=0)


async def main():

    # Get the user's testing request
    user_request = input("\nEnter your QA testing request: ")

    # Locate MCP server
    project_path = Path(__file__).parent

    server_path = project_path / "mcp_servers" / "playwright" / "playwright_server.py"

    server_params = StdioServerParameters(
        command=sys.executable, args=[str(server_path)]
    )

    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("\nConnected to MCP Server.")

            # Discover available tools
            tool_response = await session.list_tools()

            available_tools = tool_response.tools

            print("\nAvailable MCP Tools:")

            for tool in available_tools:
                print("-", tool.name)

            # Prepare tool descriptions for Qwen
            tool_details = []

            for tool in available_tools:
                tool_details.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                )

            # Ask Qwen to select a tool
            prompt = f"""
You are an AI QA testing agent.

User testing request:
{user_request}

Available MCP tools:
{json.dumps(tool_details, indent=2)}

Available SauceDemo test credentials:
Username: standard_user
Password: secret_sauce

Instructions:
1. Select the most suitable available MCP tool.
2. Use only the tool names provided.
3. For a valid SauceDemo login test, use the credentials above.
4. Return only valid JSON.
5. Do not include Markdown or explanations.

Required JSON format:
{{
    "tool_name": "test_saucedemo_login",
    "arguments": {{
        "username": "standard_user",
        "password": "secret_sauce"
    }}
}}
"""

            print("\nQwen is analyzing your request...")

            response = llm.invoke(prompt)

            ai_response = response.content

            print("\nQWEN TOOL SELECTION:")
            print(ai_response)

            # Extract JSON from AI response
            try:
                match = re.search(r"\{.*\}", ai_response, re.DOTALL)

                if not match:
                    raise ValueError("No JSON found in Qwen response")

                decision = json.loads(match.group())

                selected_tool = decision["tool_name"]
                arguments = decision["arguments"]

            except Exception as e:
                print("\nCould not understand Qwen's tool selection.")
                print("Details:", str(e))
                return

            # Validate selected tool
            available_names = [tool.name for tool in available_tools]

            if selected_tool not in available_names:
                print("\nSelected tool is not available.")
                return

            print("\nAI selected MCP tool:", selected_tool)
            print("Arguments:", arguments)

            # Invoke selected MCP tool
            print("\nExecuting browser test...")

            result = await session.call_tool(selected_tool, arguments=arguments)

            print("\n===== FINAL QA RESULT =====")

            if result.structuredContent:
                print(json.dumps(result.structuredContent, indent=2))
            else:
                for item in result.content:
                    if hasattr(item, "text"):
                        print(item.text)

            if result.isError:
                print("\nMCP tool execution reported an error.")


if __name__ == "__main__":
    asyncio.run(main())

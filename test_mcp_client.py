import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    # Locate the Playwright MCP server
    project_path = Path(__file__).parent

    server_path = project_path / "mcp_servers" / "playwright" / "playwright_server.py"

    # Configure MCP server connection
    server_params = StdioServerParameters(
        command=sys.executable, args=[str(server_path)]
    )

    print("Connecting to Playwright MCP Server...")

    # Start server and establish MCP communication
    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize MCP connection
            await session.initialize()

            print("\nMCP connection successful!")

            # Discover available tools
            tools = await session.list_tools()

            print("\nAvailable MCP Tools:")

            for tool in tools.tools:
                print(f"\nTool Name: {tool.name}")
                print(f"Description: {tool.description}")

            # Invoke the login testing tool
            print("\nExecuting SauceDemo login test...")

            result = await session.call_tool(
                "test_saucedemo_login",
                arguments={"username": "standard_user", "password": "secret_sauce"},
            )

            print("\n===== TEST EXECUTION RESULT =====")

            for item in result.content:
                if hasattr(item, "text"):
                    print(item.text)

            if result.isError:
                print("\nMCP tool execution reported an error.")


if __name__ == "__main__":
    asyncio.run(main())

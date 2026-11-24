from mcp.server.fastmcp import FastMCP
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

mcp = FastMCP("Playwright-QA-Server")


@mcp.tool()
async def test_saucedemo_login(username: str, password: str) -> dict:

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("https://www.saucedemo.com/", wait_until="domcontentloaded")

            await page.locator("#user-name").fill(username)
            await page.locator("#password").fill(password)
            await page.locator("#login-button").click()

            # Wait for either successful login or an error message
            try:
                await page.locator(
                    ".inventory_list, [data-test='error']"
                ).first.wait_for(state="visible", timeout=10000)
            except PlaywrightTimeoutError:
                return {
                    "status": "ERROR",
                    "message": "Neither inventory page nor login error appeared",
                    "url": page.url,
                }

            # Validate successful login
            if await page.locator(".inventory_list").count() > 0:

                return {
                    "status": "PASS",
                    "message": "Login successful",
                    "url": page.url,
                }

            # Capture login error
            error_message = await page.locator("[data-test='error']").inner_text()

            return {"status": "FAIL", "message": error_message, "url": page.url}

        except Exception as e:

            return {"status": "ERROR", "message": str(e), "url": page.url}

        finally:
            await browser.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")

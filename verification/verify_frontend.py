from playwright.sync_api import sync_playwright
import os

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the local HTML file
        file_path = os.path.abspath("verification/mock_session.html")
        page.goto(f"file://{file_path}")

        # Verify elements are visible
        page.locator("#regra_processing").wait_for()

        # Take screenshot
        page.screenshot(path="verification/verification.png", full_page=True)

        browser.close()

if __name__ == "__main__":
    verify_frontend()
from playwright.sync_api import sync_playwright
import random
import time
import json

def visit_website():
    base_url = "https://literature-explorer.streamlit.app"

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()

        # Track network requests
        network_requests = []
        def log_request(request):
            network_requests.append({
                "url": request.url,
                "resource_type": request.resource_type,
                "status": None
            })
        def log_response(response):
            for req in network_requests:
                if req["url"] == response.url:
                    req["status"] = response.status
        page.on("request", log_request)
        page.on("response", log_response)

        try:
            # Step 1: Visit base URL
            print("Visiting base URL to wake the app...")
            response = page.goto(base_url, timeout=60000)
            print(f"Base URL status: {response.status}")
            if response.status in [301, 302]:
                print(f"Redirect detected: {response.headers.get('location', 'unknown')}")
                return

            # Log page metadata
            print(f"Page title: {page.title()}")
            print(f"Current URL: {page.url}")

            # Wait for full page load
            page.wait_for_load_state("networkidle", timeout=60000)

            # Periodically check WebSocket connection over 30 seconds
            print("\nChecking WebSocket connection periodically...")
            websocket_found = False
            for i in range(6):  # Check every 5 seconds for 30 seconds
                try:
                    page.wait_for_function(
                        "!!Array.from(window.performance.getEntriesByType('resource')).find(e => e.name.includes('_stcore/stream'))",
                        timeout=5000
                    )
                    print(f"Streamlit WebSocket connection detected at {i*5} seconds")
                    websocket_found = True
                    break
                except:
                    print(f"No WebSocket at {i*5} seconds, continuing...")
                time.sleep(5)
            if not websocket_found:
                print("WebSocket connection (_stcore/stream) not detected after 30 seconds")

            # Check for Streamlit UI elements
            streamlit_elements = [
                {"selector": "div.stApp", "description": "Streamlit main container"},
                {"selector": "div#MainMenu", "description": "Streamlit main menu"},
                {"selector": "div.stButton", "description": "Streamlit button"},
                {"selector": "div.stTextInput", "description": "Streamlit text input"}
            ]
            print("\nChecking for Streamlit UI elements:")
            for elem in streamlit_elements:
                try:
                    page.wait_for_selector(elem["selector"], timeout=10000)
                    print(f"Found {elem['description']} ({elem['selector']})")
                except:
                    print(f"Not found: {elem['description']} ({elem['selector']})")

            # Log JavaScript errors
            print("\nChecking for JavaScript errors...")
            page.on("console", lambda msg: print(f"JS Console: {msg.type} - {msg.text}") if msg.type == "error" else None)

            # Log cookies
            cookies = context.cookies()
            print("\nCookies observed:")
            print(json.dumps(cookies, indent=2) if cookies else "No cookies")

            # Log network requests
            print("\nNetwork requests observed:")
            for req in network_requests:
                print(f"URL: {req['url']}, Type: {req['resource_type']}, Status: {req['status']}")

            # Simulate human-like behavior
            print("\nSimulating human-like interaction...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(5, 10))
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(random.uniform(2, 5))

            # Test Flask endpoint
            print("\nTesting Flask endpoint...")
            test_response = page.goto(f"{base_url}/", timeout=30000)
            test_content = page.content()
            try:
                test_json = json.loads(test_content)
                print("Flask endpoint response:", json.dumps(test_json, indent=2))
            except json.JSONDecodeError:
                print("Flask endpoint returned HTML, not JSON (expected for UI)")

            # Wait longer to ensure Flask backend (load_data) completes
            print("\nWaiting to ensure app initialization...")
            time.sleep(45)  # Increased to 45 seconds for slow rendering

            # Log page content snippet
            content = page.content()
            print("\nPage content snippet (first 500 characters):")
            print(content[:500])
            try:
                json_content = json.loads(content)
                print("Page content is JSON:", json.dumps(json_content, indent=2))
            except json.JSONDecodeError:
                print("Page content is HTML, not JSON")

            print("\nSuccessfully completed base URL visit")

        except Exception as e:
            print(f"Error during website visit: {e}")

        finally:
            browser.close()

if __name__ == "__main__":
    visit_website()

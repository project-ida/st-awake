from playwright.sync_api import sync_playwright
import random
import time

def visit_website():
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Navigate to the website
            page.goto("https://literature-explorer.streamlit.app", timeout=60000)
            
            # Wait for page to load
            page.wait_for_load_state("load")
            
            # Simulate human-like behavior
            # Scroll down the page
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(2, 5))  # Random wait to mimic human reading
            
            # Scroll back up
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(random.uniform(1, 3))
            
            print("Successfully visited the website")
        
        except Exception as e:
            print(f"Error during website visit: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    visit_website()

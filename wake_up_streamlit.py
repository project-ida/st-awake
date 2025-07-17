from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from streamlit_app import STREAMLIT_APPS
import datetime
import time

# Set up Selenium webdriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Initialize log file
with open("wakeup_log.txt", "a") as log_file:
    log_file.write(f"Execution started at: {datetime.datetime.now()}\n")

    # Iterate through each URL in the list
    for url in STREAMLIT_APPS:
        try:
            # Navigate to the webpage
            driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Check if the wake up button exists
            try:
                button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='wakeup-button-viewer']"))
                )
                driver.execute_script("arguments[0].click();", button)
            
                # Wait for the button to disappear (app booting up)
                WebDriverWait(driver, 15).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "button[data-testid='wakeup-button-viewer']"))
                )
                
                # Give the app time to fully start up before browser closes
                time.sleep(10)
            
                log_file.write(f"[{datetime.datetime.now()}] App is likely starting OK at: {url}\n")
            except TimeoutException:
                log_file.write(f"[{datetime.datetime.now()}] Button not found or did not disappear after click at: {url}\n")

        
        except Exception as e:
            log_file.write(f"[{datetime.datetime.now()}] Error for app at {url}: {str(e)}\n")

# Close the browser
driver.quit()

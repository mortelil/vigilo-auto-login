from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

full_name = "" # Lastname Firstname, has to match whats on the website 
username = ""
password = ""
school_name = ""
chromium_datadir = "" # If you're on ubuntu and have installed using snap its probably /home/username/snap/chromium/common/chromium

options = webdriver.ChromeOptions()
# User data and profile
options.add_argument(f"--user-data-dir={chromium_datadir}")
options.add_argument("--profile-directory=Default")  
options.add_argument('--start-maximized')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Performance optimizations
options.page_load_strategy = 'eager'  # Don't wait for all resources
options.add_argument("--disable-extensions")  # Disable extensions

# Remove automation infobar
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# Keep browser open
options.add_experimental_option("detach", True)

# Use the correct chromedriver path
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

# Disable images using CDP
driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.svg", "*.webp"]})
driver.execute_cdp_cmd('Network.enable', {})

# Set an implicit wait time for finding elements
driver.implicitly_wait(5)

try:
    # Step 1: Open initial page
    driver.get("https://web-school.prod.vigilo-oas.no/")
    # Step 2: Wait for redirect to auth login with signin param
    WebDriverWait(driver, 10).until(
        EC.url_contains("https://auth.prod.vigilo-oas.no/login?signin=")
    )
    # Step 3: Click "Dataporten / Feide"
    dataporten_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//span[contains(text(), 'Dataporten / Feide')]/ancestor::a"
        ))
    )
    dataporten_button.click()
    # Step 4: Wait for account chooser page
    WebDriverWait(driver, 8).until(
        EC.url_contains("https://auth.dataporten.no/accountchooser")
    )
    # Step 5: Click on name
    name_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//a[.//h3[text()='{full_name}']]"
        ))
    )
    name_button.click()
    # Wait for the username field and enter username
    username_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_input.send_keys(f"{username}")
    # Wait for the password field and enter your password
    password_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_input.send_keys(f"{password}")
    # Click the "Log in" button (it has type='submit')
    login_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Log in')]"))
    )
    login_button.click()
    # Wait for the link containing the <h3> with desired text, then click it
    twofactor_link = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//h3[contains(text(), 'Use work or school account')]/ancestor::a"))
    )
    twofactor_link.click()
    # Wait for the link containing the school name and click it
    school_link = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{school_name}')]"))
    )
    school_link.click()
    
    # Re-enable images after login is complete
    driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": []})
    
    # Re-enable images by refreshing the page after the login process
    current_url = driver.current_url
    driver.refresh()
    
    # Browser will now stay open because of the detach option
except Exception as e:
    print("Something went wrong:", e)
    # Keep the browser open even if there's an error

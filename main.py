import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from webdriver_manager.chrome import ChromeDriverManager

LOD_EMAIL    = os.environ["LOD_EMAIL"]
LOD_PASSWORD = os.environ["LOD_PASSWORD"]
FOLDER_ID    = os.environ["FOLDER_ID"]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    # użyj webdriver_manager, żeby nie martwić się wersjami
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def login(driver):
    driver.get("https://app.lodgify.com/login")
    wait = WebDriverWait(driver, 15)
    email = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
    email.clear(); email.send_keys(LOD_EMAIL)
    pwd   = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
    pwd.clear();   pwd.send_keys(LOD_PASSWORD)
    driver.find_element(By.XPATH, "//button[normalize-space()='Log in' or normalize-space()='Zaloguj się']").click()
    wait.until(EC.url_contains("/dashboard"))
    print("✅ Zalogowano pomyślnie")

# ... dalej reszta twoich funkcji: download_csv(), merge_report(), upload_to_drive() ...

if __name__ == "__main__":
    print("🚀 Start bota Lodgify")
    driver = setup_driver()
    try:
        login(driver)
        # tutaj dalej: pobierz CSV, zrób PDF/tabelkę, wrzuć na Drive
    finally:
        driver.quit()

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIG ===
LOD_EMAIL = os.environ['LOD_EMAIL']
LOD_PASSWORD = os.environ['LOD_PASSWORD']
FOLDER_ID = os.environ['FOLDER_ID']
DOWNLOAD_PATH = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# === Selenium ===
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument(f'--window-size=1200,800')
    chrome_options.add_argument(f'--user-agent=Mozilla/5.0')
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": DOWNLOAD_PATH,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    })
    return webdriver.Chrome(options=chrome_options)

def login(driver):
    driver.get("https://app.lodgify.com/sign-in")
    wait = WebDriverWait(driver, 15)
    form = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form.email-login")))
    inputs = form.find_elements(By.CSS_SELECTOR, "input")
    email_input, password_input = inputs[0], inputs[1]
    email_input.send_keys(LOD_EMAIL)
    password_input.send_keys(LOD_PASSWORD)
    btn = form.find_element(By.CSS_SELECTOR, "button[type=submit], button")
    btn.click()
    # poczekaj aż dashboard się załaduje
    wait.until(EC.url_contains("/dashboard"))

def download_all_csvs(driver):
    tabs = ["Next arrivals", "Next departures", "Currently staying"]
    for tab in tabs:
        # klikamy odpowiedni tab
        driver.find_element(By.XPATH, f"//div[contains(text(), '{tab}')]").click()
        time.sleep(3)
        # klikamy button "Download …"
        btn = driver.find_element(By.XPATH,
            "//button[contains(., 'Download')]"
        )
        btn.click()
        # poczekaj na ściągnięcie pliku
        time.sleep(5)

# === Google Drive upload ===
def drive_service():
    creds = service_account.Credentials.from_service_account_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

def upload_files(service):
    for fn in os.listdir(DOWNLOAD_PATH):
        full = os.path.join(DOWNLOAD_PATH, fn)
        if fn.lower().endswith('.csv'):
            meta = {'name': fn, 'parents': [FOLDER_ID]}
            media = MediaFileUpload(full, mimetype='text/csv')
            service.files().create(body=meta, media_body=media).execute()
            print("✓ uploaded", fn)

def clear_downloads():
    for f in os.listdir(DOWNLOAD_PATH):
        os.remove(os.path.join(DOWNLOAD_PATH, f))

# === Main ===
if __name__ == "__main__":
    driver = setup_driver()
    try:
        clear_downloads()
        login(driver)
        download_all_csvs(driver)
    finally:
        driver.quit()

    svc = drive_service()
    upload_files(svc)
    print("✅ done")

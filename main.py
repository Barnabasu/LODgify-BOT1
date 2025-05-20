import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load env vars
load_dotenv()
LOD_EMAIL    = os.getenv("LOD_EMAIL")
LOD_PASSWORD = os.getenv("LOD_PASSWORD")
FOLDER_ID    = os.getenv("FOLDER_ID")
DOWNLOAD_DIR = "/tmp"

FILES = {
    "Next arrivals":     "next_arrivals.csv",
    "Next departures":   "next_departures.csv",
    "Currently staying": "currently_staying.csv"
}

def setup_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    svc = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=svc, options=opts)

def login(driver):
    driver.get("https://app.lodgify.com/login")
    time.sleep(5)
    driver.find_element(By.NAME, "email").send_keys(LOD_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(LOD_PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(., 'Log in')]").click()
    time.sleep(7)

def download_csvs(driver):
    for tab, fname in FILES.items():
        print(f"📥 Pobieram zakładkę: {tab}")
        driver.get("https://app.lodgify.com/dashboard")
        time.sleep(5)
        driver.find_element(By.XPATH, f'//div[contains(text(), "{tab}")]').click()
        time.sleep(5)
        driver.find_element(By.XPATH, '//button[contains(text(), "Download")]').click()
        time.sleep(8)

def setup_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        "client_secret.json",
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    return build("drive", "v3", credentials=creds)

def upload_to_drive(service):
    existing = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute().get("files", [])
    for f in existing:
        service.files().delete(fileId=f["id"]).execute()
        print(f"🗑 Usunięto: {f['name']}")

    for fname in FILES.values():
        path = os.path.join(DOWNLOAD_DIR, fname)
        if os.path.exists(path):
            print(f"☁️ Wysyłam na Drive: {fname}")
            media = MediaFileUpload(path, mimetype="text/csv")
            service.files().create(
                body={"name": fname, "parents":[FOLDER_ID]},
                media_body=media
            ).execute()
        else:
            print(f"⚠️ Nie znaleziono pliku: {fname}")

if __name__ == "__main__":
    print("🚀 Start bota Lodgify")
    driver = setup_driver()
    login(driver)
    download_csvs(driver)
    driver.quit()
    drive_service = setup_drive_service()
    upload_to_drive(drive_service)
    print("✅ Zakończono pomyślnie")
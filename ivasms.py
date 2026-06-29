"""
Minimal iVasms client helpers: session creation, login, cookie management, fetch SMS.
This is a simplified and safer rewrite of the logic found in the original script.
Credentials and tokens are read from environment variables.
"""
import os
import requests
from bs4 import BeautifulSoup
import json
import threading

IVASMS_BASE = os.getenv("IVASMS_BASE_URL", "https://www.ivasms.com")
IVASMS_USERNAME = os.getenv("IVASMS_USERNAME")
IVASMS_PASSWORD = os.getenv("IVASMS_PASSWORD")
COOKIES_FILE = os.getenv("COOKIES_FILE", "mafia_ck_4235.json")

class IvasmsClient:
    def __init__(self):
        self.session = requests.Session()
        self.is_logged_in = False
        self.lock = threading.Lock()

    def save_cookies(self):
        jar = self.session.cookies
        cookies = []
        for c in jar:
            cookies.append({"name": c.name, "value": c.value, "domain": c.domain})
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)

    def load_cookies(self):
        if not os.path.exists(COOKIES_FILE):
            return False
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.apply_cookies(data)
        return True

    def apply_cookies(self, cookies_list):
        self.session.cookies.clear()
        for c in cookies_list:
            domain = c.get('domain', 'www.ivasms.com').lstrip('.')
            self.session.cookies.set(c['name'], c['value'], domain=domain, path='/')
        self.is_logged_in = False
        # kick off background login check
        threading.Thread(target=self.login_if_needed, daemon=True).start()

    def login_if_needed(self):
        # simple login flow: GET login page to fetch tokens, then POST credentials
        with self.lock:
            try:
                r = self.session.get(f"{IVASMS_BASE}/login", timeout=15)
                if r.status_code != 200:
                    return False
                # parse CSRF if present
                soup = BeautifulSoup(r.text, 'html.parser')
                # placeholder: find csrf token if the page has one
                # token = soup.find('input', {'name': 'csrf'})['value'] if ...
                payload = {"email": IVASMS_USERNAME, "password": IVASMS_PASSWORD}
                post = self.session.post(f"{IVASMS_BASE}/login", data=payload, timeout=15)
                if post.status_code == 200 and "dashboard" in post.url:
                    self.is_logged_in = True
                    self.save_cookies()
                    return True
            except Exception:
                return False
        return False

    def fetch_received_sms(self):
        if not self.is_logged_in:
            self.login_if_needed()
            if not self.is_logged_in:
                return []
        try:
            r = self.session.get(f"{IVASMS_BASE}/portal/sms/received/getsms", timeout=15)
            if r.status_code == 200:
                return r.json() if r.headers.get('Content-Type','').startswith('application/json') else []
        except Exception:
            return []
        return []

# singleton
client = IvasmsClient()

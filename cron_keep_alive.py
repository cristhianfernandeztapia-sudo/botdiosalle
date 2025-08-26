
import os
import time
import requests
from datetime import datetime

APP_URL = os.getenv("APP_URL")  # ej: https://botdiosalle.onrender.com/
TIMEOUT = 15

def ping():
    if not APP_URL:
        print("❌ Falta APP_URL (ej: https://TU_APP.onrender.com/)")
        return
    url = APP_URL.rstrip("/") + "/"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        print(f"✅ {datetime.utcnow().isoformat()}Z  {r.status_code} {url}")
    except Exception as e:
        print(f"⚠️ {datetime.utcnow().isoformat()}Z  Error ping: {e}")

def main():
    print("💓 Keep-alive iniciado. Pingeando la app para que no entre en sleep.")
    ping()
    print("🎉 Listo.")

if __name__ == "__main__":
    main()


import requests
import time
import sys

BASE_URL = "http://app:5000"  # שם ה-service בדוקר
URL = f"{BASE_URL}/add"

data = {
    "title": "Buy groceries"
}



def wait_for_app(url, timeout=60, interval=2):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False

if __name__ == "__main__":
    # Espera o app estar pronto
    if not wait_for_app(BASE_URL, timeout=60, interval=2):
        print("TEST FAILED: app service not available after waiting")
        sys.exit(1)
    try:
        response = requests.post(URL, json=data)
        if response.status_code == 200:
            print("TEST PASSED:", response.json())
            sys.exit(0)
        else:
            print("TEST FAILED: bad status code", response.status_code)
            sys.exit(1)
    except Exception as e:
        print("TEST FAILED:", str(e))
        sys.exit(1)
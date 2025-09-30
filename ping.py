import requests
import time
import os

def ping_server():
    """Отправляет ping на ваш сервер"""
    url = os.environ.get('RENDER_URL', 'https://your-bot-service.onrender.com')
    try:
        response = requests.get(url)
        print(f"✅ Ping sent to {url} - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Ping failed: {e}")

if __name__ == "__main__":
    print("Starting ping service...")
    while True:
        ping_server()
        time.sleep(600)  # 10 минут

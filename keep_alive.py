from flask import Flask
from threading import Thread
import requests
import time

app = Flask('')

@app.route('/')
def home():
    return "🤖 KF Black Russia Bot is ALIVE!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Функция самопинга
def start_pinging():
    def ping():
        while True:
            try:
                # ЗАМЕНИ на свой URL Render
                requests.get('https://your-bot-name.onrender.com')
                print("✅ Пинг отправлен в", time.strftime("%H:%M:%S"))
            except Exception as e:
                print(f"❌ Ошибка: {e}")
            time.sleep(240)  # 4 минуты (меньше 5!)
    
    thread = Thread(target=ping)
    thread.daemon = True
    thread.start()

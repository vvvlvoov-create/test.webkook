from flask import Flask
from threading import Thread
import requests
import time
import os

app = Flask('')

@app.route('/')
def home():
    return "🤖 KF Black Russia Bot - ОСНОВНОЙ"

def run():
    app.run(host='0.0.0.0', port=8080)

# ✅ ДОЛЖНЫ БЫТЬ ИМЕННО ТАКИЕ ФУНКЦИИ:
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

def start_pinging():
    def ping():
        while True:
            try:
                # Пингуем СЕБЯ (основной бот)
                main_bot_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://your-main-bot.onrender.com')
                requests.get(main_bot_url)
                print(f"✅ Основной бот пингован: {time.strftime('%H:%M:%S')}")
                
            except Exception as e:
                print(f"❌ Ошибка пинга: {e}")
            
            time.sleep(240)  # 4 минуты
    
    thread = Thread(target=ping)
    thread.daemon = True
    thread.start()

from flask import Flask
import threading
import subprocess
import requests
import time
import os

app = Flask(__name__)

def run_bot():
    """Запускает бота"""
    print("🤖 Starting Telegram bot...")
    subprocess.run(["python", "bot.py"])

def ping_self():
    """Пингует сам себя каждые 10 минут"""
    def ping_loop():
        while True:
            try:
                # Пробуем разные способы получить URL
                url = os.environ.get('RENDER_EXTERNAL_URL')
                if not url:
                    service_name = os.environ.get('RENDER_SERVICE_NAME')
                    if service_name:
                        url = f"https://{service_name}.onrender.com"
                
                if url:
                    requests.get(url)
                    print(f"✅ Ping sent to: {url}")
                else:
                    print("⚠️  URL not found, skipping ping")
                    
            except Exception as e:
                print(f"❌ Ping failed: {e}")
            time.sleep(600)  # 10 минут
    
    ping_thread = threading.Thread(target=ping_loop)
    ping_thread.daemon = True
    ping_thread.start()

@app.route('/')
def home():
    return "🤖 Bot is running!"

@app.route('/ping')
def ping():
    return "🏓 Pong!"

if __name__ == '__main__':
    # Показываем какой URL используется
    url = os.environ.get('RENDER_EXTERNAL_URL') or f"https://{os.environ.get('RENDER_SERVICE_NAME', 'unknown')}.onrender.com"
    print(f"🔗 Using URL: {url}")
    
    # Запускаем self-ping
    ping_self()
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)

from flask import Flask
import os
import subprocess
import threading

app = Flask(__name__)

def run_bot():
    """Запускает бота в отдельном процессе"""
    subprocess.run(["python", "bot.py"])

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем веб-сервер
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

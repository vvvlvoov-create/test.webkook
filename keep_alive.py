import requests
import time

def ping_main_bot():
    while True:
        try:
            # Пингуем ОСНОВНОЙ бот
            requests.get('https://your-main-bot.onrender.com')
            print("🔄 Пинг основного бота")
            
            # Пингуем СЕБЯ тоже
            requests.get('https://your-ping-service.onrender.com')
            print("🔁 Самопинг")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        time.sleep(240)  # 4 минуты

if __name__ == "__main__":
    ping_main_bot() 

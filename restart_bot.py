import subprocess
import time
import sys
import os
from datetime import datetime

def run_bot():
    """Запускает бота на 4.5 минут"""
    start_time = datetime.now()
    print(f"🔄 [{start_time.strftime('%H:%M:%S')}] Запускаю бота...")
    
    try:
        process = subprocess.Popen([sys.executable, "bot.py"])
        
        # Ждем 4.5 минут (270 секунд)
        for i in range(270):
            time.sleep(1)
            # Проверяем что процесс еще жив
            if process.poll() is not None:
                print("⚠️ Бот завершился раньше времени, перезапускаю...")
                break
        
        # Останавливаем бота
        end_time = datetime.now()
        runtime = (end_time - start_time).seconds
        print(f"🔄 [{end_time.strftime('%H:%M:%S')}] Останавливаю бота (работал {runtime} сек)...")
        
        process.terminate()
        try:
            process.wait(timeout=10)  # Ждем завершения 10 секунд
        except subprocess.TimeoutExpired:
            process.kill()  # Принудительно завершаем если не останавливается
            
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
    
    # Ждем 30 секунд перед перезапуском
    print("⏳ Жду 30 секунд перед перезапуском...")
    time.sleep(30)

if __name__ == "__main__":
    print("🚀 Запускаю бесконечный цикл перезапуска бота (каждые 5 минут)")
    print("📝 Бот будет работать 4.5 минуты, затем перезапускаться")
    
    while True:
        run_bot()

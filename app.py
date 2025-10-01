import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Конфигурация
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID', '@kfblackrussia')

# Глобальные переменные
application = None

@app.route('/')
def home():
    return "🤖 KF Black Russia Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик webhook от Telegram"""
    if application is None:
        return 'Bot not initialized', 500
    
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return 'OK'

def setup_bot():
    """Настройка бота"""
    global application
    
    if not BOT_TOKEN:
        logging.error("❌ BOT_TOKEN не установлен!")
        return False
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики (импортируй свои функции)
    from bot_handlers import start, list_rr_command, list_pd_command, button_handler, error_handler
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list_rr", list_rr_command))
    application.add_handler(CommandHandler("list_pd", list_pd_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    # Настраиваем webhook
    webhook_url = os.environ.get('RENDER_EXTERNAL_URL', '') + '/webhook'
    
    if webhook_url:
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get('PORT', 10000)),
            url_path=BOT_TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
        logging.info(f"✅ Webhook установлен: {webhook_url}")
    else:
        logging.error("❌ RENDER_EXTERNAL_URL не установлен!")
        return False
    
    return True

if __name__ == '__main__':
    if setup_bot():
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        logging.error("❌ Не удалось запустить бота")

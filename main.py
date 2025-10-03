import os
import logging
from datetime import datetime, time, timedelta
import pytz
from dotenv import load_dotenv
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ✅ ДОБАВЛЕНО: Импорт keep-alive
from keep_alive import keep_alive, start_pinging

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Конфигурация
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID', '-1003154247127')
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN не установлен!")
    exit(1)

print(f"✅ Бот запускается с CHAT_ID: {CHAT_ID}")

# ✅ ДОБАВЛЕНО: Запускаем keep-alive
keep_alive()
start_pinging()

# Данные для кнопок
SERVERS = {
    '👮‍♂Череповец': 'Череповец',
    '🐀Магадан': 'Магадан',
    '🏰 Подольск': 'Подольск',
    '🏙 Сургут': 'Сургут',
    '🏍 Ижевск': 'Ижевск',
    '🎄 Томск': 'Томск',
    '🐿 Тверь': 'Тверь',
    '🐦‍🔥 Вологда': 'Вологда',
    '🦁 Таганрог': 'Таганрог',
    '🌼 Новгород': 'Новгород',
    '🫐 Калуга': 'Калуга',
    '😹 Владимир': 'Владимир',
    '🐲 Кострома': 'Кострома',
    '🦎 Чита': 'Чита',
    '🧣 Астрахань': 'Астрахань',
    '👜 Братск': 'Братск',
    '🥐 Тамбов': 'Тамбов',
    '🥽 Якутск': 'Якутск',
    '🍭 Ульяновск': 'Ульяновск',
    '🎈 Липецк': 'Липецк',
    '💦 Барнаул': 'Барнаул',
    '🏛 Ярославль': 'Ярославль',
    '🦅 Орел': 'Орел',
    '🧸 Брянск': 'Брянск',
    '🪭 Псков': 'Псков',
    '🫚 Смоленск': 'Смоленск',
    '🪼 Ставрополь': 'Ставрополь',
    '🪅 Иваново': 'Иваново',
    '🪸 Тольятти': 'Тольятти',
    '🐋 Тюмень': 'Тюмень',
    '🌺 Кемерово': 'Кемерово',
    '🔫 Киров': 'Киров',
    '🍖 Оренбург': 'Оренбург',
    '🥋 Архангельск': 'Архангельск',
    '🃏 Курск': 'Курск',
    '🎳 Мурманск': 'Мурманск',
    '🎷 Пенза': 'Пенза',
    '🎭 Рязань': 'Рязань',
    '⛳ Тула': 'Тула',
    '🏟 Пермь': 'Пермь',
    '🐨 Хабаровск': 'Хабаровск',
    '🪄 Чебоксары': 'Чебоксары',
    '🖇 Красноярск': 'Красноярск',
    '🕊 Челябинск': 'Челябинск',
    '👒 Калининград': 'Калининград',
    '🧶 Владивосток': 'Владивосток',
    '🌂 Владикавказ': 'Владикавказ',
    '⛑️ Махачкала': 'Махачкала',
    '🎓 Белгород': 'Белгород',
    '👑 Воронеж': 'Воронеж',
    '🎒 Волгоград': 'Волгоград',
    '🌪 Иркутск': 'Иркутск',
    '🪙 Омск': 'Омск',
    '🐉 Саратов': 'Саратов',
    '🍙 Грозный': 'Грозный',
    '🍃 Новосибирск': 'Новосибирск',
    '🪿 Арзамас': 'Арзамас',
    '🪻 Краснодар': 'Краснодар',
    '📗 Екатеринбург': 'Екатеринбург',
    '🪺 Анапа': 'Анапа',
    '🍺 Ростов': 'Ростов',
    '🎧 Самара': 'Самара',
    '🏛 Казань': 'Казань',
    '🌊 Сочи': 'Сочи',
    '🌪 Уфа': 'Уфа',
    '🌉 СПб': 'Санкт-Петербург',
    '🌇 Москва': 'Москва'
}

# Глобальные переменные
user_states = {}
rr_entries = []
pd_entries = []
# ✅ ДОБАВЛЕНО: Храним ID последних сообщений с листами
last_rr_message_id = None
last_pd_message_id = None

# Время постинга и очистки
PD_POST_TIME = time(5, 0, 0, tzinfo=MOSCOW_TZ)
RR_POST_TIME = time(0, 0, 0, tzinfo=MOSCOW_TZ)
CLEANUP_TIME = time(23, 59, 0, tzinfo=MOSCOW_TZ)

def create_main_menu():
    """Создает главное меню"""
    keyboard = [
        [InlineKeyboardButton("📋 Заполнить RR лист", callback_data="fill_rr")],
        [InlineKeyboardButton("🏥 Заполнить PD лист", callback_data="fill_pd")],
        [InlineKeyboardButton("📊 Посмотреть текущие листы", callback_data="view_lists")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_server_keyboard():
    """Создает клавиатуру с серверами"""
    keyboard = []
    row = []
    
    for i, (emoji, name) in enumerate(SERVERS.items()):
        btn = InlineKeyboardButton(emoji, callback_data=f"server_{name}")
        row.append(btn)
        
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = create_main_menu()
    welcome_text = """
🤖 Добро пожаловать в бот KF Black Russia!

Выберите действие:
• 📋 RR лист - для заполнения RR листа
• 🏥 PD лист - для заполнения PD листа
• 📊 Посмотреть текущие листы
• ❓ Помощь
    """
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды помощи"""
    help_text = """
📖 Инструкция по использованию бота:

1. **RR лист** (00:00 - 05:00 МСК):
   - Выберите сервер
   - Напишите что слетает

2. **PD лист** (05:01 - 23:59 МСК):
   - Выберите категорию (Дома/Гаражи)
   - Выберите время
   - Выберите сервер
   - Напишите что слетает

⏰ Автопостинг:
• RR лист публикуется в 00:00
• PD лист публикуется в 05:00
• 🧹 Ежедневный сброс в 23:59
    """
    keyboard = create_main_menu()
    await update.message.reply_text(help_text, reply_markup=keyboard)

async def format_rr_list():
    """Форматирует RR лист для постинга"""
    today = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y")
    text = f"<b>PP list by @kfblackrussia {today}</b>\n\n"
    
    servers_list = [
        "👮‍♂Череповец -", "🐀Магадан -", "🏰 ᴘᴏᴅᴏʟsᴋ -", "🏙 sᴜʀɢᴜᴛ -", "🏍 ɪᴢʜᴇᴠsᴋ -",
        "🎄 ᴛᴏᴍsᴋ -", "🐿 ᴛᴠᴇʀ -", "🐦‍🔥 ᴠᴏʟᴏɢᴅᴀ -", "🦁 ᴛᴀɢᴀɴʀᴏɢ -", "🌼 ɴᴏᴠɢᴏʀᴏᴅ -",
        "🫐 ᴋᴀʟᴜɢᴀ -", "😹 ᴠʟᴀᴅɪᴍɪʀ -", "🐲 ᴋᴏsᴛʀᴏᴍᴀ -", "🦎 ᴄʜɪᴛᴀ -", "🧣 ᴀsᴛʀᴀᴋʜᴀɴ -",
        "👜 ʙʀᴀᴛsᴋ -", "🥐 ᴛᴀᴍʙᴏᴠ -", "🥽 ʏᴀᴋᴜᴛsᴋ -", "🍭 ᴜʟʏᴀɴᴏᴠsᴋ -", "🎈 ʟɪᴘᴇᴛsᴋ -",
        "💦 ʙᴀʀɴᴀᴜʟ -", "🏛 ʏᴀʀᴏsʟᴀᴠʟ -", "🦅 ᴏʀᴇʟ -", "🧸 ʙʀʏᴀɴsᴋ -", "🪭 ᴘsᴋᴏᴠ -",
        "🫚 sᴍᴏʟᴇɴsᴋ -", "🪼 sᴛᴀᴠʀᴏᴘᴏʟ -", "🪅 ɪᴠᴀɴᴏᴠᴏ -", "🪸 ᴛᴏʟʏᴀᴛᴛɪ -", "🐋 ᴛʏᴜᴍᴇɴ -",
        "🌺 ᴋᴇᴍᴇʀᴏᴠᴏ -", "🔫 ᴋɪʀᴏᴠ -", "🍖 ᴏʀᴇɴʙᴜʀɢ -", "🥋 ᴀʀᴋʜᴀɴɢᴇʟsᴋ -", "🃏 ᴋᴜʀsᴋ -",
        "🎳 ᴍᴜʀᴍᴀɴsᴋ -", "🎷 ᴘᴇɴᴢᴀ -", "🎭 ʀʏᴀᴢᴀɴ -", "⛳ ᴛᴜʟᴀ -", "🏟 ᴘᴇʀᴍ -",
        "🐨 ᴋʜᴀʙᴀʀᴏᴠsᴋ -", "🪄 ᴄʜᴇʙᴏᴋsᴀʀ -", "🖇 ᴋʀᴀsɴᴏʏᴀʀsᴋ -", "🕊 ᴄʜᴇʟʏᴀʙɪɴsᴋ -",
        "👒 ᴋᴀʟɪɴɪɴɢʀᴀᴅ -", "🧶 ᴠʟᴀᴅɪᴠᴏsᴛᴏᴋ -", "🌂 ᴠʟᴀᴅɪᴋᴀᴠᴋᴀᴢ -", "⛑️ ᴍᴀᴋʜᴀᴄʜᴋᴀʟᴀ -",
        "🎓 ʙᴇʟɢᴏʀᴏᴅ -", "👑 ᴠᴏʀᴏɴᴇᴢʜ -", "🎒 ᴠᴏʟɢᴏɢʀᴀᴅ -", "🌪 ɪʀᴋᴜᴛsᴋ -", "🪙 ᴏᴍsᴋ -",
        "🐉 sᴀʀᴀᴛᴏᴠ -", "🍙 ɢʀᴏᴢɴʏ -", "🍃 ɴᴏᴠᴏsɪʙ -", "🪿 ᴀʀᴢᴀᴍᴀs -", "🪻 ᴋʀᴀsɴᴏᴅᴀʀ -",
        "📗 ᴇᴋʙ -", "🪺 ᴀɴᴀᴘᴀ -", "🍺 ʀᴏsᴛᴏᴠ -", "🎧 sᴀᴍᴀʀᴀ -", "🏛 ᴋᴀᴢᴀɴ -",
        "🌊 sᴏᴄʜɪ -", "🌪 ᴜғᴀ -", "🌉 sᴘʙ -", "🌇 ᴍᴏsᴄᴏᴡ -", "🤎 ᴄʜᴏᴄᴏ -",
        "📕 ᴄʜɪʟʟɪ -", "❄ ɪᴄᴇ -", "📓 ɢʀᴀʏ -", "📘 ᴀǫᴜᴀ -", "🩶 ᴘʟᴀᴛɪɴᴜᴍ -",
        "💙 ᴀᴢᴜʀᴇ -", "💛️ ɢᴏʟᴅ -", "❤‍🔥 ᴄʀɪᴍsᴏɴ -", "🩷 ᴍᴀɢᴇɴᴛᴀ -", "🤍 ᴡʜɪᴛᴇ -",
        "💜 ɪɴᴅɪɢᴏ -", "🖤 ʙʟᴀᴄᴋ -", "🍒 ᴄʜᴇʀʀʏ -", "💕 ᴘɪɴᴋ -", "🍋 ʟɪᴍᴇ -",
        "💜 ᴘᴜʀᴘʟᴇ -", "🧡 ᴏʀᴀɴɢᴇ -", "💛 ʏᴇʟʟᴏᴡ -", "💙 ʙʟᴜᴇ -", "💚 ɢʀᴇᴇɴ -",
        "❤‍🩹 ʀᴇᴅ -"
    ]
    
    server_data = {server.split(' -')[0]: '-' for server in servers_list}
    
    for entry in rr_entries:
        server_name = entry['server']
        for emoji, name in SERVERS.items():
            if name == server_name:
                if emoji in server_data:
                    server_data[emoji] = entry.get('description', 'Слёт')
                break
    
    for server in servers_list:
        emoji = server.split(' -')[0]
        value = server_data.get(emoji, '-')
        text += f"{emoji} - {value}\n"
    
    return text

async def format_pd_list():
    """Форматирует PD лист для постинга"""
    today = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y")
    text = f"<b>PD list by @kfblackrussia {today}</b>\n\n"
    
    text += "<b>Дома</b>\n"
    houses_data = {}
    for entry in pd_entries:
        if entry['category'] == 'house':
            time_key = entry['time']
            if time_key not in houses_data:
                houses_data[time_key] = []
            houses_data[time_key].append(entry)
    
    if houses_data:
        for time_key in sorted(houses_data.keys()):
            text += f"<b>{time_key}</b>\n"
            for entry in houses_data[time_key]:
                text += f"{entry['server']}: {entry.get('description', 'Слёт')}\n"
            text += "\n"
    else:
        text += "Нет записей\n\n"
    
    text += "<b>Гаражи</b>\n"
    garages_data = {}
    for entry in pd_entries:
        if entry['category'] == 'garage':
            time_key = entry['time']
            if time_key not in garages_data:
                garages_data[time_key] = []
            garages_data[time_key].append(entry)
    
    if garages_data:
        for time_key in sorted(garages_data.keys()):
            text += f"<b>{time_key}</b>\n"
            for entry in garages_data[time_key]:
                text += f"{entry['server']}: {entry.get('description', 'Слёт')}\n"
            text += "\n"
    else:
        text += "Нет записей\n"
    
    return text

def create_add_button():
    """Создает кнопку Добавить слёт"""
    keyboard = [[InlineKeyboardButton("➕ Добавить слёт", url="https://t.me/blackpapashabot_bot")]]
    return InlineKeyboardMarkup(keyboard)

# ✅ ДОБАВЛЕНО: Функция обновления листов в чате
async def update_rr_list_in_chat(context: ContextTypes.DEFAULT_TYPE):
    """Обновляет RR лист в чате"""
    global last_rr_message_id
    
    try:
        rr_text = await format_rr_list()
        
        if last_rr_message_id:
            # Редактируем существующее сообщение
            await context.bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=last_rr_message_id,
                text=rr_text,
                parse_mode='HTML',
                reply_markup=create_add_button()
            )
            logging.info("✅ RR лист обновлен в чате")
        else:
            # Отправляем новое сообщение
            message = await context.bot.send_message(
                chat_id=CHAT_ID,
                text=rr_text,
                parse_mode='HTML',
                reply_markup=create_add_button()
            )
            last_rr_message_id = message.message_id
            await context.bot.pin_chat_message(chat_id=CHAT_ID, message_id=last_rr_message_id)
            logging.info("✅ RR лист отправлен и закреплен в чате")
            
    except Exception as e:
        logging.error(f"❌ Ошибка обновления RR листа: {e}")

async def update_pd_list_in_chat(context: ContextTypes.DEFAULT_TYPE):
    """Обновляет PD лист в чате"""
    global last_pd_message_id
    
    try:
        pd_text = await format_pd_list()
        
        if last_pd_message_id:
            # Редактируем существующее сообщение
            await context.bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=last_pd_message_id,
                text=pd_text,
                parse_mode='HTML',
                reply_markup=create_add_button()
            )
            logging.info("✅ PD лист обновлен в чате")
        else:
            # Отправляем новое сообщение
            message = await context.bot.send_message(
                chat_id=CHAT_ID,
                text=pd_text,
                parse_mode='HTML',
                reply_markup=create_add_button()
            )
            last_pd_message_id = message.message_id
            await context.bot.pin_chat_message(chat_id=CHAT_ID, message_id=last_pd_message_id)
            logging.info("✅ PD лист отправлен и закреплен в чате")
            
    except Exception as e:
        logging.error(f"❌ Ошибка обновления PD листа: {e}")

async def post_rr_list(context: ContextTypes.DEFAULT_TYPE):
    """Автопостинг RR листа в 00:00"""
    logging.info(f"🕒 Запуск post_rr_list, время: {datetime.now(MOSCOW_TZ)}")
    
    if rr_entries:
        await update_rr_list_in_chat(context)
        rr_entries.clear()
    else:
        logging.info("ℹ️ Нет записей для RR листа")

async def post_pd_list(context: ContextTypes.DEFAULT_TYPE):
    """Автопостинг PD листа в 05:00"""
    logging.info(f"🕒 Запуск post_pd_list, время: {datetime.now(MOSCOW_TZ)}")
    
    if pd_entries:
        await update_pd_list_in_chat(context)
        pd_entries.clear()
    else:
        logging.info("ℹ️ Нет записей для PD листа")

async def list_rr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для ручной отправки RR листа"""
    try:
        await update_rr_list_in_chat(context)
        await update.message.reply_text("✅ RR лист обновлен в чате!")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки RR листа: {e}")
        await update.message.reply_text("❌ Ошибка отправки RR листа")

async def list_pd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для ручной отправки PD листа"""
    try:
        await update_pd_list_in_chat(context)
        await update.message.reply_text("✅ PD лист обновлен в чате!")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки PD листа: {e}")
        await update.message.reply_text("❌ Ошибка отправки PD листа")

async def daily_cleanup(context: ContextTypes.DEFAULT_TYPE):
    """Ежедневный сброс всех листов в 23:59"""
    global last_rr_message_id, last_pd_message_id
    
    rr_count = len(rr_entries)
    pd_count = len(pd_entries)
    
    rr_entries.clear()
    pd_entries.clear()
    user_states.clear()
    
    # ✅ Очищаем ID сообщений при сбросе
    last_rr_message_id = None
    last_pd_message_id = None
    
    try:
        today = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y")
        cleanup_text = f"""
🧹 <b>ЕЖЕДНЕВНЫЙ СБРОС - {today}</b>

✅ Все листы очищены:
• RR записей удалено: {rr_count}
• PD записей удалено: {pd_count}

🔄 Новый день начнется в 00:00!
        """
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=cleanup_text,
            parse_mode='HTML'
        )
        logging.info(f"🧹 Ежедневный сброс: удалено {rr_count} RR и {pd_count} PD записей")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки уведомления о сбросе: {e}")

async def view_lists_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает текущие собранные листы"""
    query = update.callback_query
    await query.answer()
    
    now = datetime.now(MOSCOW_TZ).time()
    today = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y")
    
    if time(0, 0) <= now <= time(5, 0):
        if rr_entries:
            rr_text = await format_rr_list()
            text = f"📋 <b>Текущий RR лист на {today}</b> (будет опубликован в 00:00):\n\n{rr_text}"
        else:
            text = f"📋 RR лист на {today} пока пуст"
    else:
        if pd_entries:
            pd_text = await format_pd_list()
            text = f"🏥 <b>Текущий PD лист на {today}</b> (будет опубликован в 05:00):\n\n{pd_text}"
        else:
            text = f"🏥 PD лист на {today} пока пуст"
    
    text += f"\n\n🧹 <i>Ежедневный сброс в 23:59</i>"
    keyboard = create_main_menu()
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')

# ✅ ДОБАВЛЕНО: Обработчик текстовых сообщений для ввода описания
async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода описания слёта"""
    user_id = update.message.from_user.id
    
    if user_id not in user_states or user_states[user_id]['step'] != 'description':
        await update.message.reply_text("❌ Неизвестная команда. Используйте /start")
        return
    
    description = update.message.text
    user_state = user_states[user_id]
    
    if user_state['type'] == 'rr':
        # Для RR листа
        rr_entry = {
            'server': user_state['server'],
            'description': description,
            'timestamp': datetime.now(MOSCOW_TZ)
        }
        rr_entries.append(rr_entry)
        
        # ✅ ОБНОВЛЯЕМ RR ЛИСТ В ЧАТЕ
        await update_rr_list_in_chat(context)
        
        response_text = f"""
✅ Запись добавлена в RR лист!

Сервер: {user_state['server']}
Описание: {description}

📋 Лист обновлен в чате!
        """
        
    else:
        # Для PD листа
        category_name = "Дома" if user_state['category'] == 'house' else "Гаражи"
        pd_entry = {
            'server': user_state['server'],
            'category': user_state['category'],
            'time': user_state['time'],
            'description': description,
            'timestamp': datetime.now(MOSCOW_TZ)
        }
        pd_entries.append(pd_entry)
        
        # ✅ ОБНОВЛЯЕМ PD ЛИСТ В ЧАТЕ
        await update_pd_list_in_chat(context)
        
        response_text = f"""
✅ Запись добавлена в PD лист!

Сервер: {user_state['server']}
Категория: {category_name}
Время: {user_state['time']}
Описание: {description}

🏥 Лист обновлен в чате!
        """
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("📊 Посмотреть листы", callback_data="view_lists"),
        InlineKeyboardButton("➕ Добавить ещё", callback_data=f"fill_{user_state['type']}")
    ]])
    
    await update.message.reply_text(response_text, reply_markup=keyboard)
    
    # Очищаем состояние пользователя
    del user_states[user_id]

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "fill_rr":
        now = datetime.now(MOSCOW_TZ).time()
        if time(5, 1) <= now <= time(23, 59):
            await query.edit_message_text("❌ Сейчас время для PD листа!\nRR лист доступен с 00:00 до 05:00 МСК.")
            return
        
        user_states[user_id] = {'type': 'rr', 'step': 'server'}
        keyboard = create_server_keyboard()
        await query.edit_message_text("🎮 Выберите сервер для RR листа:", reply_markup=keyboard)
        
    elif data == "fill_pd":
        now = datetime.now(MOSCOW_TZ).time()
        if time(0, 0) <= now <= time(5, 0):
            await query.edit_message_text("❌ Сейчас время для RR листа!\nPD лист доступен с 05:01 до 23:59 МСК.")
            return
        
        user_states[user_id] = {'type': 'pd', 'step': 'category'}
        keyboard = [
            [InlineKeyboardButton("🏠 Дома", callback_data="pd_house")],
            [InlineKeyboardButton("🚗 Гаражи", callback_data="pd_garage")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        await query.edit_message_text("🏥 Выберите категорию для PD листа:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "view_lists":
        await view_lists_command(update, context)
        return
    
    elif data == "help":
        await help_command(update, context)
        return
    
    elif data == "back_to_main":
        if user_id in user_states:
            del user_states[user_id]
        keyboard = create_main_menu()
        await query.edit_message_text("🔙 Возвращаемся в главное меню:", reply_markup=keyboard)
    
    elif data.startswith("pd_"):
        if data in ["pd_house", "pd_garage"]:
            user_states[user_id]['step'] = 'time'
            user_states[user_id]['category'] = 'house' if 'house' in data else 'garage'
            
            category_name = "Дома" if user_states[user_id]['category'] == 'house' else "Гаражи"
            
            if user_states[user_id]['category'] == 'house':
                keyboard = [
                    [InlineKeyboardButton("15:00", callback_data="time_15")],
                    [InlineKeyboardButton("17:00", callback_data="time_17")],
                    [InlineKeyboardButton("20:00", callback_data="time_20")],
                    [InlineKeyboardButton("22:00", callback_data="time_22")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="fill_pd")]
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("14:00", callback_data="time_14")],
                    [InlineKeyboardButton("16:00", callback_data="time_16")],
                    [InlineKeyboardButton("19:00", callback_data="time_19")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="fill_pd")]
                ]
            
            await query.edit_message_text(f"⏰ Выберите время для {category_name}:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("time_"):
        user_states[user_id]['step'] = 'server'
        time_map = {
            '14': '14:00', '15': '15:00', '16': '16:00', 
            '17': '17:00', '19': '19:00', '20': '20:00', '22': '22:00'
        }
        user_states[user_id]['time'] = time_map[data.split('_')[1]]
        keyboard = create_server_keyboard()
        await query.edit_message_text("🎮 Отлично! Теперь выберите сервер:", reply_markup=keyboard)
    
    elif data.startswith("server_"):
        server_name = data.split('_', 1)[1]
        user_states[user_id]['server'] = server_name
        user_states[user_id]['step'] = 'description'
        
        if user_states[user_id]['type'] == 'rr':
            await query.edit_message_text(
                f"🎮 Сервер: {server_name}\n\n"
                f"📝 Теперь напишите что именно слетает на этом сервере:\n"
                f"(Например: 'Слёт домов 15:00' или 'Слёт гаражей 14:00')"
            )
        else:
            category_name = "Дома" if user_states[user_id]['category'] == 'house' else "Гаражи"
            time_selected = user_states[user_id]['time']
            await query.edit_message_text(
                f"🎮 Сервер: {server_name}\n"
                f"🏥 Категория: {category_name}\n"
                f"⏰ Время: {time_selected}\n\n"
                f"📝 Теперь напишите что именно слетает:\n"
                f"(Например: 'Слёт домов' или 'Слёт 3 гаража')"
            )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    error_msg = str(context.error)
    logging.error(f"Ошибка: {error_msg}", exc_info=context.error)

def reset_bot_webhook():
    """Сбрасывает webhook если он был установлен"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        response = requests.get(url, params={"drop_pending_updates": True})
        if response.status_code == 200:
            logging.info("✅ Webhook сброшен, pending updates очищены")
        else:
            logging.warning("⚠️ Не удалось сбросить webhook")
    except Exception as e:
        logging.error(f"❌ Ошибка сброса webhook: {e}")

def setup_schedule(application: Application):
    """Настройка расписания автопостинга"""
    try:
        job_queue = application.job_queue
        
        if job_queue is None:
            logging.error("❌ Job Queue недоступна. Убедитесь, что установлена версия python-telegram-bot с job-queue")
            return False
        
        current_time = datetime.now(MOSCOW_TZ)
        logging.info(f"⏰ Текущее время сервера: {current_time}")
        logging.info(f"📅 Настройка расписания: RR в {RR_POST_TIME}, PD в {PD_POST_TIME}")
        
        # Очищаем существующие задачи
        for job in job_queue.jobs():
            job.schedule_removal()
        
        # ✅ ДОБАВЛЯЕМ ЗАДАЧИ С ПРАВИЛЬНЫМИ ПАРАМЕТРАМИ
        job_queue.run_daily(post_rr_list, RR_POST_TIME, name="rr_post")
        job_queue.run_daily(post_pd_list, PD_POST_TIME, name="pd_post") 
        job_queue.run_daily(daily_cleanup, CLEANUP_TIME, name="cleanup")
        
        logging.info("✅ Расписание настроено успешно!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Ошибка настройки расписания: {e}")
        return False

async def check_schedule_periodically():
    """Периодическая проверка и выполнение задач по расписанию"""
    while True:
        now = datetime.now(MOSCOW_TZ)
        current_time = now.time()
        
        # Проверяем RR лист (00:00)
        if current_time.hour == 0 and current_time.minute == 0:
            logging.info("🕒 Время публикации RR листа!")
            # Здесь нужно вызвать функцию публикации RR листа
            # await post_rr_list() - нужно передать context
        
        # Проверяем PD лист (05:00)  
        elif current_time.hour == 5 and current_time.minute == 0:
            logging.info("🕒 Время публикации PD листа!")
            # Здесь нужно вызвать функцию публикации PD листа
        
        # Проверяем очистку (23:59)
        elif current_time.hour == 23 and current_time.minute == 59:
            logging.info("🕒 Время ежедневной очистки!")
            # Здесь нужно вызвать функцию очистки
        
        # Ждем 1 минуту перед следующей проверкой
        await asyncio.sleep(60)

def main():
    """Основная функция запуска бота"""
    try:
        # Создаем Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("list_rr", list_rr_command))
        application.add_handler(CommandHandler("list_pd", list_pd_command))
        
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description))
        
        application.add_error_handler(error_handler)
        
        # ✅ ДОБАВЛЕНО: Запускаем keep-alive
        keep_alive()
        start_pinging()
        
        # Пытаемся настроить расписание (если job-queue доступен)
        try:
            setup_schedule(application)
            logging.info("✅ Job-queue расписание настроено")
        except Exception as e:
            logging.warning(f"⚠️ Job-queue недоступен, используем альтернативный метод: {e}")
            # Запускаем альтернативный планировщик
            asyncio.create_task(check_schedule_periodically())
        
        # Запускаем бота
        logging.info("🤖 Запускаем бота...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка при запуске: {e}")

if __name__ == "__main__":
    main()

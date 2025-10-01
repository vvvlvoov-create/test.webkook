import os
import logging
from datetime import datetime, time, timedelta
import pytz
from dotenv import load_dotenv
import asyncio

# ✅ ДОБАВЛЕНО: Импорт keep-alive
from keep_alive import keep_alive, start_pinging

# Загружаем переменные окружения
load_dotenv()

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    print("✅ Основные импорты telegram работают!")
except ImportError as e:
    print(f"❌ Критическая ошибка импорта: {e}")
    exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Конфигурация
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID', '@kfblackrussia')
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN не установлен!")
    exit(1)

print(f"✅ Бот запускается с CHAT_ID: {CHAT_ID}")

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
rr_entries = []  # Хранит записи RR листа
pd_entries = []  # Хранит записи PD листа

# Время постинга и очистки
PD_POST_TIME = time(5, 0, 0, tzinfo=MOSCOW_TZ)  # 05:00 МСК - PD лист
RR_POST_TIME = time(0, 0, 0, tzinfo=MOSCOW_TZ)  # 00:00 МСК - RR лист
CLEANUP_TIME = time(23, 59, 0, tzinfo=MOSCOW_TZ)  # 23:59 МСК - ежедневный сброс

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
        
        if (i + 1) % 3 == 0:  # 3 кнопки в строке
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Кнопка назад
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
• 📊 Посмотреть текущие листы - просмотр собранных данных
• ❓ Помощь - инструкция по использованию

Бот работает автоматически с 00:00 до 05:00 для RR и с 05:01 до 23:59 для PD.

📢 Автопостинг:
• RR лист публикуется в 00:00
• PD лист публикуется в 05:00
• 🧹 Ежедневный сброс в 23:59
    """
    
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды помощи"""
    help_text = """
📖 Инструкция по использованию бота:

1. **RR лист** (00:00 - 05:00 МСК):
   - Выберите сервер
   - Укажите что слетает

2. **PD лист** (05:01 - 23:59 МСК):
   - Выберите категорию (Дома/Гаражи)
   - Выберите время
   - Выберите сервер
   - Укажите что слетает

⏰ Время работы:
• RR: с 00:00 до 05:00
• PD: с 05:01 до 23:59

📢 Автопостинг:
• RR лист публикуется в 00:00
• PD лист публикуется в 05:00
• 🧹 Ежедневный сброс в 23:59

Каждый день в 23:59 все листы очищаются и начинается новый день!
    """
    
    keyboard = create_main_menu()
    await update.message.reply_text(help_text, reply_markup=keyboard)

async def format_rr_list():
    """Форматирует RR лист для постинга"""
    today = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y")
    
    # Создаем базовую структуру всех серверов
    all_servers = {
        '👮‍♂Череповец': '-',
        '🐀Магадан': '-',
        '🏰 ᴘᴏᴅᴏʟsᴋ': '-',
        '🏙 sᴜʀɢᴜᴛ': '-',
        '🏍 ɪᴢʜᴇᴠsᴋ': '-',
        '🎄 ᴛᴏᴍsᴋ': '-',
        '🐿 ᴛᴠᴇʀ': '-',
        '🐦‍🔥 ᴠᴏʟᴏɢᴅᴀ': '-',
        '🦁 ᴛᴀɢᴀɴʀᴏɢ': '-',
        '🌼 ɴᴏᴠɢᴏʀᴏᴅ': '-',
        '🫐 ᴋᴀʟᴜɢᴀ': '-',
        '😹 ᴠʟᴀᴅɪᴍɪʀ': '-',
        '🐲 ᴋᴏsᴛʀᴏᴍᴀ': '-',
        '🦎 ᴄʜɪᴛᴀ': '-',
        '🧣 ᴀsᴛʀᴀᴋʜᴀɴ': '-',
        '👜 ʙʀᴀᴛsᴋ': '-',
        '🥐 ᴛᴀᴍʙᴏᴠ': '-',
        '🥽 ʏᴀᴋᴜᴛsᴋ': '-',
        '🍭 ᴜʟʏᴀɴᴏᴠsᴋ': '-',
        '🎈 ʟɪᴘᴇᴛsᴋ': '-',
        '💦 ʙᴀʀɴᴀᴜʟ': '-',
        '🏛 ʏᴀʀᴏsʟᴀᴠʟ': '-',
        '🦅 ᴏʀᴇʟ': '-',
        '🧸 ʙʀʏᴀɴsᴋ': '-',
        '🪭 ᴘsᴋᴏᴠ': '-',
        '🫚 sᴍᴏʟᴇɴsᴋ': '-',
        '🪼 sᴛᴀᴠʀᴏᴘᴏʟ': '-',
        '🪅 ɪᴠᴀɴᴏᴠᴏ': '-',
        '🪸 ᴛᴏʟʏᴀᴛᴛɪ': '-',
        '🐋 ᴛʏᴜᴍᴇɴ': '-',
        '🌺 ᴋᴇᴍᴇʀᴏᴠᴏ': '-',
        '🔫 ᴋɪʀᴏᴠ': '-',
        '🍖 ᴏʀᴇɴʙᴜʀɢ': '-',
        '🥋 ᴀʀᴋʜᴀɴɢᴇʟsᴋ': '-',
        '🃏 ᴋᴜʀsᴋ': '-',
        '🎳 ᴍᴜʀᴍᴀɴsᴋ': '-',
        '🎷 ᴘᴇɴᴢᴀ': '-',
        '🎭 ʀʏᴀᴢᴀɴ': '-',
        '⛳ ᴛᴜʟᴀ': '-',
        '🏟 ᴘᴇʀᴍ': '-',
        '🐨 ᴋʜᴀʙᴀʀᴏᴠsᴋ': '-',
        '🪄 ᴄʜᴇʙᴏᴋsᴀʀ': '-',
        '🖇 ᴋʀᴀsɴᴏʏᴀʀsᴋ': '-',
        '🕊 ᴄʜᴇʟʏᴀʙɪɴsᴋ': '-',
        '👒 ᴋᴀʟɪɴɪɴɢʀᴀᴅ': '-',
        '🧶 ᴠʟᴀᴅɪᴠᴏsᴛᴏᴋ': '-',
        '🌂 ᴠʟᴀᴅɪᴋᴀᴠᴋᴀᴢ': '-',
        '⛑️ ᴍᴀᴋʜᴀᴄʜᴋᴀʟᴀ': '-',
        '🎓 ʙᴇʟɢᴏʀᴏᴅ': '-',
        '👑 ᴠᴏʀᴏɴᴇᴢʜ': '-',
        '🎒 ᴠᴏʟɢᴏɢʀᴀᴅ': '-',
        '🌪 ɪʀᴋᴜᴛsᴋ': '-',
        '🪙 ᴏᴍsᴋ': '-',
        '🐉 sᴀʀᴀᴛᴏᴠ': '-',
        '🍙 ɢʀᴏᴢɴʏ': '-',
        '🍃 ɴᴏᴠᴏsɪʙ': '-',
        '🪿 ᴀʀᴢᴀᴍᴀs': '-',
        '🪻 ᴋʀᴀsɴᴏᴅᴀʀ': '-',
        '📗 ᴇᴋʙ': '-',
        '🪺 ᴀɴᴀᴘᴀ': '-',
        '🍺 ʀᴏsᴛᴏᴠ': '-',
        '🎧 sᴀᴍᴀʀᴀ': '-',
        '🏛 ᴋᴀᴢᴀɴ': '-',
        '🌊 sᴏᴄʜɪ': '-',
        '🌪 ᴜғᴀ': '-',
        '🌉 sᴘʙ': '-',
        '🌇 ᴍᴏsᴄᴏᴡ': '-',
        '🤎 ᴄʜᴏᴄᴏ': '-',
        '📕 ᴄʜɪʟʟɪ': '-',
        '❄ ɪᴄᴇ': '-',
        '📓 ɢʀᴀʏ': '-',
        '📘 ᴀǫᴜᴀ': '-',
        '🩶 ᴘʟᴀᴛɪɴᴜᴍ': '-',
        '💙 ᴀᴢᴜʀᴇ': '-',
        '💛️ ɢᴏʟᴅ': '-',
        '❤‍🔥 ᴄʀɪᴍsᴏɴ': '-',
        '🩷 ᴍᴀɢᴇɴᴛᴀ': '-',
        '🤍 ᴡʜɪᴛᴇ': '-',
        '💜 ɪɴᴅɪɢᴏ': '-',
        '🖤 ʙʟᴀᴄᴋ': '-',
        '🍒 ᴄʜᴇʀʀʏ': '-',
        '💕 ᴘɪɴᴋ': '-',
        '🍋 ʟɪᴍᴇ': '-',
        '💜 ᴘᴜʀᴘʟᴇ': '-',
        '🧡 ᴏʀᴀɴɢᴇ': '-',
        '💛 ʏᴇʟʟᴏᴡ': '-',
        '💙 ʙʟᴜᴇ': '-',
        '💚 ɢʀᴇᴇɴ': '-',
        '❤‍🩹 ʀᴇᴅ': '-'
    }
    
    # Заполняем данные из записей
    for entry in rr_entries:
        server_name = entry['server']
        # Находим соответствующий emoji ключ
        for emoji, name in SERVERS.items():
            if name == server_name:
                all_servers[emoji] = entry.get('description', 'Слёт')
                break
    
    # Форматируем текст
    text = f"<b>PP list by kfblackrussia {today}</b>\n\n"
    
    # Группируем серверы по 3 в строку
    servers_list = list(all_servers.items())
    for i in range(0, len(servers_list), 3):
        line = ""
        for j in range(3):
            if i + j < len(servers_list):
                emoji, value = servers_list[i + j]
                line += f"{emoji} - {value}  "
        text += line + "\n"
    
    return text

async def format_pd_list():
    """Форматирует PD лист для постинга"""
    today = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y")
    
    # Группируем по времени и категории
    houses_data = {}
    garages_data = {}
    
    for entry in pd_entries:
        time_key = entry['time']
        category = entry['category']
        server = entry['server']
        
        if category == 'house':
            if time_key not in houses_data:
                houses_data[time_key] = {}
            if server not in houses_data[time_key]:
                houses_data[time_key][server] = []
            houses_data[time_key][server].append(entry)
        else:
            if time_key not in garages_data:
                garages_data[time_key] = {}
            if server not in garages_data[time_key]:
                garages_data[time_key][server] = []
            garages_data[time_key][server].append(entry)
    
    # Форматируем текст
    text = f"<b>PD list by @kfblackrussia {today}</b>\n\n"
    
    # Дома
    text += "<b>Дома</b>\n"
    if houses_data:
        for time_key in sorted(houses_data.keys()):
            text += f"<b>{time_key}</b>\n"
            for server, entries in houses_data[time_key].items():
                descriptions = [entry.get('description', 'Слёт') for entry in entries]
                text += f"{server}: {', '.join(descriptions)}\n"
            text += "\n"
    else:
        text += "Нет записей\n\n"
    
    # Гаражи
    text += "<b>Гаражи</b>\n"
    if garages_data:
        for time_key in sorted(garages_data.keys()):
            text += f"<b>{time_key}</b>\n"
            for server, entries in garages_data[time_key].items():
                descriptions = [entry.get('description', 'Слёт') for entry in entries]
                text += f"{server}: {', '.join(descriptions)}\n"
            text += "\n"
    else:
        text += "Нет записей\n"
    
    return text

def create_add_button():
    """Создает кнопку Добавить слёт"""
    keyboard = [[InlineKeyboardButton("➕ Добавить слёт", url="https://t.me/kfblackrussiabot_bot")]]
    return InlineKeyboardMarkup(keyboard)

async def post_rr_list(context: ContextTypes.DEFAULT_TYPE):
    """Автопостинг RR листа в 00:00"""
    logging.info(f"🕒 Запуск post_rr_list, время: {datetime.now(MOSCOW_TZ)}")
    logging.info(f"📊 RR записей: {len(rr_entries)}")
    
    if rr_entries:
        rr_text = await format_rr_list()
        logging.info(f"📝 Текст RR листа подготовлен")
        try:
            message = await context.bot.send_message(
                chat_id=CHAT_ID,
                text=rr_text,
                parse_mode='HTML',
                reply_markup=create_add_button()
            )
            # Закрепляем сообщение
            await context.bot.pin_chat_message(chat_id=CHAT_ID, message_id=message.message_id)
            logging.info("✅ RR лист опубликован и закреплен в канале")
            rr_entries.clear()
        except Exception as e:
            logging.error(f"❌ Ошибка отправки RR листа: {e}")
    else:
        logging.info("ℹ️ Нет записей для RR листа")

async def post_pd_list(context: ContextTypes.DEFAULT_TYPE):
    """Автопостинг PD листа в 05:00"""
    logging.info(f"🕒 Запуск post_pd_list, время: {datetime.now(MOSCOW_TZ)}")
    logging.info(f"📊 PD записей: {len(pd_entries)}")
    
    if pd_entries:
        pd_text = await format_pd_list()
        logging.info(f"📝 Текст PD листа подготовлен")
        try:
            message = await context.bot.send_message(
                chat_id=CHAT_ID,
                text=pd_text,
                parse_mode='HTML',
                reply_markup=create_add_button()
            )
            # Закрепляем сообщение
            await context.bot.pin_chat_message(chat_id=CHAT_ID, message_id=message.message_id)
            logging.info("✅ PD лист опубликован и закреплен в канале")
            pd_entries.clear()
        except Exception as e:
            logging.error(f"❌ Ошибка отправки PD листа: {e}")
    else:
        logging.info("ℹ️ Нет записей для PD листа")

async def list_rr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для ручной отправки RR листа"""
    if rr_entries:
        rr_text = await format_rr_list()
        try:
            message = await update.message.reply_text(
                text=rr_text,
                parse_mode='HTML',
                reply_markup=create_add_button()
            )
            logging.info("✅ RR лист отправлен по команде")
        except Exception as e:
            logging.error(f"❌ Ошибка отправки RR листа: {e}")
            await update.message.reply_text("❌ Ошибка отправки RR листа")
    else:
        await update.message.reply_text("📋 RR лист пуст")

async def list_pd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для ручной отправки PD листа"""
    if pd_entries:
        pd_text = await format_pd_list()
        try:
            message = await update.message.reply_text(
                text=pd_text,
                parse_mode='HTML',
                reply_markup=create_add_button()
            )
            logging.info("✅ PD лист отправлен по команде")
        except Exception as e:
            logging.error(f"❌ Ошибка отправки PD листа: {e}")
            await update.message.reply_text("❌ Ошибка отправки PD листа")
    else:
        await update.message.reply_text("🏥 PD лист пуст")

async def daily_cleanup(context: ContextTypes.DEFAULT_TYPE):
    """Ежедневный сброс всех листов в 23:59"""
    rr_count = len(rr_entries)
    pd_count = len(pd_entries)
    
    # Очищаем все записи
    rr_entries.clear()
    pd_entries.clear()
    user_states.clear()
    
    # Отправляем уведомление в канал
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
        logging.info(f"🧹 Ежедневный сброс в 23:59: удалено {rr_count} RR и {pd_count} PD записей")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки уведомления о сбросе: {e}")

async def view_lists_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает текущие собранные листы"""
    query = update.callback_query
    await query.answer()
    
    now = datetime.now(MOSCOW_TZ).time()
    today = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y")
    
    if time(0, 0) <= now <= time(5, 0):
        # Время RR
        if rr_entries:
            rr_text = await format_rr_list()
            text = f"📋 <b>Текущий RR лист на {today}</b> (будет опубликован в 00:00):\n\n{rr_text}"
        else:
            text = f"📋 RR лист на {today} пока пуст"
    else:
        # Время PD
        if pd_entries:
            pd_text = await format_pd_list()
            text = f"🏥 <b>Текущий PD лист на {today}</b> (будет опубликован в 05:00):\n\n{pd_text}"
        else:
            text = f"🏥 PD лист на {today} пока пуст"
    
    # Добавляем информацию о сбросе
    text += f"\n\n🧹 <i>Ежедневный сброс в 23:59</i>"
    
    keyboard = create_main_menu()
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "fill_rr":
        # Проверяем время для RR листа
        now = datetime.now(MOSCOW_TZ).time()
        if time(5, 1) <= now <= time(23, 59):
            await query.edit_message_text("❌ Сейчас время для PD листа!\nRR лист доступен с 00:00 до 05:00 МСК.")
            return
        
        user_states[user_id] = {'type': 'rr', 'step': 'server'}
        keyboard = create_server_keyboard()
        await query.edit_message_text("🎮 Выберите сервер для RR листа:", reply_markup=keyboard)
        
    elif data == "fill_pd":
        # Проверяем время для PD листа
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
        today = datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y")
        
        if user_states[user_id]['type'] == 'rr':
            # Для RR листа - добавляем запись
            rr_entry = {
                'server': server_name,
                'description': 'Слёт',
                'timestamp': datetime.now(MOSCOW_TZ)
            }
            rr_entries.append(rr_entry)
            
            rr_text = await format_rr_list()
            response_text = f"""
✅ Запись добавлена в RR лист на {today}!

Сервер: {server_name}
Тип: RR лист

📋 Запись будет опубликована в 00:00
            """
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("📊 Посмотреть листы", callback_data="view_lists"),
                InlineKeyboardButton("➕ Добавить ещё", callback_data="fill_rr")
            ]])
            
            await query.edit_message_text(response_text, reply_markup=keyboard)
            
        else:
            # Для PD листа - добавляем запись
            category_name = "Дома" if user_states[user_id]['category'] == 'house' else "Гаражи"
            time_selected = user_states[user_id]['time']
            
            pd_entry = {
                'server': server_name,
                'category': user_states[user_id]['category'],
                'time': time_selected,
                'description': 'Слёт',
                'timestamp': datetime.now(MOSCOW_TZ)
            }
            pd_entries.append(pd_entry)
            
            response_text = f"""
✅ Запись добавлена в PD лист на {today}!

Сервер: {server_name}
Категория: {category_name}
Время: {time_selected}

🏥 Запись будет опубликована в 05:00
            """
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("📊 Посмотреть листы", callback_data="view_lists"),
                InlineKeyboardButton("➕ Добавить ещё", callback_data="fill_pd")
            ]])
            
            await query.edit_message_text(response_text, reply_markup=keyboard)
        
        # Очищаем состояние пользователя
        if user_id in user_states:
            del user_states[user_id]

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    error_msg = str(context.error)
    logging.error(f"Ошибка: {error_msg}", exc_info=context.error)

def setup_schedule(application: Application):
    """Настройка расписания автопостинга"""
    job_queue = application.job_queue
    
    if job_queue is None:
        logging.error("❌ Job Queue не инициализирована")
        return
    
    # PD лист в 05:00
    job_queue.run_daily(
        post_pd_list,
        time=PD_POST_TIME,
        days=(0, 1, 2, 3, 4, 5, 6),
        name="post_pd_list"
    )
    
    # RR лист в 00:00
    job_queue.run_daily(
        post_rr_list,
        time=RR_POST_TIME,
        days=(0, 1, 2, 3, 4, 5, 6),
        name="post_rr_list"
    )
    
    # Ежедневный сброс в 23:59
    job_queue.run_daily(
        daily_cleanup,
        time=CLEANUP_TIME,
        days=(0, 1, 2, 3, 4, 5, 6),
        name="daily_cleanup"
    )
    
    logging.info(f"📅 Расписание настроено: PD в {PD_POST_TIME}, RR в {RR_POST_TIME}, сброс в {CLEANUP_TIME}")

def main():
    """Основная функция"""
    # ✅ ДОБАВЛЕНО: Запуск keep-alive системы
    keep_alive()
    start_pinging()
    
    logging.info("🚀 Запуск бота KF Black Russia...")
    logging.info(f"✅ CHAT_ID: {CHAT_ID}")
    logging.info(f"✅ Токен: {'установлен' if BOT_TOKEN else 'отсутствует'}")
    
    if not BOT_TOKEN:
        logging.error("❌ BOT_TOKEN не установлен!")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list_rr", list_rr_command))
    application.add_handler(CommandHandler("list_pd", list_pd_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    # Настраиваем расписание автопостинга ПОСЛЕ создания приложения
    setup_schedule(application)
    
    # Запускаем в режиме polling
    logging.info("🚀 Запуск в режиме polling...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()

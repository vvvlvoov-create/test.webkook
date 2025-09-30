import os
import logging
from datetime import datetime, time, timedelta
import asyncio
import pytz
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Используем простые импорты для стабильности
try:
    from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    print("✅ Основные импорты telegram работают!")
except ImportError as e:
    print(f"❌ Критическая ошибка импорта: {e}")
    exit(1)

# Настройка безопасного логирования (без токенов)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Скрываем токены в логах httpx 
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

# Конфигурация из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7719252121:AAEUyzzdo1JjYVfNv1uN_Y7PQFHR6de3T1o')
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME', '@kfblackrussia')
CHAT_ID = os.environ.get('CHAT_ID', '@kfblackrussia')
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Проверка обязательных переменных
if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN не установлен!")
    exit(1)

print(f"✅ Конфигурация загружена. CHAT_ID: {CHAT_ID}")

# Данные для кнопок
SERVERS = {
    '👮‍♂Череповец': 'Череповец',
    '🐀Магадан': 'Магадан',
    '🏰 ᴘᴏᴅᴏʟsᴋ': 'Подольск',
    '🏙 sᴜʀɢᴜᴛ': 'Сургут',
    '🏍 ɪᴢʜᴇᴠsᴋ': 'Ижевск',
    '🎄 ᴛᴏᴍsᴋ': 'Томск',
    '🐿 ᴛᴠᴇʀ': 'Тверь',
    '🐦‍🔥 ᴠᴏʟᴏɢᴅᴀ': 'Вологда',
    '🦁 ᴛᴀɢᴀɴʀᴏɢ': 'Таганрог',
    '🌼 ɴᴏᴠɢᴏʀᴏᴅ': 'Новгород',
    '🫐 ᴋᴀʟᴜɢᴀ': 'Калуга',
    '😹 ᴠʟᴀᴅɪᴍɪʀ': 'Владимир',
    '🐲 ᴋᴏsᴛʀᴏᴍᴀ': 'Кострома',
    '🦎 ᴄʜɪᴛᴀ': 'Чита',
    '🧣 ᴀsᴛʀᴀᴋʜᴀɴ': 'Астрахань',
    '👜 ʙʀᴀᴛsᴋ': 'Братск',
    '🥐 ᴛᴀᴍʙᴏᴡ': 'Тамбов',
    '🥽 ʏᴀᴋᴜᴛsᴋ': 'Якутск',
    '🍭 ᴜʟʏᴀɴᴏᴠsᴋ': 'Ульяновск',
    '🎈 ʟɪᴘᴇᴛsᴋ': 'Липецк',
    '💦 ʙᴀʀɴᴀᴜʟ': 'Барнаул',
    '🏛 ʏᴀʀᴏsʟᴀᴠʟ': 'Ярославль',
    '🦅 ᴏʀᴇʟ': 'Орел',
    '🧸 ʙʀʏᴀɴsᴋ': 'Брянск',
    '🪭 ᴘsᴋᴏᴠ': 'Псков',
    '🫚 sᴍᴏʟᴇɴsᴋ': 'Смоленск',
    '🪼 sᴛᴀᴠʀᴏᴘᴏʟ': 'Ставрополь',
    '🪅 ɪᴠᴀɴᴏᴠᴏ': 'Иваново',
    '🪸 ᴛᴏʟʏᴀᴛᴛɪ': 'Тольятти',
    '🐋 ᴛʏᴜᴍᴇɴ': 'Тюмень',
    '🌺 ᴋᴇᴍᴇʀᴏᴠᴏ': 'Кемерово',
    '🔫 ᴋɪʀᴏᴠ': 'Киров',
    '🍖 ᴏʀᴇɴʙᴜʀɢ': 'Оренбург',
    '🥋 ᴀʀᴋʜᴀɴɢᴇʟsᴋ': 'Архангельск',
    '🃏 ᴋᴜʀsᴋ': 'Курск',
    '🎳 ᴍᴜʀᴍᴀɴsᴋ': 'Мурманск',
    '🎷 ᴘᴇɴᴢᴀ': 'Пенза',
    '🎭 ʀʏᴀᴢᴀɴ': 'Рязань',
    '⛳ ᴛᴜʟᴀ': 'Тула',
    '🏟 ᴘᴇʀᴍ': 'Пермь',
    '🐨 ᴋʜᴀʙᴀʀᴏᴠsᴋ': 'Хабаровск',
    '🪄 ᴄʜᴇʙᴏᴋsᴀʀ': 'Чебоксары',
    '🖇 ᴋʀᴀsɴᴏʏᴀʀsᴋ': 'Красноярск',
    '🕊 ᴄʜᴇʟʏᴀʙɪɴsᴋ': 'Челябинск',
    '👒 ᴋᴀʟɪɴɪɴɢʀᴀᴅ': 'Калининград',
    '🧶 ᴠʟᴀᴅɪᴠᴏsᴛᴏᴋ': 'Владивосток',
    '🌂 ᴠʟᴀᴅɪᴋᴀᴠᴋᴀᴢ': 'Владикавказ',
    '⛑️ ᴍᴀᴋʜᴀᴄʜᴋᴀʟᴀ': 'Махачкала',
    '🎓 ʙᴇʟɢᴏʀᴏᴅ': 'Белгород',
    '👑 ᴠᴏʀᴏɴᴇᴢʜ': 'Воронеж',
    '🎒 ᴠᴏʟɢᴏɢʀᴀᴅ': 'Волгоград',
    '🌪 ɪʀᴋᴜᴛsᴋ': 'Иркутск',
    '🪙 ᴏᴍsᴋ': 'Омск',
    '🐉 sᴀʀᴀᴛᴏᴠ': 'Саратов',
    '🍙 ɢʀᴏᴢɴʏ': 'Грозный',
    '🍃 ɴᴏᴠᴏsɪʙ': 'Новосибирск',
    '🪿 ᴀʀᴢᴀᴍᴀs': 'Арзамас',
    '🪻 ᴋʀᴀsɴᴏᴅᴀʀ': 'Краснодар',
    '📗 ᴇᴋʙ': 'Екатеринбург',
    '🪺 ᴀɴᴀᴘᴀ': 'Анапа',
    '🍺 ʀᴏsᴛᴏᴠ': 'Ростов',
    '🎧 sᴀᴍᴀʀᴀ': 'Самара',
    '🏛 ᴋᴀᴢᴀɴ': 'Казань',
    '🌊 sᴏᴄʜɪ': 'Сочи',
    '🌪 ᴜғᴀ': 'Уфа',
    '🌉 sᴘʙ': 'Санкт-Петербург',
    '🌇 ᴍᴏsᴄᴏᴡ': 'Москва',
    '🤎 ᴄʜᴏᴄᴏ': 'Шоко',
    '📕 ᴄʜɪʟʟɪ': 'Чилли',
    '❄ ɪᴄᴇ': 'Айс',
    '📓 ɢʀᴀʏ': 'Грей',
    '📘 ᴀǫᴜᴀ': 'Аква',
    '🩶 ᴘʟᴀᴛɪɴᴜᴍ': 'Платинум',
    '💙 ᴀᴢᴜʀᴇ': 'Азуре',
    '💛️ ɢᴏʟᴅ': 'Голд',
    '❤‍🔥 ᴄʀɪᴍsᴏɴ': 'Кримсон',
    '🩷 ᴍᴀɢᴇɴᴛᴀ': 'Магента',
    '🤍 ᴡʜɪᴛᴇ': 'Вайт',
    '💜 ɪɴᴅɪɢᴏ': 'Индиго',
    '🖤 ʙʟᴀᴄᴋ': 'Блэк',
    '🍒 ᴄʜᴇʀʀʏ': 'Черри',
    '💕 ᴘɪɴᴋ': 'Пинк',
    '🍋 ʟɪᴍᴇ': 'Лайм',
    '💜 ᴘᴜʀᴘʟᴇ': 'Пурпл',
    '🧡 ᴏʀᴀɴɢᴇ': 'Оранж',
    '💛 ʏᴇʟʟᴏᴡ': 'Еллоу',
    '💙 ʙʟᴜᴇ': 'Блу',
    '💚 ɢʀᴇᴇɴ': 'Грин',
    '❤‍🩹 ʀᴇᴅ': 'Ред'
}

# Глобальные переменные для хранения состояния
current_rr_message = None
current_pd_message = None
list_type = None  # 'rr' или 'pd'
user_states = {}
rr_entries = []  # Список записей RR
pd_entries = {'house': [], 'garage': []}  # Записи PD по категориям

def create_server_keyboard():
    """Создает клавиатуру с серверами (4 колонки)"""
    keyboard = []
    row = []
    
    for i, (emoji, name) in enumerate(SERVERS.items()):
        btn = InlineKeyboardButton(emoji, callback_data=f"server_{name}")
        row.append(btn)
        
        if (i + 1) % 4 == 0:  # 4 кнопки в строке
            keyboard.append(row)
            row = []
    
    if row:  # Добавляем оставшиеся кнопки
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

def create_main_menu():
    """Создает главное меню"""
    keyboard = [
        [InlineKeyboardButton("📋 Заполнить RR лист", callback_data="fill_rr")],
        [InlineKeyboardButton("🏥 Заполнить PD лист", callback_data="fill_pd")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_pd_category_keyboard():
    """Создает клавиатуру выбора категории для PD"""
    keyboard = [
        [InlineKeyboardButton("🏠 Дома", callback_data="pd_house")],
        [InlineKeyboardButton("🚗 Гаражи", callback_data="pd_garage")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_time_keyboard(category):
    """Создает клавиатуру выбора времени в зависимости от категории"""
    if category == 'house':
        keyboard = [
            [
                InlineKeyboardButton("15:00", callback_data="time_15"),
                InlineKeyboardButton("17:00", callback_data="time_17")
            ],
            [
                InlineKeyboardButton("20:00", callback_data="time_20"),
                InlineKeyboardButton("22:00", callback_data="time_22")
            ]
        ]
    else:  # garage
        keyboard = [
            [
                InlineKeyboardButton("14:00", callback_data="time_14"),
                InlineKeyboardButton("16:00", callback_data="time_16")
            ],
            [
                InlineKeyboardButton("19:00", callback_data="time_19")
            ]
        ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = create_main_menu()
    await update.message.reply_text(
        "Привет! Это бот для автолистов кф \"Чёрная Россия\", выберите действие.",
        reply_markup=keyboard
    )

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
            await query.message.reply_text("Сообщение не найдено❌")
            return
        
        user_states[user_id] = {'type': 'rr', 'step': 'server'}
        keyboard = create_server_keyboard()
        await query.message.reply_text("Выберите сервер:", reply_markup=keyboard)
        
    elif data == "fill_pd":
        # Проверяем время для PD листа
        now = datetime.now(MOSCOW_TZ).time()
        if time(0, 0) <= now <= time(5, 0):
            await query.message.reply_text("Сообщение не найдено❌")
            return
        
        user_states[user_id] = {'type': 'pd', 'step': 'category'}
        keyboard = create_pd_category_keyboard()
        await query.message.reply_text("Привет, выбери категорию слета:", reply_markup=keyboard)
    
    elif data.startswith("pd_"):
        user_states[user_id]['step'] = 'time'
        user_states[user_id]['category'] = 'house' if 'house' in data else 'garage'
        
        keyboard = create_time_keyboard(user_states[user_id]['category'])
        await query.message.reply_text("Выберите время:", reply_markup=keyboard)
    
    elif data.startswith("time_"):
        user_states[user_id]['step'] = 'server'
        time_map = {
            '14': '14:00', '15': '15:00', '16': '16:00', 
            '17': '17:00', '19': '19:00', '20': '20:00', '22': '22:00'
        }
        user_states[user_id]['time'] = time_map[data.split('_')[1]]
        
        keyboard = create_server_keyboard()
        await query.message.reply_text("Отлично, укажите сервер:", reply_markup=keyboard)
    
    elif data.startswith("server_"):
        server_name = data.split('_', 1)[1]
        user_states[user_id]['server'] = server_name
        user_states[user_id]['step'] = 'description'
        
        await query.message.reply_text("Напишите что слетает:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.message.from_user.id
    
    if user_id not in user_states or user_states[user_id]['step'] != 'description':
        await update.message.reply_text("Используйте кнопки меню для начала работы.")
        return
    
    user_data = user_states[user_id]
    description = update.message.text
    
    # Формируем запись для добавления в лист
    if user_data['type'] == 'rr':
        entry = f"{user_data['server']} - {description}"
        rr_entries.append(entry)
        await update.message.reply_text(f"✅ Добавлено в RR лист:\n{entry}")
        
        # Обновляем сообщение в канале
        await update_rr_message(context)
    else:  # pd
        category_name = 'Дома' if user_data['category'] == 'house' else 'Гаражи'
        entry = f"{user_data['server']} - {user_data['time']} - {description}"
        pd_entries[user_data['category']].append(entry)
        await update.message.reply_text(f"✅ Добавлено в PD лист ({category_name}):\n{entry}")
        
        # Обновляем сообщение в канале
        await update_pd_message(context)
    
    # Очищаем состояние пользователя
    del user_states[user_id]

async def update_rr_message(context: ContextTypes.DEFAULT_TYPE):
    """Обновляет RR сообщение с текущими записями"""
    global current_rr_message
    if not current_rr_message:
        return
    
    try:
        # Создаём текст RR листа
        rr_text = "RR list by kf @kfblackrussia\n\n"
        
        # Группируем записи по серверам
        server_entries = {}
        for entry in rr_entries:
            if ' - ' in entry:
                server, desc = entry.split(' - ', 1)
                if server not in server_entries:
                    server_entries[server] = []
                server_entries[server].append(desc)
        
        # Добавляем все сервера
        for emoji, name in SERVERS.items():
            if name in server_entries:
                rr_text += f"{emoji} - {', '.join(server_entries[name])}\n"
            else:
                rr_text += f"{emoji} - \n"
        
        # Кнопка для перехода в бота
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("➕ Добавить слёт", url="https://t.me/kfblackrussia_bot")
        ]])
        
        await context.bot.edit_message_text(
            chat_id=current_rr_message['chat_id'],
            message_id=current_rr_message['message_id'],
            text=rr_text,
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении RR сообщения: {e}")

async def update_pd_message(context: ContextTypes.DEFAULT_TYPE):
    """Обновляет PD сообщение с текущими записями"""
    global current_pd_message
    if not current_pd_message:
        return
    
    try:
        # Создаём текст PD листа
        pd_text = "PD list by kf @kfblackrussia\n\n"
        
        # Дома
        pd_text += "🏠 House\n"
        for entry in pd_entries['house']:
            pd_text += f"• {entry}\n"
        if not pd_entries['house']:
            pd_text += "-\n"
        pd_text += "\n"
        
        # Гаражи
        pd_text += "🚗 Garage\n"
        for entry in pd_entries['garage']:
            pd_text += f"• {entry}\n"
        if not pd_entries['garage']:
            pd_text += "-\n"
            
        # Кнопка для перехода в бота
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("➕ Добавить слёт", url="https://t.me/kfblackrussia_bot")
        ]])
        
        await context.bot.edit_message_text(
            chat_id=current_pd_message['chat_id'],
            message_id=current_pd_message['message_id'],
            text=pd_text,
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении PD сообщения: {e}")

async def send_initial_message(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет начальное сообщение при запуске бота"""
    global current_rr_message, current_pd_message
    
    try:
        # Проверяем текущее время для определения типа листа
        now = datetime.now(MOSCOW_TZ).time()
        
        if time(0, 0) <= now <= time(5, 0):
            # Время для RR листа
            rr_text = "RR list by kf @kfblackrussia\n\n"
            for emoji, name in SERVERS.items():
                rr_text += f"{emoji} - \n"
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ Добавить слёт", url="https://t.me/kfblackrussia_bot")
            ]])
            
            message = await context.bot.send_message(CHAT_ID, rr_text, reply_markup=keyboard)
            current_rr_message = {
                'chat_id': CHAT_ID,
                'message_id': message.message_id
            }
            
        else:
            # Время для PD листа
            pd_text = "PD list by kf @kfblackrussia\n\n🏠 House\n-\n\n🚗 Garage\n-"
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ Добавить слёт", url="https://t.me/kfblackrussia_bot")
            ]])
            
            message = await context.bot.send_message(CHAT_ID, pd_text, reply_markup=keyboard)
            current_pd_message = {
                'chat_id': CHAT_ID,
                'message_id': message.message_id
            }
            
    except Exception as e:
        logging.error(f"Ошибка при отправке начального сообщения: {e}")

async def auto_post_messages(context: ContextTypes.DEFAULT_TYPE):
    """Автоматическая отправка сообщений по расписанию"""
    global current_rr_message, current_pd_message, rr_entries, pd_entries
    
    now = datetime.now(MOSCOW_TZ)
    current_time = now.time()
    
    try:
        # В 00:00 отправляем RR лист
        if current_time.hour == 0 and current_time.minute == 0:
            # Очищаем старые записи
            rr_entries.clear()
            
            # Создаем текст RR листа
            rr_text = "RR list by kf @kfblackrussia\n\n"
            for emoji, name in SERVERS.items():
                rr_text += f"{emoji} - \n"
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ Добавить слёт", url="https://t.me/kfblackrussia_bot")
            ]])
            
            # Удаляем старое сообщение если есть
            if current_rr_message:
                try:
                    await context.bot.delete_message(
                        chat_id=current_rr_message['chat_id'],
                        message_id=current_rr_message['message_id']
                    )
                except:
                    pass
            
            # Отправляем новое сообщение
            message = await context.bot.send_message(CHAT_ID, rr_text, reply_markup=keyboard)
            current_rr_message = {
                'chat_id': CHAT_ID,
                'message_id': message.message_id
            }
            
            logging.info("✅ Автоматически отправлен RR лист в 00:00")
        
        # В 5:01 отправляем PD лист  
        elif current_time.hour == 5 and current_time.minute == 1:
            # Очищаем старые записи
            pd_entries = {'house': [], 'garage': []}
            
            # Создаем текст PD листа
            pd_text = "PD list by kf @kfblackrussia\n\n🏠 House\n-\n\n🚗 Garage\n-"
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ Добавить слёт", url="https://t.me/kfblackrussia_bot")
            ]])
            
            # Удаляем старое сообщение если есть
            if current_pd_message:
                try:
                    await context.bot.delete_message(
                        chat_id=current_pd_message['chat_id'],
                        message_id=current_pd_message['message_id']
                    )
                except:
                    pass
            
            # Отправляем новое сообщение
            message = await context.bot.send_message(CHAT_ID, pd_text, reply_markup=keyboard)
            current_pd_message = {
                'chat_id': CHAT_ID,
                'message_id': message.message_id
            }
            
            logging.info("✅ Автоматически отправлен PD лист в 5:01")
            
    except Exception as e:
        logging.error(f"Ошибка при автоматической отправке сообщений: {e}")

async def background_time_checker(application: Application):
    """Фоновая задача для проверки времени"""
    while True:
        try:
            # Создаем контекст для вызова auto_post_messages
            async with application:
                await auto_post_messages(application)
            await asyncio.sleep(60)  # Проверяем каждую минуту
        except Exception as e:
            logging.error(f"Ошибка в фоновой задаче проверки времени: {e}")
            await asyncio.sleep(60)

async def health_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка здоровья бота"""
    await update.message.reply_text("✅ Бот работает исправно!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус бота"""
    status_text = f"""
🤖 Статус бота KF Black Russia

📊 Статистика:
• RR записей: {len(rr_entries)}
• PD домов: {len(pd_entries['house'])}
• PD гаражей: {len(pd_entries['garage'])}

⏰ Время МСК: {datetime.now(MOSCOW_TZ).strftime('%H:%M:%S')}
✅ Бот активен
"""
    await update.message.reply_text(status_text)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    error_msg = str(context.error)
    logging.error(f"Ошибка: {error_msg}", exc_info=context.error)

def main():
    """Основная функция"""
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
    application.add_handler(CommandHandler("health", health_check))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Задачи, которые выполняются после запуска
    async def post_init(application: Application):
        """Задачи после инициализации бота"""
        await send_initial_message(application)
        # Запускаем фоновую задачу для проверки времени
        asyncio.create_task(background_time_checker(application))
    
    # Привязываем post_init к приложению
    application.post_init = post_init
    
    # Всегда используем polling (работает надежно на Render)
    logging.info("🚀 Запуск в режиме polling...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

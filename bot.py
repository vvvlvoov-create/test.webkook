import os
import logging
from datetime import datetime, time, timedelta
import pytz
from dotenv import load_dotenv
import asyncio

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
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7719252121:AAEUyzzdo1JjYVfNv1uN_Y7PQFHR6de3T1o')
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

# Время постинга - ИСПРАВЛЕНО
PD_POST_TIME = time(5, 0, 0, tzinfo=MOSCOW_TZ)  # 05:00 МСК - PD лист
RR_POST_TIME = time(0, 0, 0, tzinfo=MOSCOW_TZ)  # 00:00 МСК - RR лист

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

Если бот не отвечает - проверьте время и выберите правильный тип листа.
    """
    
    keyboard = create_main_menu()
    await update.message.reply_text(help_text, reply_markup=keyboard)

async def format_rr_list():
    """Форматирует RR лист для постинга"""
    if not rr_entries:
        return "📋 RR Лист на сегодня пуст"
    
    # Группируем по серверам
    servers_data = {}
    for entry in rr_entries:
        server = entry['server']
        if server not in servers_data:
            servers_data[server] = []
        servers_data[server].append(entry)
    
    # Форматируем текст
    text = "🚨 <b>RR ЛИСТ</b> 🚨\n"
    text += "⏰ Время публикации: 00:00 МСК\n\n"
    
    for server, entries in servers_data.items():
        text += f"🎮 <b>{server}</b>:\n"
        for i, entry in enumerate(entries, 1):
            text += f"   {i}. {entry.get('description', 'Слёт')}\n"
        text += "\n"
    
    text += f"📊 Всего записей: {len(rr_entries)}"
    return text

async def format_pd_list():
    """Форматирует PD лист для постинга"""
    if not pd_entries:
        return "🏥 PD Лист на сегодня пуст"
    
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
    text = "🏥 <b>PD ЛИСТ</b> 🏥\n"
    text += "⏰ Время публикации: 05:00 МСК\n\n"
    
    # Дома
    if houses_data:
        text += "🏠 <b>ДОМА</b>:\n"
        for time_key in sorted(houses_data.keys()):
            text += f"   ⏰ <b>{time_key}</b>:\n"
            for server, entries in houses_data[time_key].items():
                text += f"      🎮 {server}: "
                descriptions = [entry.get('description', 'Слёт') for entry in entries]
                text += ", ".join(descriptions) + "\n"
            text += "\n"
    
    # Гаражи
    if garages_data:
        text += "🚗 <b>ГАРАЖИ</b>:\n"
        for time_key in sorted(garages_data.keys()):
            text += f"   ⏰ <b>{time_key}</b>:\n"
            for server, entries in garages_data[time_key].items():
                text += f"      🎮 {server}: "
                descriptions = [entry.get('description', 'Слёт') for entry in entries]
                text += ", ".join(descriptions) + "\n"
            text += "\n"
    
    text += f"📊 Всего записей: {len(pd_entries)}"
    return text

async def post_rr_list(context: ContextTypes.DEFAULT_TYPE):
    """Автопостинг RR листа в 00:00"""
    if rr_entries:
        rr_text = await format_rr_list()
        try:
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=rr_text,
                parse_mode='HTML'
            )
            logging.info("✅ RR лист опубликован в канал")
            rr_entries.clear()  # Очищаем после публикации
        except Exception as e:
            logging.error(f"❌ Ошибка отправки RR листа: {e}")
    else:
        logging.info("ℹ️ Нет записей для RR листа")

async def post_pd_list(context: ContextTypes.DEFAULT_TYPE):
    """Автопостинг PD листа в 05:00"""
    if pd_entries:
        pd_text = await format_pd_list()
        try:
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=pd_text,
                parse_mode='HTML'
            )
            logging.info("✅ PD лист опубликован в канал")
            pd_entries.clear()  # Очищаем после публикации
        except Exception as e:
            logging.error(f"❌ Ошибка отправки PD листа: {e}")
    else:
        logging.info("ℹ️ Нет записей для PD листа")

async def schedule_posts(application: Application):
    """Настройка расписания автопостинга"""
    job_queue = application.job_queue
    
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
    
    logging.info(f"📅 Расписание настроено: PD в {PD_POST_TIME}, RR в {RR_POST_TIME}")

async def view_lists_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает текущие собранные листы"""
    query = update.callback_query
    await query.answer()
    
    now = datetime.now(MOSCOW_TZ).time()
    
    if time(0, 0) <= now <= time(5, 0):
        # Время RR
        if rr_entries:
            rr_text = await format_rr_list()
            text = f"📋 <b>Текущий RR лист</b> (будет опубликован в 00:00):\n\n{rr_text}"
        else:
            text = "📋 RR лист пока пуст"
    else:
        # Время PD
        if pd_entries:
            pd_text = await format_pd_list()
            text = f"🏥 <b>Текущий PD лист</b> (будет опубликован в 05:00):\n\n{pd_text}"
        else:
            text = "🏥 PD лист пока пуст"
    
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
✅ Запись добавлена в RR лист!

Сервер: {server_name}
Тип: RR лист

📋 Запись будет опубликована в 00:00
Текущий RR лист:
{rr_text}
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
            
            pd_text = await format_pd_list()
            response_text = f"""
✅ Запись добавлена в PD лист!

Сервер: {server_name}
Категория: {category_name}
Время: {time_selected}

🏥 Запись будет опубликована в 05:00
Текущий PD лист:
{pd_text}
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
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    # Настраиваем расписание автопостинга
    asyncio.get_event_loop().run_until_complete(schedule_posts(application))
    
    # Запускаем в режиме polling
    logging.info("🚀 Запуск в режиме polling...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()

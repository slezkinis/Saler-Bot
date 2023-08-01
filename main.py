import telebot
from dotenv import load_dotenv
import os
from telebot import types
from db import SQL


db = SQL()
load_dotenv()
bot = telebot.TeleBot(os.environ['TG_TOKEN'])
creator_chat_id = os.environ['CREATOR_CHAT_ID']
payment_token = os.environ['PAYMENT_TOKEN']
add_section_val = False
admin = False
section = ''
add_new = ''
product = []


@bot.callback_query_handler(func=lambda c: 'set-adm_' in c.data)
def settings_section(message):
    global section
    bot.delete_message(message.message.chat.id, message.message.message_id)
    all_results = db.get_products_section(int(message.data.replace("set-adm_", "")))
    
    markup = types.InlineKeyboardMarkup()
    delete = types.InlineKeyboardButton('🗑️ Удалить эту категорию', callback_data=f'delete_category_{message.data.replace("set-adm_", "")}')
    add = types.InlineKeyboardButton('➕ Добавить товар в эту категорию', callback_data=f'add_product_in_{message.data.replace("set-adm_", "")}')
    markup.add(delete, add)
    for product in all_results:
        button1 = types.InlineKeyboardButton(product[1], callback_data=f'product_set_{product[0]}')
        markup.add(button1)
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    section = db.get_section(message.data.replace('set-adm_', ''))
    bot.send_message(message.message.chat.id, f'Это раздел для редактирования категории "{section[0]}"', reply_markup=markup)
    bot.answer_callback_query(message.id)

    
@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and m.text == '⚙️ Настройка магазина')
def admin_func(message):
    global admin
    admin = True
    markup = types.InlineKeyboardMarkup()
    sections = db.get_all_sections()
    new = types.InlineKeyboardButton('✏️ Добавить новую категорию', callback_data='new_section')
    markup.add(new)
    for section in sections:
        b1 = types.InlineKeyboardButton(section[0], callback_data=f'set-adm_{section[1]}')
        markup.add(b1)
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.chat.id, 'Это настройка магазина! Вот все категории', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'new_section')
def add_section(message):
    global add_section_val
    bot.delete_message(message.message.chat.id, message.message.message_id)
    add_section_val = True
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_section')
    markup.add(cancel)
    bot.send_message(message.message.chat.id, 'Напишите название для новой категории', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'product_set_' in c.data)
def delete_product(message):
    markup = types.InlineKeyboardMarkup()
    product = db.get_info_about_product(message.data.replace("product_set_", ""))
    bot.delete_message(message.message.chat.id, message.message.message_id)
    yes = types.InlineKeyboardButton('✅', callback_data=f'yes_product_{message.data.replace("product_set_", "")}')
    no = types.InlineKeyboardButton('❌', callback_data=f'no_product_{message.data.replace("product_set_", "")}')
    markup.add(yes, no)
    bot.send_message(message.message.chat.id, f'Вы уверены, что хотите удалить товар "{product[1]}', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'yes_product_' in c.data)
def delete(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    global admin
    admin = False
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    product = db.get_info_about_product(message.data.replace("yes_product_", ""))
    os.remove(product[7])
    db.delete_product(message.data.replace("yes_product_", ""))
    users = db.get_all_users()
    for user in users:
        buy = user[2].split('; ')
        if f'{message.data.replace("yes_product_", "")}' in buy:
            buy.remove(f'{message.data.replace("yes_product_", "")}')
        db.update_user('; '.join(buy), user[0])
    bot.send_message(message.message.chat.id, f'Товар "{product[1]}" удалён!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'no_product_' in c.data)
def cancel_delete(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    global admin
    admin = False
    product = db.get_info_about_product(message.data.replace("no_product_", ""))
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    bot.send_message(message.message.chat.id, f'Товар "{product[1]}" не удалён!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'delete_category_' in c.data)
def delete_category(message):
    markup = types.InlineKeyboardMarkup()
    bot.delete_message(message.message.chat.id, message.message.message_id)
    category = db.get_section(message.data.replace("delete_category_", ""))
    yes = types.InlineKeyboardButton('✅', callback_data=f'yes_category_{message.data.replace("delete_category_", "")}')
    no = types.InlineKeyboardButton('❌', callback_data=f'no_category_{message.data.replace("delete_category_", "")}')
    markup.add(yes, no)
    bot.send_message(message.message.chat.id, f'Вы уверены, что хотите удалить категорию "{category[0]} вместе со всеми принадлежащими ей товарами?', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'cancel_product' in c.data)
def cancel_product(message):
    global add_new, product
    add_new = ''
    product = []
    bot.delete_message(message.message.chat.id, message.message.message_id)
    global admin
    admin = True
    markup = types.InlineKeyboardMarkup()
    sections = db.get_all_sections()
    new = types.InlineKeyboardButton('✏️ Добавить новую категорию', callback_data='new_section')
    markup.add(new)
    for section in sections:
        b1 = types.InlineKeyboardButton(section[0], callback_data=f'set-adm_{section[1]}')
        markup.add(b1)
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.message.chat.id, 'Это настройка магазина! Вот все категории', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'add_product_in_' in c.data)
def add_new_product(message):
    global add_new, product
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    bot.delete_message(message.message.chat.id, message.message.message_id)
    add_new = f'Название_{message.data.replace("add_product_in_", "")}'
    bot.send_message(message.message.chat.id, 'Напишите название товара', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and "Название_" in add_new)
def name(message):
    global add_new, product
    # bot.delete_message(message.chat.id, message.message_id)
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    add_new = f'Описание_{add_new.replace("Название_", "")}'
    product.append(message.text)
    bot.send_message(message.chat.id, 'Напишите описание товара', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'Описание_' in add_new)
def description(message):
    global add_new, product
    add_new = f'Ссылка_{add_new.replace("Описание_", "")}'
    # bot.delete_message(message.chat.id, message.message_id)
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    product.append(message.text)
    bot.send_message(message.chat.id, 'Напишите ссылку на курс', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'Ссылка_' in add_new)
def link(message):
    global add_new, product
    add_new = f'C_Цена_{add_new.replace("Ссылка_", "")}'
    # bot.delete_message(message.chat.id, message.message_id)
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    product.append(message.text)
    bot.send_message(message.chat.id, 'Напишите старую цену на курс (в рублях)', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'C_Цена_' in add_new)
def old_price(message):
    global add_new, product
    add_new = f'Н_Цена_{add_new.replace("C_Цена_", "")}'
    # bot.delete_message(message.chat.id, message.message_id)
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    product.append(message.text)
    bot.send_message(message.chat.id, 'Напишите новую цену на курс (в рублях)', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'Н_Цена_' in add_new)
def new_price(message):
    global add_new, product
    # bot.delete_message(message.chat.id, message.message_id)
    add_new = f'Image_{add_new.replace("Н_Цена_", "")}'
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    product.append(int(message.text))
    product.append(add_new.replace('Image_', ''))
    bot.send_message(message.chat.id, 'Отправьте картинку для курса', reply_markup=markup)


@bot.message_handler(content_types=['photo'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'Image_' in add_new)
def image(message):
    global add_new, product
    markup = types.InlineKeyboardMarkup()
    # bot.delete_message(message.chat.id, message.message_id)
    yes = types.InlineKeyboardButton('✅', callback_data=f'add')
    no = types.InlineKeyboardButton('❌', callback_data=f'not_add')
    markup.add(yes, no)
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = f'./images/{product[0]}.jpg'
    product.append(src)
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    add_new = 'Ок'
    bot.send_message(message.chat.id, f'Название: {product[0]}\nОписание: {product[1]}\nСсылка: {product[2]}\nСтарая цена: {product[3]} руб.\nНовая цена: {product[4]} руб.', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'Ок' in add_new)
def ok(message):
    global add_new, product, admin
    add_new = ''
    bot.delete_message(message.message.chat.id, message.message.message_id)
    admin = False
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    if message.data == 'add':
        db.add_product(product)
        bot.send_message(message.message.chat.id, 'Товар добавлен!', reply_markup=markup)
        product = []
    else:
        bot.send_message(message.message.chat.id, 'Товар не добавлен!', reply_markup=markup)
        product = []
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'yes_category_' in c.data)
def delete_category(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    name = db.get_section(str(message.data).replace('yes_category_', ''))
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    db.delete_section(name[1])
    all_results = db.get_products_section(name[1])
    count = 0
    for product in all_results:
        users = db.get_all_users()
        for user in users:
            buy = user[2].split('; ')
            if product[0] in buy:
                buy.remove(product[0])
            db.update_user('; '.join(buy), user[0])
        db.delete_product(product[0])
        count += 1
    bot.send_message(message.message.chat.id, f'Удалена категория "{name[0]} и {count} шт товаров!', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'no_category_' in c.data)
def delete_category(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    bot.send_message(message.message.chat.id, f'Удаление категории отменено', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and add_section_val)
def correct_section(message):
    db.create_section(message.text)
    markup = types.InlineKeyboardMarkup()
    global add_section_val
    add_section_val = False
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    bot.send_message(message.chat.id, f'Создана новая категория с именем {message.text}!', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    all_results = db.get_all_users()
    all_users = [i[0] for i in all_results]
    if message.chat.id not in all_users:
        if len(message.text.split(' ')) == 2:
            markup = types.InlineKeyboardMarkup()
            close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
            markup.add(close)
            ref_chat_id = message.text.split(' ')[1]
            user = db.get_user(ref_chat_id)
            bot.send_message(message.chat.id, f'Хэй! Тебя пригласил {user[1]}! Поздравляю, в честь этого тебе начисленно 10 бонусных рублей 💸. Ты можешь их потратить на плкупку товаров в этом магазине!', reply_markup=markup)
            db.add_user((message.chat.id, message.chat.username, '', 10, ref_chat_id))
        else:
            db.add_user((message.chat.id, message.chat.username, '', 0, -1))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    shop = types.KeyboardButton('🛒 Товары')
    not_pay = types.KeyboardButton('❗️Акция❗️')
    profile = types.KeyboardButton('📱 Профиль')
    ref = types.KeyboardButton('💸 Реферальная система')
    markup.add(shop, not_pay, profile, ref)
    if str(message.chat.id) == str(creator_chat_id):
        admin1 = types.KeyboardButton('⚙️ Настройка магазина')
        markup.add(admin1)
    bot.send_message(message.chat.id, 'Привет! Добро пожаловать в онлайн магазин', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '💸 Реферальная система')
def ref_system(message):
    ch = 0
    all_users = db.get_all_users()
    for user in all_users:
        if user[4] == message.chat.id:
            ch += 1
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    link = f't.me/{bot.user.username}?start={message.chat.id}'
    bot.send_message(message.chat.id, f'У нас в магазине действует реферальная система. Если ты пригласишь друга, то он получит десять бонусных рублей. А если он что-то купит у нас, то ты получишь 50 бонусных рублей, которые сможешь потратить на наши товары.\nЭто твоя персональная ссылка: {link}\nСейчас по ней зарегестрировалось вот столько пользователей: {ch}', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '❗️Акция❗️')
def not_pay(message):
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton('💳 Купить за 1499 руб', callback_data='sale')
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(ok, close)
    bot.send_message(message.chat.id, 'Внимание❗️ Вы можете получить все товары за 1499 руб❗️ Скорее покупайте и наслаждайтесь', reply_markup=markup)


@bot.callback_query_handler(func=lambda m:m.data == 'sale')
def sale(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    prices = []
    user = db.get_user(message.message.chat.id)
    users_buy = user[2].split('; ')
    if '' in users_buy:
        users_buy.remove('')
    all_results = db.get_info()
    for product in all_results:
        if str(product[0]) not in users_buy:
            price = types.LabeledPrice(label=f'Доступ к курсу "{product[1]}"', amount=int(product[4]) * 100)
            prices.append(price)
    if prices:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(f"Заплатить", pay=True))
        keyboard.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
        prices = [types.LabeledPrice(label=f'Доступ ко всем товарам', amount=149900)]
        bot.send_invoice(
            message.message.chat.id,
            'Доступ',
            f'Доступ ко всем товарам', is_flexible=False, prices=prices, provider_token=payment_token, currency="rub", invoice_payload='sale', reply_markup=keyboard, )
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
        bot.send_message(message.message.chat.id, f'Вы уже купили все товары в этом боте!\nСсылка: https://disk.yandex.ru/d/fJttnVQnkrmpMA', reply_markup=markup)
    bot.answer_callback_query(message.id)
    


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '🛒 Товары')
def shop(message):
    all_results = db.get_all_users()
    all_users = [i[0] for i in all_results]
    if message.chat.id not in all_users:
        db.add_user((message.chat.id, message.chat.username, '', 0, -1))
    all_results = db.get_all_sections()
    markup = types.InlineKeyboardMarkup()
    for product in all_results:
        button1 = types.InlineKeyboardButton(product[0], callback_data=f'category_{product[1]}')
        markup.add(button1)
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.chat.id, 'Вот список категорий', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '📱 Профиль')
def profile(message):
    all_results = db.get_all_users()
    all_users = [i[0] for i in all_results]
    if message.chat.id not in all_users:
       db.add_user((message.chat.id, message.chat.username, '', 0, -1))
    user = db.get_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    name = message.chat.first_name
    count = 0
    count_products = 0
    users_buy = user[2].split('; ')
    if '' in users_buy:
        users_buy.remove('')
    for product_name in users_buy:
        product = db.get_info_about_product(product_name)
        count += product[4]
        count_products += 1
    if not name:
        name = 'Не указано'
    text = f'🙍‍♂ Пользователь: {message.chat.first_name}\n🆔 ID: {message.chat.id}\n------------------\n🛒 Количество покупок: {count_products} шт.\n💰 Общая сумма: {count} руб.'
    bot.send_message(message.chat.id, text, reply_markup=markup)
    

@bot.message_handler(commands=['add'], func=lambda c: str(c.chat.id) == str(creator_chat_id))
def add(message):
    text = message.text.split()
    if not text[1]:
        bot.send_message(message.chat.id, 'Проверьте, указали ли Вы ID человека!')
        return
    user = db.get_user(int(text[1]))
    if not user:
        bot.send_message(message.chat.id, 'Пользователь с таким ID в базе данных не найден!')
    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton('✅', callback_data=f'ok_{text[1]}')
    no = types.InlineKeyboardButton('❌', callback_data=f'not_{text[1]}')
    markup.add(yes, no)
    bot.send_message(message.chat.id, f'Вы уверены, что хотите выдать пользователю с ID {text[1]} все товары?', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'ok_' in c.data)
def add_t(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    all_results = db.get_info()
    products = [i[0] for i in all_results]
    db.update_user('; '.join(products), message.data.replace('ok_', ''))
    bot.send_message(message.message.chat.id, f'Пользователю с ID {message.data.replace("ok_", "")} выдано {len(products)} шт товаров!', reply_markup=markup)
    bot.answer_callback_query(message.id)
    bot.send_message(message.data.replace('ok_', ''), '❗️Вам выдали доступ ко всем курсам! Поздравляем!❗️', reply_markup=markup)
    

@bot.callback_query_handler(func=lambda c: 'not_' in c.data)
def add_t(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.message.chat.id, f'Операция отменена!', reply_markup=markup)
    bot.answer_callback_query(message.id)


def check_sections(message):
    all_results = db.get_all_sections()
    data = [str(product[1]) for product in all_results]
    if message.data.replace('category_', '') in data and 'category_' in message.data:
        return True
    else:
        return False


def check_products(message):
    all_results = db.get_info()
    data = [str(product[0]) for product in all_results]
    if message.data.replace('product_', '') in data and 'product_' in message.data:
        return True
    else:
        return False


@bot.callback_query_handler(func=check_sections)
def inlin_sections(message):
    section = db.get_section(int(message.data.replace('category_', '')))
    all_results = db.get_products_section(section[1])
    markup = types.InlineKeyboardMarkup(row_width=1)
    count = 0
    buttons = []
    # buy_all = types.InlineKeyboardButton('💳 Купить всю категорию', callback_data=f'cat_{message.data.replace("category_", "")}')
    # markup.add(buy_all)
    for product in all_results:
        button1 = types.InlineKeyboardButton(product[1], callback_data=f'product_{product[0]}')
        buttons.append(button1)
        if count == 2:
            for j in buttons:
                markup.add(j)
            count = 0
            buttons = []
        else:
            count += 1
    for j in buttons:
        markup.add(j)
    button1 = types.InlineKeyboardButton("Назад 🔙", callback_data="home")
    markup.add(button1)
    bot.delete_message(message.message.chat.id, message.message.message_id)
    bot.send_message(message.message.chat.id, f'Товары из категории "{section[0]}" ⬇️', reply_markup=markup)
    bot.answer_callback_query(message.id)


# @bot.callback_query_handler(func=lambda c: 'cat_' in c.data)
# def buy_category(message):
#     bot.delete_message(message.message.chat.id, message.message.message_id)
#     prices = []
#     user = db.get_user(message.message.chat.id)
#     users_buy = user[2].split('; ')
#     if '' in users_buy:
#         users_buy.remove('')
#     section = db.get_section(message.data.replace('cat_', ''))
#     all_results = db.get_products_section(message.data.replace('cat_', ''))
#     data = [str(i[0]) for i in all_results]
#     links = []
#     for product in all_results:
#         if str(product[0]) not in users_buy:
#             price = types.LabeledPrice(label=f'Доступ к курсу "{product[1]}"', amount=int(product[4]) * 100)
#             prices.append(price)
#         links.append(f'Название: {product[0]}\nОписание: {product[1]}\nЦена: {product[3]} руб.\nСсылка на курс "{product[0]}": {product[2]}\n\n')
#     links = "\n".join(links)
#     markup = types.InlineKeyboardMarkup()
#     button1 = types.InlineKeyboardButton("Назад к категории 🔙", callback_data=f'category_{product[5]}')
#     markup.add(button1)
#     if prices:
#         keyboard = types.InlineKeyboardMarkup()
#         keyboard.add(types.InlineKeyboardButton(f"Заплатить", pay=True))
#         keyboard.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
#         bot.send_invoice(
#             message.message.chat.id,
#             'Доступ',
#             f'Доступ к категории "{section[0]}', is_flexible=False, prices=prices, provider_token=payment_token, currency="rub", invoice_payload='; '.join(data), reply_markup=keyboard, )
#     else:
#         bot.send_message(message.message.chat.id, f'Вы уже купили все товары из этой категории\n{links}', reply_markup=markup)

@bot.callback_query_handler(func=check_products)
def inlin_product(message):
    markup = types.InlineKeyboardMarkup()
    product = db.get_info_about_product(message.data.replace('product_', ''))
    with open(product[7], 'rb') as file:
        image = file.read()
    buy_products = db.get_user(message.message.chat.id)[2].split('; ')
    if str(product[0]) not in buy_products:
        buy = types.InlineKeyboardButton("Купить 💳", callback_data=f"{product[0]}_buy")
    else:
        buy = types.InlineKeyboardButton("Отправить ссылку", callback_data=f"{product[0]}_buy")
    button1 = types.InlineKeyboardButton("Назад к категории 🔙", callback_data=f'category_{product[6]}')
    markup.add(buy, button1)
    bot.delete_message(message.message.chat.id, message.message.message_id)
    bot.send_photo(message.message.chat.id, image, f"Название: {product[1]}\nОписание: {product[2]}\nЦена: ~{product[4]} руб~    *{product[5]} руб*", reply_markup=markup, parse_mode='MarkdownV2')
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c:True)
def inlin(message):
    # data = message.message.json['reply_markup']['inline_keyboard'][0][0]['callback_data']
    if message.data == 'close':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.answer_callback_query(message.id)
    if message.data == 'home':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        all_results = db.get_all_sections()
        markup = types.InlineKeyboardMarkup()
        for product in all_results:
            button1 = types.InlineKeyboardButton(product[0], callback_data=f'category_{product[1]}')
            markup.add(button1)
        close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
        markup.add(close)
        bot.send_message(message.message.chat.id, 'Вот список категорий', reply_markup=markup)
        bot.answer_callback_query(message.id)
    if message.data == 'cancel_section':
        global add_section_val
        add_section_val = False
        bot.delete_message(message.message.chat.id, message.message.message_id)
        global admin
        admin = True
        markup = types.InlineKeyboardMarkup()
        sections = db.get_all_sections()
        new = types.InlineKeyboardButton('✏️ Добавить новую категорию', callback_data='new_section')
        markup.add(new)
        for section in sections:
            b1 = types.InlineKeyboardButton(section[0], callback_data=f'set-adm_{section[1]}')
            markup.add(b1)
        close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
        markup.add(close)
        bot.send_message(message.message.chat.id, 'Это настройка магазина! Вот все категории', reply_markup=markup)
    if '_buy' in message.data:
        data = message.message.json['reply_markup']['inline_keyboard'][0][0]['callback_data'].replace('_buy', '')
        product = db.get_info_about_product(message.data.replace('_buy', ''))
        buy_products = db.get_user(message.message.chat.id)[2].split('; ')
        if data not in buy_products:
            price = types.LabeledPrice(label=f'Доступ к курсу "{product[1]}"', amount=int(product[4]) * 100)
            bot.delete_message(message.message.chat.id, message.message.message_id)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(f"💲Заплатить", pay=True))
            keyboard.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.send_invoice(
                message.message.chat.id,
                product[1],
                f'Доступ к курсу "{product[1]}"', is_flexible=False, prices=[price], provider_token=payment_token, currency="rub", invoice_payload=product[0], reply_markup=keyboard)
        else:
            markup = types.InlineKeyboardMarkup()
            section = types.InlineKeyboardButton('Обратно к категории 🔙', callback_data=f'category_{product[4]}')
            home = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
            markup.add(section, home)
            bot.delete_message(message.message.chat.id, message.message.message_id)
            bot.send_message(message.message.chat.id, f'Вы уже купили этот курс! Вот ссылка: {product[3]}', reply_markup=markup)
        bot.answer_callback_query(message.id)


@bot.pre_checkout_query_handler(lambda h: True)
def good(message):
    bot.answer_pre_checkout_query(message.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def good(message):
    if message.successful_payment.invoice_payload != 'sale':
        bot.delete_message(message.chat.id, message.message_id)
        product = db.get_info_about_product(message.successful_payment.invoice_payload.split('; ')[0])
        markup = types.InlineKeyboardMarkup()
        section = types.InlineKeyboardButton('Обратно к категории 🔙', callback_data=f'category_{str(product[5])}')
        home = types.InlineKeyboardButton("На главный экран 🏠", callback_data="close")
        links = []
        markup.add(section, home)
        for i in message.successful_payment.invoice_payload.split('; '):
            product = db.get_info_about_product(i)
            buy_products = db.get_user(message.chat.id)[2].split('; ')
            buy_products.append(str(product[0]))
            if '' in buy_products:
                buy_products.remove('')
            db.update_user('; '.join(buy_products), message.chat.id)
            links.append(f'Название: {product[1]}\nОписание: {product[2]}\nЦена: {product[4]} руб.\nСсылка на курс "{product[1]}": {product[3]}\n\n')
        links = "\n".join(links)
        bot.send_message(message.chat.id, f'Спасибо за покупку!\n{links}', reply_markup=markup)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        markup = types.InlineKeyboardMarkup()
        home = types.InlineKeyboardButton("🚫 Закрыть", callback_data="close")
        links = []
        for product in db.get_info():
            buy_products = db.get_user(message.chat.id)[2].split('; ')
            if str(product[0]) not in buy_products:
                buy_products.append(str(product[0]))
            if '' in buy_products:
                buy_products.remove('')
            db.update_user('; '.join(buy_products), message.chat.id)
        markup.add(home)
        bot.send_message(message.chat.id, 'Спасибо за покупку всех товаров!\nСсылка: https://disk.yandex.ru/d/fJttnVQnkrmpMA', reply_markup=markup)

bot.infinity_polling(skip_pending = True)

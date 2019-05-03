from app import bot, Database, parser, config
import telebot


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Пожалуйста, представься:')
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    with Database() as db:
        db.add_user(message.chat.id, message.text)
    bot.send_message(message.chat.id, 'Привет, ' + message.text + '!')


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, '/search - поиск фильма')


@bot.message_handler(commands=['search'])
def handle_search(message):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    key_author = telebot.types.KeyboardButton(text='По режиссёру')
    keyboard.add(key_author)
    key_genre = telebot.types.KeyboardButton(text='По жанру')
    keyboard.add(key_genre)
    key_auto = telebot.types.KeyboardButton(text='Автоматически')
    keyboard.add(key_auto)
    bot.send_message(message.chat.id, 'Выбери тип поиска:',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, get_search_type)


def get_search_type(message):
    message_texts = {'По режиссёру': 'Введи имя режиссера:',
                     'По жанру': 'Введи желаемый жанр:'}
    handlers = {'По режиссёру': handle_author_name,
                'По жанру': handle_genre}
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    if message.text in message_texts:
        bot.send_message(message.chat.id, message_texts[message.text],
                         reply_markup=markup)
        bot.register_next_step_handler(message, handlers[message.text])
    else:
        handle_all(message, markup)


def obtain_films_list(message, films_list):
    if not films_list:
        bot.send_message(message.chat.id, 'Что-то пошло не так. '
                                          'Попробуй позже')
        return
    with Database() as db:
        db.clear_search_data(message.chat.id)
        db.insert_search_data(message.chat.id, films_list)
    keyboard = telebot.types.InlineKeyboardMarkup(4)
    key_back = telebot.types.InlineKeyboardButton('⬅', callback_data='back')
    key_fwd = telebot.types.InlineKeyboardButton('➡', callback_data='fwd')
    key_like = telebot.types.InlineKeyboardButton('👍', callback_data='like')
    key_dis = telebot.types.InlineKeyboardButton('👎', callback_data='dis')
    keyboard.add(key_back, key_fwd, key_like, key_dis)
    msg = 'Фильм: {}\nРейтинг: {}/10'. \
        format(films_list[0][0], films_list[0][1])
    bot.send_message(message.chat.id, text=msg, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def buttons_callback(call):
    with Database() as db:
        cur_pos = db.get_cur_search_pos(call.message.chat.id)
        search_data = db.get_search_data(call.message.chat.id)
    new_pos = cur_pos
    if call.data == 'back':
        if cur_pos >= 1:
            new_pos -= 1
    elif call.data == 'fwd':
        if cur_pos < len(search_data) - 1:
            new_pos += 1
    if new_pos != cur_pos:
        with Database() as db:
            db.change_cur_search_pos(call.message.chat.id, new_pos)
        keyboard = telebot.types.InlineKeyboardMarkup(4)
        key_back = telebot.types.InlineKeyboardButton('⬅', callback_data='back')
        key_fwd = telebot.types.InlineKeyboardButton('➡', callback_data='fwd')
        key_like = telebot.types.InlineKeyboardButton('👍', callback_data='like')
        key_dis = telebot.types.InlineKeyboardButton('👎', callback_data='dis')
        keyboard.add(key_back, key_fwd, key_like, key_dis)
        msg = 'Фильм: {}\nРейтинг: {}/10'.\
            format(search_data[new_pos][0], search_data[new_pos][1])
        bot.edit_message_text(msg, call.message.chat.id,
                              call.message.message_id, reply_markup=keyboard)


def handle_author_name(message):
    id = parser.get_man_id_by_name(message.text)
    if id is not None:
        films_list = parser.get_film_list_by_director_id(id)
        obtain_films_list(message, films_list)
    else:
        bot.send_message(message.chat.id, 'Такой режиссёр не найден')


def handle_genre(message):
    genre = message.text.lower()
    if genre not in config['genre_codes']:
        bot.send_message(message.chat.id, 'Такой жанр не найден')
    else:
        code = config['genre_codes'][genre]
        films_list = parser.get_film_list_by_genre(code)
        obtain_films_list(message, films_list)


@bot.message_handler()
def handle_all(message, markup=None):
    bot.send_message(message.chat.id, 'Не знаю, как ответить.\n'
                                      'Попробуй написать /help',
                     reply_markup=markup)
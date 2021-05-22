import telebot
from telebot import types
import config
from App import App

bot = telebot.TeleBot(config.TOKEN)
app = App(bot)


@bot.message_handler(content_types=['text'])
def use_the_latter(message):
    if message.text == 'Use the latter':
        app.use_the_latter(message.chat.id, True)
        bot.send_message(message.chat.id, 'The latter used', reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, 'Что мне сделать с твоей фоткой?', reply_markup=app.markup)


@bot.message_handler(content_types=['photo'])
def images(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        file_path = file_info.file_path
        chat = message.chat.id

        app.add(chat, file_path)
    except Exception as e:
        print(repr(e))

    try:
        markup = app.markup
        bot.send_message(message.chat.id, 'Фотография получена', reply_markup=types.ReplyKeyboardRemove())
        app.use_the_latter(message.chat.id, False)
        bot.send_message(message.chat.id, 'Что мне сделать с твоей фоткой?', reply_markup=markup)
    except Exception as e:
        print(repr(e))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data in app.funcs.keys():
                photo = app.change(call.data, call.message.chat.id)
                app.add_last_send(call.message.chat.id, photo)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button = types.KeyboardButton('Use the latter')
                markup.add(button)
                bot.send_photo(call.message.chat.id, photo, reply_markup=markup)
    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)

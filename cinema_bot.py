import app

if __name__ == '__main__':
    bot = app.bot
    bot.polling(none_stop=True, interval=1)

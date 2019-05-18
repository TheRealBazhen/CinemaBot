import json
import telebot

with open('app/bin/config.json', 'rt', encoding='utf-8') as f:
    config = json.load(f)

bot = telebot.TeleBot(config['bot']['token'])

from app.db.db import Database
from app.web_utils import parser
from app.bot_utils import handlers

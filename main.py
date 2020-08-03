import os
import sys
import logging

from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackQueryHandler, InlineQueryHandler, TypeHandler
from telegram import TelegramObject

import commands

mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.info("Bot launched")
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Before all handlers
    dispatcher.add_handler(TypeHandler(TelegramObject, commands.check_database), group=0)

    # Inline Handler
    dispatcher.add_handler(InlineQueryHandler(commands.inline_status), group=1)

    # Commands Handlers
    dispatcher.add_handler(CommandHandler('start', commands.cmd_start), group=2)
    dispatcher.add_handler(CommandHandler('status', commands.cmd_status), group=2)
    dispatcher.add_handler(CommandHandler('players', commands.cmd_players), group=2)

    # Message Handler
    dispatcher.add_handler(MessageHandler(None, commands.message), group=2)

    # CallBack Handlers
    dispatcher.add_handler(CallbackQueryHandler(commands.cb_status, pattern='pattern_status'), group=3)
    dispatcher.add_handler(CallbackQueryHandler(commands.cb_players, pattern='pattern_players'), group=3)
    dispatcher.add_handler(CallbackQueryHandler(commands.cb_about, pattern='pattern_about'), group=3)

    dispatcher.add_error_handler(commands.error_handler)

    if mode == "dev":
        updater.start_polling()
    elif mode == "prod":
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
    else:
        logging.error("No MODE specified!")
        sys.exit(1)

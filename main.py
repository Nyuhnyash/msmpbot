import logging
import commands
import os
import sys
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackQueryHandler, InlineQueryHandler, PicklePersistence, ConversationHandler
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.info("Bot launched")
    my_persistence = PicklePersistence(filename='persistent_data')

    updater = Updater(TOKEN, persistence=my_persistence, use_context=True)
    dispatcher = updater.dispatcher

    # Inline Handler
    dispatcher.add_handler(InlineQueryHandler(commands.inline_status))

    # Commands Handlers
    dispatcher.add_handler(CommandHandler('start', commands.cmd_start))
    dispatcher.add_handler(CommandHandler('status', commands.cmd_status))
    dispatcher.add_handler(CommandHandler('players', commands.cmd_players))

    # Message Handler
    dispatcher.add_handler(MessageHandler(None, commands.message))

    # CallBack Handlers
    dispatcher.add_handler(CallbackQueryHandler(commands.cb_status, pattern='pattern_status'))
    dispatcher.add_handler(CallbackQueryHandler(commands.cb_players, pattern='pattern_players'))
    dispatcher.add_handler(CallbackQueryHandler(commands.cb_about, pattern='pattern_about'))

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

# pylint: disable=unused-wildcard-import

from telegram import *
import logging
from mcstatus import MinecraftServer

from telegram.ext.dispatcher import run_async
from telegram.ext import CallbackContext

from utils import *
from replies import error, info, reply_markup

from socket import timeout as TimeoutError

import db
import inspect

logging.basicConfig(
                    handlers=(
                              logging.FileHandler('command_logs.log'),
                              logging.StreamHandler()),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

welcome_text = """
༼ つ ◕ ◡ ◕ ༽つ\nСервис для отслеживания Колбасного сервера

Чтобы узнать список игроков на сервере введите @msmpbot <любой запрос> в строке ввода текста в любом чате Telegram. 

Команды:
/status - информация о сервере
/players - игроки онлайн на сервере

Если вы хотите изменить отслеживаемый сервер, отправьте мне его IP-адрес."""

# ==========================
# Inline Query Handler
# ==========================

@run_async
def inline_status(update: Update, context: CallbackContext):
    logging.info("inline request from " + name_and_id(update.inline_query))

    user_data = context.user_data
    try: 
        user_data['url'] = db.get(update.inline_query)
        
        q = list()

        q.append(InlineQueryResultArticle(
            id='1', title='IP: ' + user_data['url'],
            input_message_content=InputTextMessageContent(
            message_text='IP: ' + user_data['url']))
            )
        server = MinecraftServer.lookup(user_data['url'])
        status = server.status()
        online = status.players.online
        if online < 32:
            query = server.query()
            players = query.players.names
            str_players = str(", ".join(players))
            descr = str_players
        else:
            descr = ""
        end = ending(online)

        q.append(InlineQueryResultArticle(
            id='2', title='{0} игрок{1} онлайн'.format(online, end),
            description=descr,
            input_message_content=InputTextMessageContent(
            message_text='{0} игрок{1} онлайн: {2}'.format(online, end, descr)))
            )

        context.bot.answer_inline_query(update.inline_query.id, q, cache_time=60)
        logging.info("inline answer sent")
        return

    except TimeoutError:
        logging.error("Timeout error ({})".format(inspect.stack()[0][3]))
    except Exception as e:
        logging.exception(e)

    error.status_inline(context.bot, update.inline_query.id)

# ==========================
# Message Handler
# ==========================

@run_async
def message(update: Update, context: CallbackContext):
    """Usage: <IP-address> """
    text = update.message.text
    logging.info(text + " recieved from " + name_and_id(update.message))

    user_data = context.user_data
    try: 
        
        if text=="default":
            text = db.default_url
        if not validUrl(text):
            logging.info("Invalid URL, too long")
            return
        user_data['url'] = text
        db.set(update.message, text)

        context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        context.bot.send_message(update.message.chat_id, text="Адрес сервера изменён на "+user_data['url'], parse_mode=ParseMode.MARKDOWN)
        return

    except Exception as e:
        logging.exception(e)

# ==========================
# Commands
# ==========================

@run_async
def cmd_start(update: Update, context: CallbackContext):
    """Usage: /start"""
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.message))
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    
    context.bot.send_message(update.message.chat_id, text=welcome_text, parse_mode=ParseMode.MARKDOWN)

@run_async
def cmd_status(update: Update, context: CallbackContext):
    """Usage: /status url"""
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.message))
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    user_data = context.user_data
    user_data['url'] = db.get(update.message)

    try:

        user_data['server'] = MinecraftServer.lookup(user_data['url'])
        user_data['status'] = user_data['server'].status()

        info.status(context.bot, update.message.chat_id, user_data['url'], user_data['status'])
        logging.info("/status %s online" % user_data['url'])
        return
        
    except TimeoutError:
        logging.error("Timeout error ({})".format(inspect.stack()[0][3]))
    except Exception as e:
        logging.exception(e)

    error.status(context.bot, update.message.chat_id, user_data['url'])
        


@run_async
def cmd_players(update: Update, context: CallbackContext):
    """Usage: /players url"""
    
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.message))
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    user_data = context.user_data
    user_data['url'] = db.get(update.message)
    try:
        
        user_data['url'] = db.get(update.message)

        user_data['server'] = MinecraftServer.lookup(user_data['url'])
        user_data['status'] = user_data['server'].status()
        if user_data['status'].players.online < 32:
            user_data['query'] = user_data['server'].query()
            info.players(context.bot, update.message.chat_id, user_data['url'], user_data['query'])
        else:
            info.players_toomany(context.bot, update.message.chat_id, user_data['url'], user_data['status'])
        logging.info("/players %s online" % user_data['url'])
        return

    except TimeoutError:
        logging.error("Timeout error ({})".format(inspect.stack()[0][3]))
    except Exception as e:
        logging.exception(e)

    error.status(context.bot, update.message.chat_id, user_data['url'])


# ==========================
# CallBacks
# ==========================

@run_async
def cb_status(update: Update, context: CallbackContext):
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.callback_query))

    user_data = context.user_data

    try:

        user_data['status'] = user_data['server'].status()

        if type(user_data['status'].description) is str:
            description = user_data['status'].description # hypixel-like
        else:
            description = user_data['status'].description['text'] # vanilla
        logging.info("Status description type is "+ str(type(user_data['status'].description)))

        import re
        description_format = re.sub('§.', '', description)
        description_format = re.sub('', '', description_format)

        context.bot.editMessageText(
            text=(
                "(ﾉ◕ヮ◕)ﾉ:･ﾟ✧\n╭ ✅ *Online*\n*Url:* `{0}`\n*Description:*\n_{1}_\n*Version:* {"
                "2}\n*Ping:* {3}ms\n*Players:* {4}/{5}\n╰".format(
                    user_data['url'],
                    description_format,
                    user_data['status'].version.name,
                    user_data['status'].latency,
                    user_data['status'].players.online,
                    user_data['status'].players.max,
                ))
            , reply_markup=reply_markup
            , chat_id=update.callback_query.message.chat_id
            , message_id=update.callback_query.message.message_id
            , parse_mode=ParseMode.MARKDOWN)
        return

    except TimeoutError:
        logging.error("Timeout error ({})".format(inspect.stack()[0][3]))
    except Exception as e:
        logging.exception(e)

    error.status_edit(update, context.bot, user_data['url'])


@run_async
def cb_players(update: Update, context: CallbackContext):
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.callback_query))
    user_data = context.user_data

    try:
        query = MinecraftServer.lookup(user_data['url'])
        user_data['query'] = query.query()

        context.bot.editMessageText(
            text="(•(•◡(•◡•)◡•)•)\n╭ ✅ *Online*\n*Url:* `{0}`\n*Users Online* {1}*:*\n{2}\n╰\n".format(
                user_data['url'],
                len(user_data['query'].players.names),
                str("`" + "`, `".join(user_data['query'].players.names) + "`")
            )
            , reply_markup=reply_markup
            , chat_id=update.callback_query.message.chat_id
            , message_id=update.callback_query.message.message_id
            , parse_mode=ParseMode.MARKDOWN)
        return
    except TimeoutError:
        logging.error("Timeout error ({})".format(inspect.stack()[0][3]))
    except Exception as e:
        logging.exception(e)
        
    error.players_edit(update, context.bot, user_data['url'])


@run_async
def cb_about(update: Update, context: CallbackContext):
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.callback_query))

    try:
        context.bot.editMessageText(
            text=welcome_text
            , chat_id=update.callback_query.message.chat_id
            , reply_markup=reply_markup
            , message_id=update.callback_query.message.message_id
            , parse_mode=ParseMode.MARKDOWN)
        return
    
    except Exception as e:
        logging.exception(e)
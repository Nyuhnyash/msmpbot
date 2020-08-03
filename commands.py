# pylint: disable=unused-wildcard-import

import logging
from mcstatus import MinecraftServer
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, ChatAction, ParseMode
from telegram.ext import CallbackContext

from utils import validUrl, ending, name_and_id, update_object_type
from replies import error, info, reply_markup
import db

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

def inline_status(update: Update, context: CallbackContext):
    user_data = context.user_data

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


# ==========================
# Message Handler
# ==========================

def message(update: Update, context: CallbackContext):
    """Usage: <IP-address> """
    user_data = context.user_data
    
    text = update.message.text
        
    if text=="default":
        text = db.default_url
    if not validUrl(text):
        logging.info("Invalid URL, too long")
        return
    user_data['url'] = text
    db.set(update.effective_user.id, text)

    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    context.bot.send_message(update.message.chat_id, text="Адрес сервера изменён на "+user_data['url'], parse_mode=ParseMode.MARKDOWN)


# ==========================
# Commands
# ==========================

def cmd_start(update: Update, context: CallbackContext):
    """Usage: /start"""
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    
    context.bot.send_message(update.message.chat_id, text=welcome_text, parse_mode=ParseMode.MARKDOWN)


def cmd_status(update: Update, context: CallbackContext):
    """Usage: /status url"""
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    user_data = context.user_data

    user_data['server'] = MinecraftServer.lookup(user_data['url'])
    user_data['status'] = user_data['server'].status()

    info.status(context.bot, update.message.chat_id, user_data['url'], user_data['status'])
    logging.info("/status %s online" % user_data['url'])


def cmd_players(update: Update, context: CallbackContext):
    """Usage: /players url"""
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    user_data = context.user_data

    user_data['server'] = MinecraftServer.lookup(user_data['url'])
    user_data['status'] = user_data['server'].status()
    if user_data['status'].players.online < 32:
        user_data['query'] = user_data['server'].query()
        info.players(context.bot, update.message.chat_id, user_data['url'], user_data['query'])
    else:
        info.players_toomany(context.bot, update.message.chat_id, user_data['url'], user_data['status'])
    logging.info("/players %s online" % user_data['url'])


# ==========================
# CallBacks
# ==========================

def cb_status(update: Update, context: CallbackContext):
    user_data = context.user_data

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


def cb_players(update: Update, context: CallbackContext):
    user_data = context.user_data

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
        

def cb_about(update: Update, context: CallbackContext):
    context.bot.editMessageText(
        text=welcome_text
        , chat_id=update.callback_query.message.chat_id
        , reply_markup=reply_markup
        , message_id=update.callback_query.message.message_id
        , parse_mode=ParseMode.MARKDOWN)


# ==========================
# Before all handlers
# ==========================

def check_database(update, context):
    try:

        context.user_data['url']

    except KeyError:
        context.user_data['url'] = db.get(update.effective_user.id)

    logging.info(update_object_type(update).__class__.__name__ + " recieved from " + name_and_id(update.effective_user))
        

# ==========================
# Error handler
# ==========================

from socket import timeout as TimeoutError
def error_handler(update : Update, context : CallbackContext):
    if type(context.error) is TimeoutError:
        logging.error("Timeout error")
    else:
        logging.exception(context.error)

    if update.inline_query:
        error.inline(context.bot, update.inline_query.id)
    elif update.message:
        error.message(context.bot, update.message.chat_id, context.user_data['url'])
    elif update.callback_query:
        error.callback(context.bot, update.callback_query.message, context.user_data['url'])
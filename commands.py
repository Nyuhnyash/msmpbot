# pylint: disable=undefined-variable
import logging

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, ChatAction, ParseMode
from telegram.ext import CallbackContext
from telegram.ext.dispatcher import run_async

from utils import validUrl, name_and_id, update_object_type, MinecraftServer, players
from replies import error, info, reply_markup
from db import data
logging.basicConfig(
                    handlers=(
                              logging.FileHandler('command_logs.log'),
                              logging.StreamHandler()),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# ==========================
# Inline Query Handler
# ==========================

def inline_status(update: Update, context: CallbackContext):
    address = context.user_data['url']

    q = list()

    q.append(InlineQueryResultArticle(
        id='1', title=_('Address: ') + address,
        input_message_content=InputTextMessageContent(
        message_text=_('Address: ') + address))
        )

    online, str_players = players(address, True)

    text = ngettext('{0} player online', '{0} players online', online).format(online)

    q.append(InlineQueryResultArticle(
        id='2', title=text,
        description=str_players,
        input_message_content=InputTextMessageContent(
        message_text=text + ': ' + str_players)))

    context.bot.answer_inline_query(update.inline_query.id, q, cache_time=60)
    logging.info("inline answer sent")


# ==========================
# Message Handler
# ==========================

def message(update: Update, context: CallbackContext):
    """Usage: <IP-address> """
    user_data = context.user_data
    
    text = update.message.text.lower()

    if text != 'default':
        if not validUrl(text):
            logging.info("Invalid URL, too long")
            return

    data(update.effective_user.id, text)

    user_data['url'] = data(update.effective_user.id)

    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    context.bot.send_message(update.message.chat_id, text=_('Server addess changed to ') + user_data['url'], parse_mode=ParseMode.MARKDOWN)


# ==========================
# Commands
# ==========================

@run_async
def cmd_start(update: Update, context: CallbackContext):
    """Usage: /start"""
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    context.bot.send_message(update.message.chat_id, text=welcome_text
    , parse_mode=ParseMode.MARKDOWN)


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

    address = context.user_data['url']

    info.players(context.bot, update.message.chat_id, address, players(address))

    logging.info("/players %s online" % address)


# ==========================
# CallBacks
# ==========================

def cb_status(update: Update, context: CallbackContext):
    user_data = context.user_data

    user_data['server'] = MinecraftServer.lookup(user_data['url'])
    user_data['status'] = user_data['server'].status()

    if type(user_data['status'].description) is str:
        description = user_data['status'].description # hypixel-like
    else:
        description = user_data['status'].description['text'] # vanilla

    import re
    description_format = re.sub('§.', '', description)
    description_format = re.sub('', '', description_format)

    context.bot.editMessageText(
        text=_(
            "(ﾉ◕ヮ◕)ﾉ:･ﾟ✧\n"
            "╭ ✅ *Online*\n"
            "*Url:* `{0}`\n"
            "*Description:*\n"
            "_{1}_\n"
            "*Version:* {2}\n"
            "*Ping:* {3}ms\n"
            "*Players:* {4}/{5}\n"
            "╰"
            ).format(
                user_data['url'],
                description_format,
                user_data['status'].version.name,
                user_data['status'].latency,
                user_data['status'].players.online,
                user_data['status'].players.max,
            )
        , reply_markup=reply_markup()
        , chat_id=update.callback_query.message.chat_id
        , message_id=update.callback_query.message.message_id
        , parse_mode=ParseMode.MARKDOWN)


def cb_players(update: Update, context: CallbackContext):
    user_data = context.user_data

    query = MinecraftServer.lookup(user_data['url'])
    user_data['query'] = query.query()

    context.bot.editMessageText(
        text=_(
            "(•(•◡(•◡•)◡•)•)\n"
            "╭ ✅ *Online*\n"
            "*Url:* `{0}`\n"
            "*Players online:* {1}\n"
            "{2}\n"
            "╰"
            ).format(
                user_data['url'],
                len(user_data['query'].players.names),
                str("`" + "`, `".join(user_data['query'].players.names) + "`")
            )
        , reply_markup=reply_markup()
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

from os import getenv
import gettext
domain = getenv("HEROKU_APP_NAME")
lang_code = ""

def check_database(update : Update, context: CallbackContext):
    try:
        context.user_data['url']

    except KeyError:
        context.user_data['url'] = data(update.effective_user.id)
        context.user_data['lang'] = update.effective_user.language_code
        
    global lang_code
    if lang_code != context.user_data['lang']:
        lang_code = context.user_data['lang']
        
        if gettext.find(domain, "locale", [lang_code]):
            lang = gettext.translation(domain, "locale", [lang_code])
        else:
            lang = gettext.translation(domain, "locale", ['en'])
        lang.install(['ngettext'])

        global welcome_text
        welcome_text = _(
            "Minecraft Server Status Bot\n"
            "\n"
            "To check players online on the server use @msmpbot in the text input line in any Telegram chat.\n"
            "\n"
            "Commands:\n"
            "/status - Server info\n"
            "/players - Online players on the server\n"
            "\n"
            "To change the monitored server send me its address."
        )

    logging.info(update_object_type(update).__class__.__name__ + " recieved from " + name_and_id(update.effective_user))
    
# ==========================
# Error handler
# ==========================

from socket import timeout as TimeoutError
from telegram.error import BadRequest

def error_handler(update : Update, context : CallbackContext):
    if type(context.error) is TimeoutError:
        logging.error("Timeout error")
    else:
        logging.exception(context.error)

        if type(context.error) is BadRequest: return

    if update.inline_query:
        error.inline(context.bot, update.inline_query.id)
    elif update.message:
        error.message(context.bot, update.message.chat_id, context.user_data['url'])
    elif update.callback_query:
        error.callback(context.bot, update.callback_query.message, context.user_data['url'])
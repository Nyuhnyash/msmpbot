import telegram
import logging
from mcstatus import MinecraftServer
import re
from telegram.ext.dispatcher import run_async
from utils import validUrl, ending, name_and_id
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

btn_players = telegram.InlineKeyboardButton("Players", callback_data='pattern_players')
btn_status = telegram.InlineKeyboardButton("Status", callback_data='pattern_status')
btn_about = telegram.InlineKeyboardButton("About", callback_data='pattern_about')
keyboard = [[btn_status, btn_players, btn_about]]
reply_markup = telegram.InlineKeyboardMarkup(keyboard)


# ==========================
# Inline Query Handler
# ==========================

from telegram import Update, Bot, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CallbackContext
from socket import timeout
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
    
    except timeout:
        error_status_inline(context.bot, update.inline_query.id)
        logging.error("Timeout error (inline)")
    except Exception as e:
        logging.exception(e)

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

        context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(update.message.chat_id, text="Адрес сервера изменён на "+user_data['url'], parse_mode=telegram.ParseMode.MARKDOWN)

    except Exception as e:
        logging.exception(e)

# ==========================
# Commands
# ==========================

@run_async
def cmd_start(update: Update, context: CallbackContext):
    """Usage: /start"""
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.message))
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    
    context.bot.send_message(update.message.chat_id, text=welcome_text, parse_mode=telegram.ParseMode.MARKDOWN)

@run_async
def cmd_status(update: Update, context: CallbackContext):
    """Usage: /status url"""
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.message))
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    user_data = context.user_data
    user_data['url'] = db.get(update.message)

    try:

        user_data['server'] = MinecraftServer.lookup(user_data['url'])
        user_data['status'] = user_data['server'].status()

        info_status(context.bot, update.message.chat_id, user_data['url'], user_data['status'])
        logging.info("/status %s online" % user_data['url'])

    except timeout:
        error_status(context.bot, update.message.id,user_data['url'])
        logging.error("Timeout error (/status)")

    except Exception as e:
        error_status(context.bot, update.message.chat_id, user_data['url'])
        logging.exception(e)


@run_async
def cmd_players(update: Update, context: CallbackContext):
    """Usage: /players url"""
    
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.message))
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    user_data = context.user_data
    user_data['url'] = db.get(update.message)
    try:
        
        user_data['url'] = db.get(update.message)

        user_data['server'] = MinecraftServer.lookup(user_data['url'])
        user_data['status'] = user_data['server'].status()
        if user_data['status'].players.online < 32:
            user_data['query'] = user_data['server'].query()
            info_players(context.bot, update.message.chat_id, user_data['url'], user_data['query'])
        else:
            toomany_players(context.bot, update.message.chat_id, user_data['url'], user_data['status'])
        logging.info("/players %s online" % user_data['url'])

    except Exception as e:
        error_status(context.bot, update.message.chat_id, user_data['url'])
        logging.exception(e)


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
            , parse_mode=telegram.ParseMode.MARKDOWN)
            
    except Exception as e:
        error_status_edit(update, context.bot, user_data['url'])
        logging.exception(e)


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
            , parse_mode=telegram.ParseMode.MARKDOWN)

    except Exception as e:
        error_players_edit(update, context.bot, user_data['url'])
        logging.exception(e)


@run_async
def cb_about(update: Update, context: CallbackContext):
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.callback_query))

    try:
        context.bot.editMessageText(
            text=welcome_text
            , chat_id=update.callback_query.message.chat_id
            , reply_markup=reply_markup
            , message_id=update.callback_query.message.message_id
            , parse_mode=telegram.ParseMode.MARKDOWN)
    except Exception as e:
        logging.exception(e)


# ==========================
# Info
# ==========================

def info_status(bot, chat_id, _url, _status):
    if type(_status.description) is str:
        description = _status.description # hypixel-like
    else:
        description = _status.description['text'] # vanilla

    description_format = re.sub('§.', '', description)
    description_format = re.sub('', '', description_format)

    bot.sendMessage(
        chat_id=chat_id,
        text=(
            "(ﾉ◕ヮ◕)ﾉ:･ﾟ✧\n╭ ✅ *Online*\n*Url:* `{0}`\n*Description:*\n_{1}_\n*Version:* {"
            "2}\n*Ping:* {3}ms\n*Players:* {4}/{5}\n╰".format(
                _url,
                description_format,
                _status.version.name,
                _status.latency,
                _status.players.online,
                _status.players.max,
            ))
        , reply_markup=reply_markup
        , parse_mode=telegram.ParseMode.MARKDOWN)


def info_players(bot, chat_id, _url, _query):
    bot.sendMessage(
        chat_id=chat_id,
        text="(•(•◡(•◡•)◡•)•)\n╭ ✅ *Online*\n*Url:* `{0}`\n*Users Online* {1}*:*\n{2}\n╰\n".format(
            _url,
            len(_query.players.names),
            str("`" + "`, `".join(_query.players.names) + "`")
        )
        , reply_markup=reply_markup
        , parse_mode=telegram.ParseMode.MARKDOWN)


def toomany_players(bot, chat_id, _url, status):
    bot.sendMessage(
        text="(•(•◡(•◡•)◡•)•)\n╭ ✅ *Online*\n*Url:* `{0}`\n*Users Online* {1}".format(
            _url,
            status.players.online
        )
        , reply_markup=reply_markup
        , chat_id=chat_id
        , parse_mode=telegram.ParseMode.MARKDOWN)

# ==========================
# Error
# ==========================

def error_status_inline(bot: Bot, iq_id):
    r = InlineQueryResultArticle(
            id='1', title='Сервер не отвечает',
            #description=str_players,
            input_message_content=InputTextMessageContent(
            message_text='Сервер не отвечает')
            )
    bot.answer_inline_query(iq_id, [r], cache_time=5)


def error_status(bot, chat_id, args):
    bot.sendMessage(
        chat_id=chat_id,
        text="(╯°□°）╯ ︵ ┻━┻\n╭ ⭕ *Offline*\n*Url:* `{0}`\n*Error Description:*\n{1}\n╰\n".format(
            args[0],
            str("_Could not connect to the server_")
        )
        , reply_markup=reply_markup
        , parse_mode=telegram.ParseMode.MARKDOWN)


def error_status_edit(update, bot, param_url):
    bot.editMessageText(
        text="(╯°□°）╯ ︵ ┻━┻\n╭ ⭕ *Offline*\n*Url:* `{0}`\n*Error Description:*\n{1}\n╰\n".format(
            param_url,
            str("_Could not connect to the server_")
        )
        , reply_markup=reply_markup
        , chat_id=update.callback_query.message.chat_id
        , message_id=update.callback_query.message.message_id
        , parse_mode=telegram.ParseMode.MARKDOWN)


def error_players_edit(update, bot, param_url):
    bot.editMessageText(
        text="(╯°□°）╯ ︵ ┻━┻\n╭ 🔻 *Error*\n*Url:* `{0}`\n*Error Description:*\n_Could not connect to the "
             "server_\n_The server may not allow Query requests_\n╰\n".format(param_url)
        , reply_markup=reply_markup
        , chat_id=update.callback_query.message.chat_id
        , message_id=update.callback_query.message.message_id
        , parse_mode=telegram.ParseMode.MARKDOWN)


def error_url(bot, update, args):
    bot.sendMessage(
        chat_id=update.message.chat_id,
        text=("(╯°□°）╯ ︵ ┻━┻\n╭ 🔻 *Error*\n*Url:* `{0}`\n*Error Description:*\n{1}\n\n*Correct "
              "Examples:*\n_play.minecraft.net_\n_minecraftgame.org_\n╰").format(
            args[0],
            str("_The url introduced is not valid, please, try again_")
        )
        , reply_markup=reply_markup
        , parse_mode=telegram.ParseMode.MARKDOWN)


def error_incomplete(bot, update):
    bot.sendMessage(
        chat_id=update.message.chat_id,
        text=(
            "(╯°□°）╯ ︵ ┻━┻\n╭ 🔻 *Error*\n_You must provide an url please, try again_\n\n*Correct "
            "Examples:*\n_/status play.minecraft.net_\n_/status minecraftgame.org:25898_\n╰ "
        )
        , reply_markup=reply_markup
        , parse_mode=telegram.ParseMode.MARKDOWN)
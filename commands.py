import telegram
import logging
from mcstatus import MinecraftServer
import re
from telegram.ext.dispatcher import run_async
from utils import validUrl, ending, name_and_id
import inspect

logging.basicConfig(
                    handlers=(
                              logging.FileHandler('command_logs.log'),
                              logging.StreamHandler()),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

welcome_text = "༼ つ ◕ ◡ ◕ ༽つ\nMinecraft Server Status\n\n/status _url.example.com_\n/players _play.example.com_\n\nBot developed by @GSiesto"

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
    user_data = context.user_data
    try: 
        if not user_data['url']:
            user_data['url'] = "51.178.75.71:40714"
        if not validUrl(user_data['url']):
            error_status_inline(context.bot, update.inline_query.id)
            logging.error("Error status (inline)")
        server = MinecraftServer.lookup(user_data['url'])
        query = server.query()
        q = list()
        players = query.players.names
        
        q.append(InlineQueryResultArticle(
            id='1', title='IP: ' + user_data['url'],
            input_message_content=InputTextMessageContent(
            message_text='IP: ' + user_data['url']))
            )

        str_players = str(", ".join(players))
        end = ending(len(players))
        
        q.append(InlineQueryResultArticle(
            id='2', title='{0} игрок{1} онлайн:'.format(len(players),end),
            description=str_players,
            input_message_content=InputTextMessageContent(
            message_text='{0} игрок{1} онлайн: {2}'.format(len(players),end, str_players)))
            )

        context.bot.answer_inline_query(update.inline_query.id, q, cache_time=60)
        logging.info("inline answer sent to " + name_and_id(update.inline_query))
    
    except timeout:
        error_status_inline(context.bot, update.inline_query.id)
        logging.error("Timeout (inline)")
    except Exception as e:
        logging.exception(e)

# ==========================
# Message Handler
# ==========================

@run_async
def message(update: Update, context: CallbackContext):
    """Usage: <IP-address> """
    logging.info("Message recieved")
    user_data = context.user_data
    try: 
        if not validUrl(update.message.text):
            logging.info("Invalid URL, too long")
            return
        user_data['url'] = update.message.text
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
    user_data = context.user_data
    user_data['url'] = '51.178.75.71:40714'
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(update.message.chat_id, text=welcome_text, parse_mode=telegram.ParseMode.MARKDOWN)


@run_async
def cmd_status(update: Update, context: CallbackContext):
    """Usage: /status url"""
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.message))
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    user_data = context.user_data

    try:

        if  not validUrl(user_data['url']):
            error_url(context.bot, update, user_data['url'])
            logging.error("Invalid URL, too long")
            return
        user_data['server'] = MinecraftServer.lookup(user_data['url'])
        user_data['status'] = user_data['server'].status()

        info_status(context.bot, update.message.chat_id, user_data['url'], user_data['status'])
        logging.info("/status %s online" % user_data['url'])
   
    except Exception as e:
        error_status(context.bot, update.message.chat_id, user_data['url'])
        logging.exception(e)


@run_async
def cmd_players(update: Update, context: CallbackContext):
    """Usage: /players url"""
    
    logging.info(inspect.stack()[0][3] + " called by " + name_and_id(update.message))
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    user_data = context.user_data

    try:

        if not validUrl(user_data['url']):
            error_url(context.bot, update, user_data['url'])
            logging.info("Invalid URL, too long")
            return
        user_data['server'] = MinecraftServer.lookup(user_data['url'])
        user_data['status'] = user_data['server'].status()

        user_data['server'] = user_data['server']
        user_data['query'] = user_data['server'].query()

        info_players(context.bot, update.message.chat_id, user_data['url'], user_data['query'])
        logging.info("/players %s online" % user_data['url'])

    except Exception as e:
        error_status(context.bot, update.message.chat_id, context.args)
        logging.exception(e)


# ==========================
# CallBacks
# ==========================

@run_async
def cb_status(update: Update, context: CallbackContext):
    logging.info("CallBack Status called")

    user_data = context.user_data

    try:

        user_data['status'] = user_data['server'].status()

        description_format = re.sub('§.', '', user_data['status'].description['text'])
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
    logging.info("CallBack Players called")

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
    logging.info("CallBack About called")

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
    description_format = re.sub('§.', '', _status.description['text'])
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
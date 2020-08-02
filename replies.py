# pylint: disable=no-self-argument, no-member

import telegram

btn_players = telegram.InlineKeyboardButton("Players", callback_data='pattern_players')
btn_status = telegram.InlineKeyboardButton("Status", callback_data='pattern_status')
btn_about = telegram.InlineKeyboardButton("About", callback_data='pattern_about')
keyboard = [[btn_status, btn_players, btn_about]]
reply_markup = telegram.InlineKeyboardMarkup(keyboard)

class error:
    
    def inline(bot: telegram.Bot, iq_id):
        r = telegram.InlineQueryResultArticle(
                id='1', title='Сервер не отвечает',
                input_message_content=telegram.InputTextMessageContent(
                message_text='Сервер не отвечает')
                )
        bot.answer_inline_query(iq_id, [r], cache_time=5)


    def message(bot, chat_id, param_url):
        bot.sendMessage(
            chat_id=chat_id,
            text="(╯°□°）╯ ︵ ┻━┻\n╭ ⭕ *Offline*\n*Url:* `{0}`\n*Error Description:*\n{1}\n╰\n".format(
                param_url,
                str("_Could not connect to the server_")
            )
            , reply_markup=reply_markup
            , parse_mode=telegram.ParseMode.MARKDOWN)


    def callback(bot, message, param_url):
        bot.editMessageText(
            text="(╯°□°）╯ ︵ ┻━┻\n╭ ⭕ *Error*\n*Url:* `{0}`\n*Error Description:*\n{1}\n╰\n".format(
                param_url,
                str("_Could not connect to the server_")
            )
            , reply_markup=reply_markup
            , chat_id=message.chat_id
            , message_id=message.message_id
            , parse_mode=telegram.ParseMode.MARKDOWN)

class info:

    def status(bot, chat_id, _url, _status):
        if type(_status.description) is str:
            description = _status.description # hypixel-like
        else:
            description = _status.description['text'] # vanilla
            
        import re
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


    def players(bot, chat_id, _url, _query):
        bot.sendMessage(
            chat_id=chat_id,
            text="(•(•◡(•◡•)◡•)•)\n╭ ✅ *Online*\n*Url:* `{0}`\n*Users Online* {1}*:*\n{2}\n╰\n".format(
                _url,
                len(_query.players.names),
                str("`" + "`, `".join(_query.players.names) + "`")
            )
            , reply_markup=reply_markup
            , parse_mode=telegram.ParseMode.MARKDOWN)


    def players_toomany(bot, chat_id, _url, status):
        bot.sendMessage(
            text="(•(•◡(•◡•)◡•)•)\n╭ ✅ *Online*\n*Url:* `{0}`\n*Users Online* {1}".format(
                _url,
                status.players.online
            )
            , reply_markup=reply_markup
            , chat_id=chat_id
            , parse_mode=telegram.ParseMode.MARKDOWN)
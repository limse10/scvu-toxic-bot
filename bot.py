import logging
import json 
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv('TOKEN')
# from env import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

latest_message = None

toxic_score = {}
with open('scores.json') as scoresfile:
    toxic_score = json.load(scoresfile)

def add_toxic(message):
    user = message.from_user.username
    print(message.from_user)
    if user in toxic_score:
        toxic_score[user] += 1
    else:
        toxic_score[user] = 1

    with open('scores.json', 'w') as scoresfile:
        json.dump(toxic_score, scoresfile)

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('/t')

def get_scores(update, context):
    names = update.message.text.split()[1:]
    for name in names:
        if name in toxic_score:
            if toxic_score[name]==1:
                update.message.reply_text(f'{name} currently has {toxic_score[name]} toxic point')
            else:
                update.message.reply_text(f'{name} currently has {toxic_score[name]} toxic points')

        else:
            update.message.reply_text(f'{name} not found')

def leaderboard(update, context):
    sorted_scores = dict(sorted(toxic_score.items(), key=lambda item: item[1], reverse=True))
    output_message = 'LEADERBOARD\n'
    for i, (name, score) in enumerate(sorted_scores.items()):
        if score==1:
            output_message += f'{i+1}: {name} - {score} toxic point\n'
        else:
            output_message += f'{i+1}: {name} - {score} toxic points\n'
    update.message.reply_text(output_message)

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('toxic scores get added when u reply to message with /t.\nwhen u /t without a reply, it adds to the latest non "/t" message')

def toxic(update, context):
    # update.message.reply_text('/t')
    if update.message.reply_to_message:
        add_toxic(update.message.reply_to_message)
    elif latest_message:
        add_toxic(latest_message)

def read(update,context):
    global latest_message

    if update.message.text != "/t":
        latest_message = update.message

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("t", toxic))
    dp.add_handler(CommandHandler("scores", get_scores))
    dp.add_handler(CommandHandler("leaderboard", leaderboard))
    dp.add_handler(MessageHandler(Filters.text, read))


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
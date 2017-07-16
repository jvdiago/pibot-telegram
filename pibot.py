#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to send timed Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler
import logging
from log_utils import LogReader
from datetime import timedelta, datetime
import tzlocal
import settings
from command_utils import LocalCommand

# Enable logging
logging.basicConfig(
    filename=settings.LOG_FILE,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    for job in settings.JOBS.keys():
        update.message.reply_text('Hi! Use /set {0} <seconds> to set a {0} job'.format(
            job
        ))


def logparser_job(bot, job):
    interval = job.interval
    job_name = job.name
    log_settings = settings.JOBS.get(job_name)

    log_file = log_settings['log_file']
    log_reader = log_settings['log_reader']
    status_limits = log_settings['status_limits']
    filter_networks = log_settings['filter_networks']

    processor = LogReader(log_reader, log_file)
    tz = tzlocal.get_localzone()
    for log in processor.get_records():
        try:
            now = datetime.now(tz)
            if log.get_date() >= (now - timedelta(seconds=interval)):
                if status_limits[1] > log.get_status() >= status_limits[0]:
                    notify = True
                    for network in filter_networks:
                        if log.get_ip() in network:
                            notify = False
                    if notify:
                        bot.sendMessage(job.context, text=str(log))
        except Exception as e:
            logger.warn('Error parsing nginx logs: {0}'.format(e))


def set_wrapper(bot, update, args, job_queue, chat_data):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[1])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_name = args[0]
        if job_name not in settings.JOBS:
            update.message.reply_text(
                'Sorry {0} is not a valid job'.format(job_name))
            return

        # Add job to queue
        job_queue.run_repeating(logparser_job, due, name=job_name, context=chat_id)

        update.message.reply_text('{0} job set!'.format(job_name))

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <job_name> <seconds>')


def unset_wrapper(bot, update, args, job_queue, chat_data):
    """Removes the job if the user changed their mind"""
    job_name = args[0]
    if job_name not in settings.JOBS:
        update.message.reply_text(
            'Sorry {0} is not a valid job'.format(job_name))
        return

    job = None
    for j in job_queue.jobs():
        if j.name == job_name:
            job = j
            break

    if not job:
        update.message.reply_text('You have no active job')
        return

    job.schedule_removal()

    update.message.reply_text('{0} job successfully unset!'.format(job_name))


def cmd_job(bot, update, args, job_queue, chat_data):
    alias = args[0]

    if alias not in settings.CMD.keys():
        update.message.reply_text('{0} alias not valid!'.format(alias))
        logger.warning('{0} alias not found'.format(alias))
        return

    command = settings.CMD[alias]

    cmd = LocalCommand(command)
    c_out, c_err, c_returncode = cmd.execute()


    update.message.reply_text('Command: {0} executed\nOutput: {1}\nErrror: {2}\nCode: {3}'.format(
        command,
        c_out,
        c_err,
        c_returncode
    ))


def error(bot, update, error):
    logger.warning('Update "{0}" caused error "{1}"'.format(update, error))


def main():
    updater = Updater(settings.TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler(
        "set",
        set_wrapper,
        pass_args=True,
        pass_job_queue=True,
        pass_chat_data=True))
    dp.add_handler(CommandHandler(
        "unset",
        unset_wrapper,
        pass_args=True,
        pass_job_queue=True,
        pass_chat_data=True))
    
    dp.add_handler(CommandHandler(
        "cmd",
        cmd_job,
        pass_args=True,
        pass_job_queue=True,
        pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

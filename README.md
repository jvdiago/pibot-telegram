# pibot-telegram

Simple telegram bot to manage some aspects of a Raspberry PI with Raspbian. It has a bascic plugin support to add more commands and log readers

## Instructions

    $ pip install -r requirements.txt
    $ Edit settings.py and add yout telegram chat token (TELEGRAM_TOKEN=)
    $ python pibot.py

### Start log reader jobs

    # From the telegram chat, type /set <job> <timer>. The bot will read the logfile each <timer> seconds and alert about any action between the boundaries defined in settings.py
    $ /set nginx 15
    $ /set ssh 15
    

### execute commands

    # From the telegram chat, type /cmd <alias> to execute the alias defined on settings.py
    $ /cmd  hostname

## Limitations

Only tested on raspbian. Because of how it works (it does not save the last parsed line to seek afterwards, performance could be terrible on very large files.

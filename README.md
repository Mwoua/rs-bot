# rs-bot

Discord bot to manage red star for the game Hades star

Note: its currently coded so it works on only one server. If the bot is running on several servers, the queue will be common

## Available commands

- clearX: empty the queue for red star level X
- rsX: queue user for red star level X queue
- out: remove user from all queues

## Setup

Create a `.env` file in the root directory:

>ServerId=SERVERID  
TOKEN=TOKEN

ServerId is the id of the server you want the bot to run on
TOKEN is the discord bot token

## Startup basic

You need to run `main.py`

## Startup as a daemon

Create a file in `/etc/systemd/system` for example with `nano /etc/systemd/system/rs_bot.service` and copy below text. (User and WorkingDirectory need to be changed to your setup)

```bash
[Unit]
Description=Red star discord bot
After=multi-user.target

[Service]
WorkingDirectory=/opt/rs-bot
Type=simple
User=user
ExecStart=/usr/bin/python3 ./main.py

# This will restart your bot if your bot doesn't return a 0 exit code
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Then enable the service:

```shell
systemctl daemon-reload
systemctl enable rs_bot
systemctl start rs_bot
```

And you can use `systemctl status rs_bot` to check that it correctly started. And `journalctl -u rs_bot` to view the bot logging output.

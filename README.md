# MSMPbot
Telegram Bot that helps you to check if your favorite Minecraft Servers are online. You can even see the players that are connected.

## How to Execute in your local machine
### Enviroment Variables

TOKEN = **Your telegram TOKEM ID**

MODE = "DEV" (Local Machine) or "PROD" (For a Heroku deployment)

### Usage
Execute with python the file `main.py`.
If everything was set up fine, you will be able to start chatting with your own bot.
A file called persistent_data will be generated. This file makes it possible for the instance to know again what the link was, and thus be able to use the inline buttons (CallBacks) on the screen.

Example

```
pip install -r requirements.txt
MODE=dev TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx python main.py
```

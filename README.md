<div align='center'>
<h1>Telegram Discord Bridge</h1>
<h3>Simple two-way bridge between Telegram and Discord in python</h3>
<br>
<a href="https://github.com/Rapptz/discord.py">
   <img src="https://img.shields.io/badge/discord.py-v2.3.1-blue?" alt="discord.py"/>
</a>
   <a href="https://github.com/pyrogram/pyrogram">
   <img src="https://img.shields.io/badge/pyrogram-2.0.106-blue?" alt="pyrogram"/>
</a>
</div>

<br>

## Features
- It can transfer messages from both Telegram to Discord and Discord to Telegram
- Supports transfaring media, documents, voice messages and stickers
- Create as many bridges as you like
- Easy to setup and run

## Installation Guide
1. Create a [Discord Bot](https://discord.com/developers/) and copy your bot token and application ID
2. Set up a [Telegram Application](https://core.telegram.org/api/obtaining_api_id) and copy your API ID and API Hash
3. Install <a href = "https://www.python.org/downloads/">python</a> 3.8 or higher and <a href = "https://git-scm.com/downloads">git</a> and add them to the path</li>
4. Git-clone this repo & change directory

```
git clone https://github.com/Shinobi7k/TelegramDiscordBridge.git

cd TelegramDiscordBridge
```
5. Install modules using pip

```
pip install -r requirements.txt
```
6. Copy `example.settings.yaml` to `settings.yaml` and fill the needed variables
7. Run the main file
```
python main.py
```
8. You will see a message in the terminal asking for a phone number or a bot token, this is needed by Telegram only the first time you run the bridge. So either enter your phone number or your [bot token](https://core.telegram.org/bots/features#creating-a-new-bot)
import discord
from discord.ext import commands
import asyncio
import os
import json
import yaml


async def check_chat(chat):
    with open('settings.yaml', 'r') as file:
        data = yaml.safe_load(file)
    targets = data['bridges']
    for target in targets:
        if chat == target['name']:
            channel = bot.get_channel(target['discord_chat_id'])
            return channel

async def detect_text_change(self):
    json_file = "messages/telegram/text.json"
    last_modified = os.path.getmtime(json_file)
    while True:
        await asyncio.sleep(0.5)
        new_modified = os.path.getmtime(json_file)
        if new_modified > last_modified:
            with open(json_file, "r") as f:
                data = json.load(f)
            content = data["message"]["content"]
            sender = data["message"]["sender"]
            chat = data["message"]["chat"]
            replied_to_text = data["message"]["replied_to_text"]
            replied_to_sender = data["message"]["replied_to_sender"]
            last_modified = new_modified
            channel = await check_chat(chat)
            limit = 1800
            async def reply_or_send(message_content):
                if str(replied_to_text) == "None":
                    await channel.send(message_content)
                else:
                    async for message in channel.history(limit=100):
                        if message.content == replied_to_text or message.content == f"*{replied_to_sender}:*\n{replied_to_text}":
                            await message.reply(message_content)
                            break
                    else:
                        await channel.send(message_content)
            if len(content) > limit:
                whole_text = [content[i: i + limit] for i in range(0, len(content), limit)]
                for part_of_text in whole_text:
                    if sender == chat: await reply_or_send(part_of_text) # If channel, don't send the username
                    else: await reply_or_send(f"*{sender}:*\n{part_of_text}") # If group, send the username
            else:
                if sender == chat: await reply_or_send(content) # If channel, don't send the username
                else: await reply_or_send(f"*{sender}:*\n{content}") # If group, send the username

async def detect_new_files(self):
    while True:
        await asyncio.sleep(0.5)
        files_now = os.listdir("messages/telegram")
        files_to_detect = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mp3", ".ogg", ".pdf", ".apk"]
        # Create a set of file extensions for faster membership check
        extensions = set(files_to_detect)
        # Check each file in files_now
        for file in files_now:
            # Extract the file extension
            file_extension = os.path.splitext(file)[1]
            if file_extension == ".temp":
                continue
            # Check if the extension is in the set of extensions
            elif file_extension.lower() in extensions:
                with open('messages/telegram/attachments.json', "r") as f:
                    data = json.load(f)
                # file_path = data["message"]["path"]
                file_path = f"messages/telegram/{file}"
                sender = data["message"]["sender"]
                chat = data["message"]["chat"]
                channel = await check_chat(chat)
                if os.path.getsize(file_path) > 8388608:
                    if sender == chat: await channel.send("File size is over 8MB, so I can't send it. Sorry :(")
                    else: await channel.send(f"*{sender}:* File size is over 8MB, so I can't send it. Sorry :(")
                else:
                    if sender == chat: await channel.send(file=discord.File(file_path))
                    else: await channel.send(file=discord.File(file_path), content=f"*{sender}:* [{file}]")
                os.remove(file_path)
            else:
                if file != "attachments.json" and file != "text.json": os.remove(f"messages/telegram/{file}")

class MyBot(commands.Bot):
    def __init__(self):
        with open('settings.yaml', 'r') as file:
            data = yaml.safe_load(file)
        app_id = data['discord']['app_id']
        super().__init__(command_prefix = ".", intents = discord.Intents.all(), application_id = app_id)

    async def close(self):
        await super().close()

    async def on_ready(self):
        asyncio.gather(detect_text_change(self), detect_new_files(self))


bot = MyBot()

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user: return

    with open('settings.yaml', 'r') as file:
        data = yaml.safe_load(file)
    targets = data['bridges']
    for target in targets:
        if message.channel.id == target['discord_chat_id']:
            chname = target['name']
            break
    else: return

    # Download the attachments if it's there
    if message.attachments:
        # if attachment.is_file():
        file_name, file_type = message.attachments[0].filename.split(".")
        if file_type == "webp": file_type = "png"
        file_count = 1
        file_path = f"messages/discord/{file_name}.{file_type}"
        while os.path.isfile(file_path): # Not working for some reason
            file_count += 1
            if os.path.isfile(f"messages/discord/{file_name}_({file_count}).{file_type}"): continue
            else: file_path = f"messages/discord/{file_name}_({file_count}).{file_type}"
        # Save attachment info in attachment.json
        json_file_path = "messages/discord/attachments.json"
        with open(json_file_path, "r", encoding = "utf8") as f:
            messages = json.load(f)
        with open(json_file_path, "w", encoding = "utf8") as f:
            sender = message.author.display_name
            messages["message"] = {}
            messages["message"]["path"] = file_path
            messages["message"]["sender"] = sender
            messages["message"]["chat"] = chname
            json.dump(messages, f, sort_keys = True, indent = 4, ensure_ascii = False)
        await message.attachments[0].save(fp=file_path)

    # Save text messages in text.json
    json_file_path = "messages/discord/text.json"
    with open(json_file_path, "r", encoding = "utf8") as f:
        messages = json.load(f)
    with open(json_file_path, "w", encoding = "utf8") as f:
        sender = message.author.display_name
        messages["message"] = {}
        messages["message"]["content"] = message.content
        messages["message"]["sender"] = sender
        messages["message"]["chat"] = chname
        json.dump(messages, f, sort_keys = True, indent = 4, ensure_ascii = False)

with open('settings.yaml', 'r') as file:
    data = yaml.safe_load(file)
token = data['discord']['token']

bot.run(token)
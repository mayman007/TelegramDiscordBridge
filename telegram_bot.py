from pyrogram import Client, filters, types
import json
import os
import asyncio
import yaml


with open('settings.yaml', 'r') as file:
    data = yaml.safe_load(file)
telegram_info = data['telegram']

api_id = telegram_info['api_id']
api_hash = telegram_info['api_hash']

app = Client("my_bot", api_id=api_id, api_hash=api_hash)

#I am alive
async def main():
    print("I am alive")
    asyncio.gather(detect_text_change(), detect_new_files())

# CHATS ID
with open('settings.yaml', 'r') as file:
    data = yaml.safe_load(file)
targets = data['bridges']
SOURCE_CHATS = []
for target in targets:
    SOURCE_CHATS.append(target['telegram_chat_id'])

filters.chat(SOURCE_CHATS)
@app.on_message(filters.chat(SOURCE_CHATS))
async def my_handler(client: Client, message: types.Message):
    # Check if chat is a target and get chname
    with open('settings.yaml', 'r') as file:
        data = yaml.safe_load(file)
    targets = data['bridges']
    for target in targets:
        if message.chat.id == target['telegram_chat_id']:
            chname = target['name']
            break
    else: return

    # Check if the message contains a media group
    if message.media_group_id:
        messages = await app.get_media_group(message.chat.id, message.id)
        for i, media in enumerate(messages):
            if media.document: file_name = media.document.file_name
            elif media.photo:
                file_name = "image"
                file_type = ".png"
            elif media.video:
                file_name = "video"
                file_type = ".mp4"
            elif media.audio:
                file_name = "audio"
                file_type = ".mp3"
            elif media.voice:
                file_name = "voice"
                file_type = ".mp3" # .ogg doesn't work for some reason
            file_path = f"messages/telegram/{file_name}_({i}){file_type}"
            # Save media group info in attachment.json
            json_file_path = "messages/telegram/attachments.json"
            with open(json_file_path, "r", encoding = "utf8") as f:
                messages = json.load(f)
            with open(json_file_path, "w", encoding = "utf8") as f:
                try: sender = message.from_user.first_name + " " + message.from_user.last_name
                except TypeError: sender = message.from_user.username
                except AttributeError: sender = chname
                messages["message"] = {}
                messages["message"]["path"] = file_path
                messages["message"]["sender"] = sender
                messages["message"]["chat"] = chname
                json.dump(messages, f, sort_keys = True, indent = 4, ensure_ascii = False)
            await client.download_media(media, file_name=file_path)
        # Save the caption if it's there
        if message.caption:
            json_file_path = "messages/telegram/text.json"
            with open(json_file_path, "r", encoding = "utf8") as f:
                messages = json.load(f)
            with open(json_file_path, "w", encoding = "utf8") as f:
                try: sender = message.from_user.first_name + " " + message.from_user.last_name
                except TypeError: sender = message.from_user.username
                except AttributeError: sender = chname
                messages["message"] = {}
                messages["message"]["content"] = message.caption
                messages["message"]["sender"] = sender
                messages["message"]["chat"] = chname
                json.dump(messages, f, sort_keys = True, indent = 4, ensure_ascii = False)

    # If message is an attachment
    elif message.media:
        # Download media in messages directory
        if message.document:
            file_name, file_type = message.document.file_name.split(".")
            file_type = f".{file_type}"
        elif message.photo:
            file_name = "image"
            file_type = ".png"
        elif message.video:
            file_name = "video"
            file_type = ".mp4"
        elif message.audio:
            file_name = "audio"
            file_type = ".mp3"
        elif message.voice:
            file_name = "voice"
            file_type = ".mp3" # .ogg doesn't work for some reason
        elif message.sticker:
            file_name = "sticker"
            file_type = ".webp"
        file_path = f"messages/telegram/{file_name}{file_type}"
        file_count = 1
        while os.path.isfile(file_path):
            file_count += 1
            if os.path.isfile(f"messages/telegram/{file_name}_({file_count}){file_type}"):
                continue
            else:
                file_path = f"messages/telegram/{file_name}_({file_count}){file_type}"
                break
        await client.download_media(message, file_path)

        # Save attachment info in attachment.json
        json_file_path = "messages/telegram/attachments.json"
        with open(json_file_path, "r", encoding = "utf8") as f:
            messages = json.load(f)
        with open(json_file_path, "w", encoding = "utf8") as f:
            try: sender = message.from_user.first_name + " " + message.from_user.last_name
            except TypeError: sender = message.from_user.username
            except AttributeError: sender = chname
            messages["message"] = {}
            messages["message"]["path"] = file_path
            messages["message"]["sender"] = sender
            messages["message"]["chat"] = chname
            json.dump(messages, f, sort_keys = True, indent = 4, ensure_ascii = False)

        # Save the caption if it's there
        if message.caption:
            caption = message.caption
            json_file_path = "messages/telegram/text.json"
            with open(json_file_path, "r", encoding = "utf8") as f:
                messages = json.load(f)
            with open(json_file_path, "w", encoding = "utf8") as f:
                try: sender = message.from_user.first_name + " " + message.from_user.last_name
                except TypeError: sender = message.from_user.username
                except AttributeError: sender = chname
                messages["message"] = {}
                messages["message"]["content"] = caption
                messages["message"]["sender"] = sender
                messages["message"]["chat"] = chname
                json.dump(messages, f, sort_keys = True, indent = 4, ensure_ascii = False)

    # If message is a text message
    else:
        # Save text messages in text.json
        replied_to = message.reply_to_message
        if replied_to == None:
            replied_to_text = "None"
            replied_to_sender = "None"
        else:
            replied_to_text = replied_to.text
            try: replied_to_sender = replied_to.from_user.first_name + " " + replied_to.from_user.last_name
            except TypeError: replied_to_sender = replied_to.from_user.username
            except AttributeError: replied_to_sender = chname
        json_file_path = "messages/telegram/text.json"
        with open(json_file_path, "r", encoding = "utf8") as f:
            messages = json.load(f)
        with open(json_file_path, "w", encoding = "utf8") as f:
            try: sender = message.from_user.first_name + " " + message.from_user.last_name
            except TypeError: sender = message.from_user.username
            except AttributeError: sender = chname
            messages["message"] = {}
            messages["message"]["content"] = message.text
            messages["message"]["sender"] = sender
            messages["message"]["chat"] = chname
            messages["message"]["replied_to_text"] = replied_to_text
            messages["message"]["replied_to_sender"] = replied_to_sender
            json.dump(messages, f, sort_keys = True, indent = 4, ensure_ascii = False)

async def check_chat(chat):
    with open('settings.yaml', 'r') as file:
        data = yaml.safe_load(file)
    targets = data['bridges']
    for target in targets:
        if chat == target['name']:
            chat_id = target['telegram_chat_id']
            return chat_id

async def detect_text_change():
    # async with app:
    json_file = "messages/discord/text.json"
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
            last_modified = new_modified
            if content == "": continue
            chat_id = await check_chat(chat)
            limit = 1800
            if len(content) > limit:
                whole_text = [content[i: i + limit] for i in range(0, len(content), limit)]
                for part_of_text in whole_text: await app.send_message(chat_id, f"**{sender}:**\n{part_of_text}")
            else: await app.send_message(chat_id, f"**{sender}:**\n{content}")

async def detect_new_files():
    while True:
        await asyncio.sleep(1)
        files_now = os.listdir("messages/discord")
        files_to_detect = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mp3", ".ogg", ".pdf", ".apk"]
        # Create a set of file extensions for faster membership check
        extensions = set(files_to_detect)
        # Check each file in files_now
        for file in files_now:
            # Extract the file extension
            file_extension = os.path.splitext(file)[1]
            if file_extension == ".temp": continue
            # Check if the extension is in the set of extensions
            if file_extension.lower() in extensions:
                with open('messages/discord/attachments.json', "r") as f:
                    data = json.load(f)
                # file_path = data["message"]["path"]
                file_path = f"messages/discord/{file}"
                sender = data["message"]["sender"]
                chat = data["message"]["chat"]
                chat_id = await check_chat(chat)
                if os.path.getsize(file_path) > 8388608:
                    await app.send_message(chat_id, f"*{sender}:* File size is over 8MB, so I can't send it. Sorry :(")
                else:
                    photos = [".png", ".jpg", ".jpeg", ".gif"]
                    for ext in photos:
                        if ext in file_path: await app.send_photo(chat_id, file_path, caption=f"**{sender}:**")
                    if ".mp4" in file_path: await app.send_video(chat_id, file_path, caption=f"**{sender}:**")
                    elif ".mp3" in file_path: await app.send_audio(chat_id, file_path, caption=f"**{sender}:**")
                    elif ".ogg" in file_path: await app.send_voice(chat_id, file_path, caption=f"**{sender}:**")
                    elif ".webp" in file_path:
                        os.remove(file_path)
                    elif ".pdf" in file_path or ".apk" in file_path: await app.send_document(chat_id, file_path, caption=f"**{sender}:**")
                os.remove(file_path)
            else:
                if file != "attachments.json" and file != "text.json":
                    os.remove(f"messages/discord/{file}")

app.run(main())
app.run()
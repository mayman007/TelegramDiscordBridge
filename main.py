import asyncio

async def run_file(file_name):
    print(f"Starting {file_name}...")
    process = await asyncio.create_subprocess_shell(f"python {file_name}", cwd=".")
    await process.wait()

def main():
    tasks = []
    tasks.append(run_file("telegram_bot.py"))
    tasks.append(run_file("discord_bot.py"))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
    main()

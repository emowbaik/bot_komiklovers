import os
import logging
import discord
import asyncio
from discord.ext import commands, tasks
from .utils import send_to_discord, get_role_mention
from .logging_config import setup_logging
from .commands import setup as setup_commands
from lib.http.db_utils import fetch_pending_entries, delete_pending_entry, get_last_entry_id, set_last_entry_id
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Inisialisasi bot dengan AutoShardedBot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True  # Add intents to receive messages
bot = commands.AutoShardedBot(command_prefix='!', intents=intents)

# Setup custom commands
setup_commands(bot)

@tasks.loop(minutes=1)
async def check_pending_entries():
    logging.info("Checking for pending entries...")
    pending_entries = fetch_pending_entries()
    
    # Log jumlah pending entries yang ditemukan
    logging.info(f"Found {len(pending_entries)} pending entries.")
    
    for entry in pending_entries:
        entry_id, published, title, link, author = entry
        
        # Log informasi dari setiap entry
        logging.info(f"Processing entry: ID={entry_id}, Title='{title}', Link='{link}', Published='{published}', Author='{author}'")
        
        role_mention = await get_role_mention(bot, title)
        if role_mention:
            await send_to_discord(bot, entry_id, title, link, published, author)
            delete_pending_entry(entry_id)
        else:
            logging.info(f"Role for '{title}' not found yet. Will retry later.")

# Event handler untuk menerima pesan dari bot lain
@bot.event
async def on_message(message):
    # Jangan merespon pesan dari diri sendiri
    if message.author == bot.user:
        return

    # Periksa apakah pesan berasal dari bot lain di channel tertentu
    if message.author.bot and message.channel.id == int(os.getenv('SOURCE_CHANNEL_ID')):
        logging.info(f"Message from the specified bot detected: {message.content}")
        # Uraikan konten pesan
        lines = message.content.split('\n')
        if len(lines) >= 4:
            title = lines[0]
            link = lines[1]
            author = lines[2]
            published = lines[3]
            entry_id = lines[4]

            logging.info(f"Extracted data - Title: {title}, Link: {link}, Author: {author}, Published: {published}, Id: {entry_id}")

            # Kirim pesan ke Discord
            await send_to_discord(bot, entry_id, title, link, published, author)

            # Simpan entri ke database
            set_last_entry_id(entry_id, published, title, link, author)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')
    if not check_pending_entries.is_running():
        check_pending_entries.start()  # Mulai pengecekan entri yang tertunda secara berkala jika belum berjalan

bot.run(os.getenv('DISCORD_TOKEN'))

import os
import json
import logging
import discord
import feedparser
import asyncio
from discord.ext import commands, tasks
from .utils import send_to_discord, get_role_mention
from .logging_config import setup_logging
from .commands import setup as setup_commands
from lib.http.db_utils import fetch_pending_entries, delete_pending_entry, get_last_entry_id, set_last_entry_id  # Import fungsi dari db_utils
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Muat data dari file JSON untuk roles
with open('roles.json') as f:
    entries_data = json.load(f)

# Inisialisasi bot dengan AutoShardedBot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.AutoShardedBot(command_prefix='!', intents=intents)

# Setup custom commands
setup_commands(bot)

# Fungsi untuk mengambil feed menggunakan run_in_executor
async def fetch_feed(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, feedparser.parse, url)

# Fungsi untuk mengambil feed dengan retry logic
async def fetch_feed_with_retry(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return await fetch_feed(url)
        except Exception as e:
            logging.error(f"Error fetching feed (attempt {attempt + 1}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

@tasks.loop(minutes=1)
async def check_pending_entries():
    logging.info("Checking for pending entries...")
    pending_entries = fetch_pending_entries()
    for entry in pending_entries:
        entry_id, published, title, link, author = entry
        role_mention = await get_role_mention(bot, title)
        if role_mention:
            await send_to_discord(bot, entry_id, title, link, published, author)
            delete_pending_entry(entry_id)
        else:
            logging.info(f"Role for '{title}' not found yet. Will retry later.")

# Fungsi untuk memeriksa feed dan mengirim update
@tasks.loop(minutes=1)
async def check_feed():
    try:
        logging.info('Checking feed...')
        new_feed = await asyncio.wait_for(fetch_feed_with_retry(os.getenv('RSS_URL')), timeout=60)
        last_entry_id = get_last_entry_id()
        new_entry = new_feed.entries[0]

        if new_entry.id != last_entry_id:
            title = new_entry.title
            link = new_entry.link
            author = new_entry.author
            published = new_entry.published

            set_last_entry_id(new_entry.id, published, title, link, author)

            logging.info(f"New entry found: {title}")

            await send_to_discord(bot, new_entry.id, title, link, published, author)
            logging.info(f"Successfully sent notification for: {title}")
        else:
            logging.info(f"No new entries found. Last entry ID {last_entry_id} is the same as the latest entry ID.")
    except asyncio.TimeoutError:
        logging.error('Timeout while fetching the feed')
    except Exception as e:
        logging.error(f"Error checking feed: {e}")

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')
    if not check_feed.is_running():
        check_feed.start()  # Mulai pengecekan feed secara berkala jika belum berjalan

    if not  check_pending_entries.is_running():
        check_pending_entries.start()  # Mulai pengecekan entri yang tertunda secara berkala jika belum berjalan

bot.run(os.getenv('DISCORD_TOKEN'))

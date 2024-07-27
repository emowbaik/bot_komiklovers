import asyncio
import logging
import feedparser
from .utils import send_to_discord
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def fetch_feed(url):
    return feedparser.parse(url)

def setup(bot):
    @bot.command(name='list')
    async def list_entries(ctx):
        try:
            feed = await asyncio.wait_for(fetch_feed(os.getenv('RSS_URL')), timeout=30)
            entries = feed.entries[:10]  # Ambil 10 artikel terbaru

            if not entries:
                await ctx.send("Tidak ada artikel yang ditemukan.")
                return

            entry_list = "\n".join([f"{i+1}. {entry.title}" for i, entry in enumerate(entries)])
            await ctx.send(f"Daftar artikel:\n{entry_list}\n\nGunakan perintah `!send <nomor>` untuk mengirim artikel yang dipilih.")

        except Exception as e:
            logging.error(f"Error fetching feed: {e}")
            await ctx.send(f"Terjadi kesalahan: {e}")

    @bot.command(name='send')
    async def send_entry(ctx, index: int):
        try:
            feed = await asyncio.wait_for(fetch_feed(os.getenv('RSS_URL')), timeout=60)
            entries = feed.entries[:10]  # Ambil 10 artikel terbaru
    
            if index < 1 or index > len(entries):
                await ctx.send("Nomor artikel tidak valid.")
                return
    
            entry = entries[index - 1]
            title = entry.title
            link = entry.link
            author = entry.author if 'author' in entry else 'Unknown'
            published = entry.published if 'published' in entry else 'Unknown'
    
            # Generate a unique entry_id, e.g., using the link or some other unique field
            entry_id = link  # Or another unique identifier
    
            # Contoh pemanggilan send_to_discord
            await send_to_discord(bot, entry_id, title, link, published, author)
            logging.info(f"Successfully sent notification for: {title}")
            await ctx.send(f"Artikel '{title}' telah dikirim ke Discord.")
    
        except Exception as e:
            logging.error(f"Error sending entry: {e}")
            await ctx.send(f"Terjadi kesalahan: {e}")

    @bot.command(name='sendall')
    async def send_all_entries(ctx):
        try:
            feed = await asyncio.wait_for(fetch_feed(os.getenv('RSS_URL')), timeout=60)
            entries = feed.entries[:10]  # Ambil 10 artikel terbaru
    
            if not entries:
                await ctx.send("Tidak ada artikel yang ditemukan untuk dikirim.")
                return
    
            for entry in entries:
                title = entry.title
                link = entry.link
                author = entry.author if 'author' in entry else 'Unknown'
                published = entry.published if 'published' in entry else 'Unknown'
    
                # Generate a unique entry_id, e.g., using the link or some other unique field
                entry_id = link  # Or another unique identifier
    
                await send_to_discord(bot, entry_id, title, link, published, author)
                logging.info(f"Successfully sent notification for: {title}")

            await ctx.send("Semua artikel telah dikirim ke Discord.")
    
        except Exception as e:
            logging.error(f"An error occurred while sending all entries: {e}")
            await ctx.send(f"Terjadi kesalahan: {e}")
import asyncio
import logging
import discord
from discord.ext import commands
from .utils import send_to_discord
from lib.http.db_utils import fetch_pending_entries, save_pending_entry
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def fetch_messages(bot, channel_id, limit=100):
    channel = bot.get_channel(channel_id)
    messages = await channel.history(limit=limit).flatten()
    return messages

def setup(bot):
    @bot.command(name='list')
    async def list_entries(ctx):
        try:
            messages = await fetch_messages(int(os.getenv('SOURCE_CHANNEL_ID')))
            entries = []

            for message in messages:
                lines = message.content.split('\n')
                if len(lines) >= 4:
                    title = lines[0]
                    link = lines[1]
                    author = lines[2]
                    published = lines[3]
                    entry_id = lines[4]
                    if entry_id not in [e[0] for e in fetch_pending_entries()]:
                        entries.append((title, link, published, author, entry_id))
            
            if not entries:
                await ctx.send("Tidak ada artikel yang ditemukan.")
                return

            entry_list = "\n".join([f"{i+1}. {entry[0]}" for i, entry in enumerate(entries)])
            await ctx.send(f"Daftar artikel:\n{entry_list}\n\nGunakan perintah `!send <nomor>` untuk mengirim artikel yang dipilih.")

        except Exception as e:
            logging.error(f"Error fetching messages: {e}")
            await ctx.send(f"Terjadi kesalahan: {e}")

    @bot.command(name='send')
    async def send_entry(ctx, index: int):
        try:
            messages = await fetch_messages(int(os.getenv('SOURCE_CHANNEL_ID')))
            entries = []

            for message in messages:
                lines = message.content.split('\n')
                if len(lines) >= 4:
                    title = lines[0]
                    link = lines[1]
                    author = lines[2]
                    published = lines[3]
                    entry_id = lines[4]
                    if entry_id not in [e[0] for e in fetch_pending_entries()]:
                        entries.append((title, link, published, author, entry_id))
            
            if index < 1 or index > len(entries):
                await ctx.send("Nomor artikel tidak valid.")
                return

            entry = entries[index - 1]
            title, link, published, author, entry_id = entry

            # Kirim pesan ke Discord
            await send_to_discord(bot, title, link, published, author)
            logging.info(f"Successfully sent notification for: {title}")

            # Simpan entri ke database
            save_pending_entry(entry_id, published, title, link, author)
            await ctx.send(f"Artikel '{title}' telah dikirim ke Discord.")
    
        except Exception as e:
            logging.error(f"Error sending entry: {e}")
            await ctx.send(f"Terjadi kesalahan: {e}")

    @bot.command(name='sendall')
    async def send_all_entries(ctx):
        try:
            messages = await fetch_messages(int(os.getenv('SOURCE_CHANNEL_ID')))
            entries = []

            for message in messages:
                lines = message.content.split('\n')
                if len(lines) >= 4:
                    title = lines[0]
                    link = lines[1]
                    author = lines[2]
                    published = lines[3]
                    entry_id = lines[4]
                    if entry_id not in [e[0] for e in fetch_pending_entries()]:
                        entries.append((title, link, published, author, entry_id))
            
            if not entries:
                await ctx.send("Tidak ada artikel yang ditemukan untuk dikirim.")
                return

            for entry in entries:
                title, link, published, author, entry_id = entry

                await send_to_discord(bot, title, link, published, author)
                logging.info(f"Successfully sent notification for: {title}")

                # Simpan entri ke database
                save_pending_entry(entry_id, published, title, link, author)

            await ctx.send("Semua artikel telah dikirim ke Discord.")
    
        except Exception as e:
            logging.error(f"An error occurred while sending all entries: {e}")
            await ctx.send(f"Terjadi kesalahan: {e}")

def setup_commands(bot):
    setup(bot)

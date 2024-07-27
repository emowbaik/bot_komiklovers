import os
from datetime import datetime
from dateutil import parser
import discord
import logging
import re
from lib.http.db_utils import save_pending_entry

# Fungsi untuk mengubah warna hex menjadi integer
def hex_to_int(hex_color):
    return int(hex_color.lstrip('#'), 16)

# Fungsi untuk menyederhanakan timestamp
# Fungsi untuk menyederhanakan timestamp
def simplify_timestamp(timestamp):
    # Jika timestamp adalah objek datetime, ubah menjadi string
    if isinstance(timestamp, datetime):
        timestamp = timestamp.isoformat()  # Mengubah datetime menjadi string ISO
    try:
        dt = parser.parse(timestamp)
        return dt.strftime('%d %B %Y, %H:%M %p')
    except Exception as e:
        logging.error(f"Failed to simplify timestamp: {e}")
        return "Invalid date"


# Fungsi untuk mengekstrak nama seri dari judul
def extract_series_name(title):
    # Misalnya, kita anggap nama seri adalah bagian dari judul sebelum "Chapter" atau "Episode"
    match = re.match(r'^(.*?)(?:Chapter \d+|Episode \d+)?$', title, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return title

# Fungsi untuk menentukan role mention berdasarkan title dari RSS feed
async def get_role_mention(bot, title):
    series_name = extract_series_name(title)
    # logging.info(f"Extracted series name: {series_name}")
    
    guild = bot.get_guild(int(os.getenv('GUILD_ID')))
    if not guild:
        logging.error("Guild not found.")
        return ""
    
    role = discord.utils.get(guild.roles, name=series_name)
    if role:
        logging.info(f"Role found: {role.name}")
        return role.mention
    else:
        logging.error(f"Role '{series_name}' not found in guild.")
        return ""

# Fungsi untuk mengirim pesan ke Discord dengan dua tombol
async def send_to_discord(bot, entry_id, title, link, published, author):
    role_mention = await get_role_mention(bot, title)
    
    if not role_mention:
        save_pending_entry(entry_id, published, title, link, author)
        # logging.info(f"Entry '{title}' saved as pending since role not found.")
        return
    
    simplified_time = simplify_timestamp(published)
    embed = discord.Embed(
        title=title,
        color=hex_to_int("#78478C")
    )
    embed.set_footer(text=f"Posted by {author} • {simplified_time}")

    button1 = discord.ui.Button(label="Baca Sekarang", url=link, style=discord.ButtonStyle.link)
    button2 = discord.ui.Button(label="Visit Site", url="https://komiklovers.com/", style=discord.ButtonStyle.link)

    view = discord.ui.View()
    view.add_item(button1)
    view.add_item(button2)

    channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
    if channel:
        try:
            await channel.send(content=f"<@&1226513877127397528>{role_mention} Read Now!", embed=embed, view=view)
        except discord.DiscordException as e:
            logging.error(f"Failed to send message: {e}")
    else:
        logging.error("Channel not found.")

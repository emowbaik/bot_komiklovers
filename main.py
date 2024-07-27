import logging

from lib.config.config import DISCORD_TOKEN
from lib.bot.bot import bot
from lib.bot.logging_config import setup_logging


# Setup logging
setup_logging()

logging.info("Starting bot...")
bot.run(DISCORD_TOKEN)

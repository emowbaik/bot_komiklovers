import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Menampilkan log di konsol
            logging.FileHandler('bot.log')  # Menyimpan log ke file bot.log
        ]
    )

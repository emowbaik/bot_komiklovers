import logging
import os
import certifi
import pymysql
from dotenv import load_dotenv

# Muat variabel lingkungan dari file .env
load_dotenv()

# Ambil konfigurasi dari variabel lingkungan
RSS_URL = os.getenv('RSS_URL')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Fungsi untuk mendapatkan koneksi database
def get_db_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        # logging.info("Database connection successful")
        return conn
    except pymysql.MySQLError as e:
        logging.error(f"Database connection failed: {e}")
        return None

# Set path sertifikat
os.environ['SSL_CERT_FILE'] = certifi.where()
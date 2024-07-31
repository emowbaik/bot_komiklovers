import logging
import pymysql
from datetime import datetime
from lib.config.config import get_db_connection
from dateutil import parser

# Fungsi untuk memformat tanggal
def format_datetime(date_string: str) -> str:
    try:
        dt = parser.parse(date_string)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        logging.error(f"Date format error: {date_string} - {e}")
        return None

# Fungsi untuk mendapatkan last_entry_id dari database
def get_last_entry_id() -> int:
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT entry_id FROM entries ORDER BY published DESC LIMIT 1')
            result = cursor.fetchone()
            logging.info(f"Fetched last_entry_id: {result[0] if result else 'None'}")
            return result[0] if result else None
        except pymysql.MySQLError as e:
            logging.error(f"Failed to fetch last_entry_id: {e}")
        finally:
            conn.close()
    else:
        logging.error("No database connection available")
    return None

# Fungsi untuk menyimpan entry_id, published, title, link, dan author ke database
def set_last_entry_id(entry_id: int, published: str, title: str, link: str, author: str):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            formatted_published = format_datetime(published)
            if formatted_published:
                cursor.execute(
                    '''
                    INSERT INTO entries (entry_id, published, title, link, author) 
                    VALUES (%s, %s, %s, %s, %s) 
                    ON DUPLICATE KEY UPDATE published=%s, title=%s, link=%s, author=%s
                    ''',
                    (entry_id, formatted_published, title, link, author, formatted_published, title, link, author)
                )
                conn.commit()
                logging.info(f"Set entry_id {entry_id} with published date {formatted_published}, title {title}, link {link}, and author {author}")
        except pymysql.MySQLError as e:
            logging.error(f"Failed to save entry_id {entry_id} to database: {e}")
        finally:
            conn.close()
    else:
        logging.error("No database connection available")

# Fungsi untuk menyimpan entri yang tertunda ke database
def save_pending_entry(entry_id: int, published: str, title: str, link: str, author: str):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            formatted_published = format_datetime(published)
            if formatted_published:
                cursor.execute(
                    '''
                    INSERT INTO pending_entries (entry_id, published, title, link, author) 
                    VALUES (%s, %s, %s, %s, %s) 
                    ON DUPLICATE KEY UPDATE published=%s, title=%s, link=%s, author=%s
                    ''',
                    (entry_id, formatted_published, title, link, author, formatted_published, title, link, author)
                )
                conn.commit()
                logging.info(f"Saved pending entry {entry_id}")
        except pymysql.MySQLError as e:
            logging.error(f"Failed to save pending entry {entry_id}: {e}")
        finally:
            conn.close()
    else:
        logging.error("No database connection available")

# Fungsi untuk mengambil entri yang tertunda dari database
def fetch_pending_entries() -> list:
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT entry_id, published, title, link, author FROM pending_entries')
            entries = cursor.fetchall()
            logging.info(f"Fetched {len(entries)} pending entries")
            return entries
        except pymysql.MySQLError as e:
            logging.error(f"Failed to fetch pending entries: {e}")
        finally:
            conn.close()
    else:
        logging.error("No database connection available")
    return []

# Fungsi untuk menghapus entri yang telah dikirim dari database
def delete_pending_entry(entry_id: int):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM pending_entries WHERE entry_id = %s', (entry_id,))
            conn.commit()
            logging.info(f"Deleted pending entry {entry_id}")
        except pymysql.MySQLError as e:
            logging.error(f"Failed to delete pending entry {entry_id}: {e}")
        finally:
            conn.close()
    else:
        logging.error("No database connection available")

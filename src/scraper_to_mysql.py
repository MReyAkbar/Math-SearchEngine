import mysql.connector
from web_scraper import crawl_site

def connect_to_mysql():
    return mysql.connector.connect(
        host='localhost', user='root', password='yourpassword', database='yourdatabase'
    )

def setup_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url TEXT UNIQUE,
            title TEXT,
            content LONGTEXT
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            from_url TEXT,
            to_url TEXT
        );
    ''')
    conn.commit()
    cursor.close()

def save_to_mysql(pages, links):
    conn = connect_to_mysql()
    setup_tables(conn)
    cursor = conn.cursor()

    for url, data in pages.items():
        cursor.execute("""
            INSERT IGNORE INTO pages (url, title, content)
            VALUES (%s, %s, %s)
        """, (url, data['title'], data['content']))

    for from_url, to_url in links:
        cursor.execute("""
            INSERT INTO links (from_url, to_url)
            VALUES (%s, %s)
        """, (from_url, to_url))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    start_url = "https://www.um.ac.id/"
    pages, links = crawl_site(start_url)
    save_to_mysql(pages, links)
    print("Data scraping berhasil disimpan ke MySQL.")

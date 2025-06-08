# src/database.py

import pymysql
from pymysql import Error
import json

def create_connection():
    """Create and return MySQL connection using PyMySQL"""
    try:
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='um_search_engine',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Error as e:
        print(f"Error connecting to MySQL (using PyMySQL): {e}")
        return None

def setup_all_tables():
    """Setup all required tables for the search system"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    url TEXT,
                    title TEXT,
                    content LONGTEXT,
                    pagerank FLOAT DEFAULT 0.0,
                    tfidf_scores TEXT
                );
            ''')
            try:
                cursor.execute("ALTER TABLE pages ADD UNIQUE (url(255))")
            except Error:
                pass
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS links (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    from_url TEXT,
                    to_url TEXT
                );
            ''')
        conn.commit()
        print("All tables created or already exist.")
        return True
    except Error as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        if conn:
            conn.close()

def save_scraped_data_to_mysql(pages, links):
    """Save scraped pages and links to MySQL"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
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
        print("Scraped data saved successfully.")
        return True
    except Error as e:
        print(f"Error saving scraped data: {e}")
        return False
    finally:
        if conn:
            conn.close()

def fetch_pages_for_processing():
    """Fetch pages from database for TF-IDF processing"""
    conn = create_connection()
    if not conn: return {}
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, content FROM pages")
            pages = {row['id']: row['content'] for row in cursor.fetchall()}
            return pages
    except Error as e:
        print(f"Error fetching pages: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def fetch_links_for_pagerank():
    """Fetch links from database and create adjacency matrix"""
    conn = create_connection()
    if not conn: return None, None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT id, url FROM pages")
            results = cursor.fetchall()
            url_to_id = {row['url']: row['id'] for row in results}
            id_to_url = {v: k for k, v in url_to_id.items()} # Mapping sebaliknya
            
            # Buat ID internal 0, 1, 2, ... untuk matriks
            internal_ids = {page_id: i for i, page_id in enumerate(id_to_url.keys())}
            
            n = len(internal_ids)
            adj_matrix = [[0] * n for _ in range(n)]
            
            cursor.execute("SELECT from_url, to_url FROM links")
            for link in cursor.fetchall():
                from_url, to_url = link['from_url'], link['to_url']
                if from_url in url_to_id and to_url in url_to_id:
                    from_page_id = url_to_id[from_url]
                    to_page_id = url_to_id[to_url]
                    
                    if from_page_id in internal_ids and to_page_id in internal_ids:
                        i = internal_ids[from_page_id]
                        j = internal_ids[to_page_id]
                        adj_matrix[i][j] = 1
            
            return adj_matrix, internal_ids, id_to_url
            
    except Error as e:
        print(f"Error fetching links: {e}")
        return None, None, None
    finally:
        if conn:
            conn.close()

def update_page_scores_in_db(pagerank_scores, tfidf_scores, internal_ids, id_to_url):
    """Update pagerank and tfidf_scores directly in the pages table."""
    conn = create_connection()
    if not conn: return False
    
    try:
        with conn.cursor() as cursor:
            internal_id_to_page_id = {v: k for k, v in internal_ids.items()}

            all_page_ids = set(internal_ids.keys())
            
            for page_id in all_page_ids:
                internal_id = internal_ids[page_id]
                
                pagerank_val = pagerank_scores.get(internal_id, 0.0)
                tfidf_dict = tfidf_scores.get(page_id, {})
                tfidf_json_str = json.dumps(tfidf_dict)
                
                cursor.execute("""
                    UPDATE pages 
                    SET pagerank = %s, tfidf_scores = %s 
                    WHERE id = %s
                """, (float(pagerank_val), tfidf_json_str, page_id))
        
        conn.commit()
        print(f"Berhasil memperbarui skor untuk {cursor.rowcount} baris di tabel 'pages'.")
        return True
    except Error as e:
        print(f"Error saat memperbarui skor di tabel pages: {e}")
        return False
    finally:
        if conn:
            conn.close()
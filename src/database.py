import mysql.connector
from mysql.connector import Error


def create_connection():
    """Create and return MySQL connection"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',  # Update with your credentials
            password='yourpassword',  # Update with your credentials
            database='yourdatabase'  # Update with your database name
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def setup_all_tables():
    """Setup all required tables for the search system"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Pages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT,
                content LONGTEXT,
                pagerank FLOAT DEFAULT 0.0
            );
        ''')
        
        # Links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INT AUTO_INCREMENT PRIMARY KEY,
                from_url TEXT,
                to_url TEXT
            );
        ''')
        
        # Combined scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_scores (
                page_id INT PRIMARY KEY,
                pagerank FLOAT,
                tfidf TEXT
            );
        ''')
        
        # Separate PageRank scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagerank_scores (
                page_id INT PRIMARY KEY,
                score FLOAT
            );
        ''')
        
        # Separate TF-IDF scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tfidf_scores (
                page_id INT PRIMARY KEY,
                scores TEXT
            );
        ''')
        
        conn.commit()
        print("All tables created successfully")
        return True
        
    except Error as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def save_scores_to_mysql(pagerank_scores, tfidf_scores):
    """Save PageRank and TF-IDF scores to MySQL database"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        for page_id in pagerank_scores:
            if page_id in tfidf_scores:
                tfidf_str = ', '.join(f"{word}:{score:.4f}" for word, score in tfidf_scores[page_id].items())
                cursor.execute(
                    "REPLACE INTO page_scores (page_id, pagerank, tfidf) VALUES (%s, %s, %s)",
                    (page_id, pagerank_scores[page_id], tfidf_str)
                )
        
        conn.commit()
        print("Scores saved successfully to page_scores table")
        return True
        
    except Error as e:
        print(f"Error saving scores: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def save_pagerank_to_db(pagerank_scores):
    """Save only PageRank scores to database"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        for page_id, score in pagerank_scores.items():
            cursor.execute(
                "REPLACE INTO pagerank_scores (page_id, score) VALUES (%s, %s)",
                (page_id, score)
            )
        
        conn.commit()
        print("PageRank scores saved successfully")
        return True
        
    except Error as e:
        print(f"Error saving PageRank scores: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def save_tfidf_to_db(tfidf_scores):
    """Save only TF-IDF scores to database"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        for page_id, scores in tfidf_scores.items():
            tfidf_str = ', '.join(f"{word}:{score:.4f}" for word, score in scores.items())
            cursor.execute(
                "REPLACE INTO tfidf_scores (page_id, scores) VALUES (%s, %s)",
                (page_id, tfidf_str)
            )
        
        conn.commit()
        print("TF-IDF scores saved successfully")
        return True
        
    except Error as e:
        print(f"Error saving TF-IDF scores: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def save_scraped_data_to_mysql(pages, links):
    """Save scraped pages and links to MySQL"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Save pages
        for url, data in pages.items():
            cursor.execute("""
                INSERT IGNORE INTO pages (url, title, content)
                VALUES (%s, %s, %s)
            """, (url, data['title'], data['content']))
        
        # Save links
        for from_url, to_url in links:
            cursor.execute("""
                INSERT INTO links (from_url, to_url)
                VALUES (%s, %s)
            """, (from_url, to_url))
        
        conn.commit()
        print("Scraped data saved successfully")
        return True
        
    except Error as e:
        print(f"Error saving scraped data: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def fetch_pages_for_processing():
    """Fetch pages from database for TF-IDF processing"""
    conn = create_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, content FROM pages")
        pages = {row[0]: row[1] for row in cursor.fetchall()}
        return pages
        
    except Error as e:
        print(f"Error fetching pages: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()


def fetch_links_for_pagerank():
    """Fetch links from database and create adjacency matrix"""
    conn = create_connection()
    if not conn:
        return None, None
    
    try:
        cursor = conn.cursor()
        
        # Get all unique URLs and create ID mapping
        cursor.execute("SELECT DISTINCT url FROM pages")
        urls = [row[0] for row in cursor.fetchall()]
        url_to_id = {url: idx for idx, url in enumerate(urls)}
        
        n = len(urls)
        adj_matrix = [[0] * n for _ in range(n)]
        
        # Fill adjacency matrix based on links
        cursor.execute("SELECT from_url, to_url FROM links")
        for from_url, to_url in cursor.fetchall():
            if from_url in url_to_id and to_url in url_to_id:
                i = url_to_id[from_url]
                j = url_to_id[to_url]
                adj_matrix[i][j] = 1
        
        return adj_matrix, url_to_id
        
    except Error as e:
        print(f"Error fetching links: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()
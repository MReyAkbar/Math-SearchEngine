import mysql.connector


def create_connection():
    """Create and return MySQL connection"""
    return mysql.connector.connect(
        user='your_username', 
        password='your_password', 
        host='localhost', 
        database='your_database'
    )


def save_scores_to_mysql(pagerank_scores, tfidf_scores):
    """Save PageRank and TF-IDF scores to MySQL database"""
    conn = create_connection()
    cursor = conn.cursor()

    # Pastikan tabel sudah dibuat:
    # CREATE TABLE page_scores (page_id INT PRIMARY KEY, pagerank FLOAT, tfidf TEXT);

    for page_id in pagerank_scores:
        tfidf_str = ', '.join(f"{word}:{score:.4f}" for word, score in tfidf_scores[page_id].items())
        cursor.execute(
            "REPLACE INTO page_scores (page_id, pagerank, tfidf) VALUES (%s, %s, %s)",
            (page_id, pagerank_scores[page_id], tfidf_str)
        )

    conn.commit()
    cursor.close()
    conn.close()
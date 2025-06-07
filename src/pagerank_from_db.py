import mysql.connector
from pagerank import pagerank

def connect_to_mysql():
    return mysql.connector.connect(
        host='localhost', user='root', password='yourpassword', database='yourdatabase'
    )

def fetch_links(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM pages")
    id_url_map = {url: idx for idx, url in cursor.fetchall()}

    n = len(id_url_map)
    adj_matrix = [[0] * n for _ in range(n)]

    cursor.execute("SELECT from_url, to_url FROM links")
    for from_url, to_url in cursor.fetchall():
        if from_url in id_url_map and to_url in id_url_map:
            i = id_url_map[from_url]
            j = id_url_map[to_url]
            adj_matrix[i][j] = 1

    cursor.close()
    return adj_matrix, id_url_map

def update_pagerank_scores(conn, ranks, id_url_map):
    cursor = conn.cursor()
    url_id_map = {v: k for k, v in id_url_map.items()}
    for i, score in enumerate(ranks):
        url = url_id_map[i]
        cursor.execute("UPDATE pages SET pagerank = %s WHERE url = %s", (float(score), url))
    conn.commit()
    cursor.close()

if __name__ == "__main__":
    conn = connect_to_mysql()
    adj_matrix, id_url_map = fetch_links(conn)
    ranks = pagerank(adj_matrix)
    update_pagerank_scores(conn, ranks, id_url_map)
    print("PageRank berhasil dihitung dan disimpan ke database.")

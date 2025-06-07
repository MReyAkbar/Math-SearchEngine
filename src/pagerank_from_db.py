from pagerank import pagerank
from database import create_connection, fetch_links_for_pagerank, save_pagerank_to_db
from mysql.connector import Error


def update_pagerank_in_pages_table(pagerank_scores, url_to_id):
    """Update PageRank scores directly in the pages table"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        id_to_url = {v: k for k, v in url_to_id.items()}
        
        for page_id, score in pagerank_scores.items():
            if page_id in id_to_url:
                url = id_to_url[page_id]
                cursor.execute("UPDATE pages SET pagerank = %s WHERE url = %s", (float(score), url))
        
        conn.commit()
        print("PageRank scores updated in pages table")
        return True
        
    except Error as e:
        print(f"Error updating PageRank in pages table: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def main():
    """Main function to calculate and save PageRank from database"""
    print("Fetching links from database...")
    adj_matrix, url_to_id = fetch_links_for_pagerank()
    
    if adj_matrix is None or url_to_id is None:
        print("Failed to fetch links from database")
        return
    
    print(f"Processing {len(url_to_id)} pages...")
    
    # Calculate PageRank
    ranks = pagerank(adj_matrix)
    
    # Convert to dictionary format
    pagerank_scores = {i: float(rank) for i, rank in enumerate(ranks)}
    
    # Save PageRank scores
    if save_pagerank_to_db(pagerank_scores):
        print("PageRank scores saved to pagerank_scores table")
    
    # Also update the main pages table
    if update_pagerank_in_pages_table(pagerank_scores, url_to_id):
        print("PageRank scores updated in pages table")
    
    # Print results
    print("\nTop 5 PageRank Scores:")
    id_to_url = {v: k for k, v in url_to_id.items()}
    sorted_scores = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for page_id, score in sorted_scores:
        url = id_to_url.get(page_id, f"Page {page_id}")
        print(f"{score:.4f}: {url}")


if __name__ == "__main__":
    main()
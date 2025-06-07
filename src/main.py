from pagerank import pagerank
from tfidf import compute_tfidf
from database import (
    create_connection, save_scores_to_mysql, fetch_pages_for_processing, 
    fetch_links_for_pagerank, setup_all_tables
)


def run_example_with_static_data():
    """Run the algorithm with static example data"""
    print("Running with static example data...")
    
    # Contoh adjacency matrix untuk 5 halaman
    adj_matrix = [
        [0, 1, 1, 0, 0],  # Halaman 0 menautkan ke 1 dan 2
        [1, 0, 0, 1, 0],  # Halaman 1 menautkan ke 0 dan 3
        [0, 1, 0, 0, 1],  # Halaman 2 menautkan ke 1 dan 4
        [0, 0, 0, 0, 1],  # Halaman 3 menautkan ke 4
        [1, 0, 0, 1, 0],  # Halaman 4 menautkan ke 0 dan 3
    ]

    # Contoh isi halaman - menggunakan dictionary format
    pages = {
        0: "Mesin pencari menggunakan algoritma PageRank",
        1: "PageRank dikembangkan oleh Google",
        2: "Algoritma PageRank memperhitungkan link",
        3: "TF-IDF adalah metode untuk mengukur relevansi kata",
        4: "Kata yang sering muncul memiliki bobot tinggi dalam TF"
    }

    # Hitung skor PageRank
    ranks = pagerank(adj_matrix)
    pagerank_scores = {i: float(rank) for i, rank in enumerate(ranks)}

    # Hitung skor TF-IDF
    tfidf_scores = compute_tfidf(pages)

    # Print results
    print("\nPageRank Scores:")
    for page_id, score in pagerank_scores.items():
        print(f"Page {page_id}: {score:.4f}")

    print("\nTF-IDF Scores (top words per page):")
    for page_id, scores in tfidf_scores.items():
        top_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"Page {page_id}: {top_words}")

    # Save to database if tables exist
    if save_scores_to_mysql(pagerank_scores, tfidf_scores):
        print("\nSkor PageRank dan TF-IDF berhasil disimpan ke database.")


def run_with_database_data():
    """Run the algorithm with data from database"""
    print("Running with database data...")
    
    # Fetch pages for TF-IDF
    pages = fetch_pages_for_processing()
    if not pages:
        print("No pages found in database. Run scraper first.")
        return
    
    # Fetch links for PageRank
    adj_matrix, url_to_id = fetch_links_for_pagerank()
    if adj_matrix is None:
        print("No links found in database. Run scraper first.")
        return
    
    print(f"Processing {len(pages)} pages and {len(url_to_id)} URLs...")
    
    # Calculate PageRank
    ranks = pagerank(adj_matrix)
    pagerank_scores = {i: float(rank) for i, rank in enumerate(ranks)}
    
    # Calculate TF-IDF
    tfidf_scores = compute_tfidf(pages)
    
    # Print top results
    print("\nTop 5 PageRank Scores:")
    id_to_url = {v: k for k, v in url_to_id.items()}
    sorted_pagerank = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    for page_id, score in sorted_pagerank:
        url = id_to_url.get(page_id, f"Page {page_id}")
        print(f"{score:.4f}: {url}")
    
    print("\nTop TF-IDF words from first 3 pages:")
    for page_id in list(tfidf_scores.keys())[:3]:
        if tfidf_scores[page_id]:
            top_words = sorted(tfidf_scores[page_id].items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"Page {page_id}: {top_words}")
    
    # Save combined scores
    if save_scores_to_mysql(pagerank_scores, tfidf_scores):
        print("\nSkor berhasil disimpan ke database.")


def main():
    """Main function with options"""
    print("=== PageRank & TF-IDF Search System ===")
    print("1. Run with static example data")
    print("2. Run with database data (requires scraped data)")
    print("3. Setup database tables")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        run_example_with_static_data()
    elif choice == "2":
        run_with_database_data()
    elif choice == "3":
        if setup_all_tables():
            print("Database tables setup successfully!")
        else:
            print("Failed to setup database tables.")
    else:
        print("Invalid choice. Running with static data by default.")
        run_example_with_static_data()


if __name__ == "__main__":
    main()
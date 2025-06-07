from pagerank import pagerank
from tfidf import compute_tfidf
from database import save_scores_to_mysql

# Contoh adjacency matrix untuk 5 halaman
adj_matrix = [
    [0, 1, 1, 0, 0],  # Halaman 0 menautkan ke 1 dan 2
    [1, 0, 0, 1, 0],  # Halaman 1 menautkan ke 0 dan 3
    [0, 1, 0, 0, 1],  # Halaman 2 menautkan ke 1 dan 4
    [0, 0, 0, 0, 1],  # Halaman 3 menautkan ke 4
    [1, 0, 0, 1, 0],  # Halaman 4 menautkan ke 0 dan 3
]

# Contoh isi halaman - FIXED: menggunakan dictionary format
pages = {
    0: "Mesin pencari menggunakan algoritma PageRank",
    1: "PageRank dikembangkan oleh Google",
    2: "Algoritma PageRank memperhitungkan link",
    3: "TF-IDF adalah metode untuk mengukur relevansi kata",
    4: "Kata yang sering muncul memiliki bobot tinggi dalam TF"
}

# Hitung skor PageRank
ranks = pagerank(adj_matrix)

# Convert ranks array to dictionary for consistency
pagerank_scores = {i: float(rank) for i, rank in enumerate(ranks)}

# Hitung skor TF-IDF
tfidf_scores = compute_tfidf(pages)

# Simpan ke database MySQL
save_scores_to_mysql(pagerank_scores, tfidf_scores)
print("Skor PageRank dan TF-IDF berhasil disimpan ke database.")

# Print results for verification
print("\nPageRank Scores:")
for page_id, score in pagerank_scores.items():
    print(f"Page {page_id}: {score:.4f}")

print("\nTF-IDF Scores (top words per page):")
for page_id, scores in tfidf_scores.items():
    top_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"Page {page_id}: {top_words}")
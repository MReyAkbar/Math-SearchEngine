from pagerank import pagerank
from tfidf import compute_tfidf
from database import connect_to_mysql, save_scores_to_mysql

# Contoh adjacency matrix untuk 5 halaman
adj_matrix = [
    [0, 1, 1, 0, 0],  # Halaman 0 menautkan ke 1 dan 2
    [1, 0, 0, 1, 0],  # Halaman 1 menautkan ke 0 dan 3
    [0, 1, 0, 0, 1],  # Halaman 2 menautkan ke 1 dan 4
    [0, 0, 0, 0, 1],  # Halaman 3 menautkan ke 4
    [1, 0, 0, 1, 0],  # Halaman 4 menautkan ke 0 dan 3
]

# Contoh isi halaman
pages = [
    "Mesin pencari menggunakan algoritma PageRank",
    "PageRank dikembangkan oleh Google",
    "Algoritma PageRank memperhitungkan link",
    "TF-IDF adalah metode untuk mengukur relevansi kata",
    "Kata yang sering muncul memiliki bobot tinggi dalam TF"
]

# Hitung skor PageRank
ranks = pagerank(adj_matrix)

# Hitung skor TF-IDF
tfidf_scores = compute_tfidf(pages)

# Simpan ke database MySQL
conn = connect_to_mysql()
save_scores_to_mysql(conn, ranks, tfidf_scores)
print("Skor PageRank dan TF-IDF berhasil disimpan ke database.")

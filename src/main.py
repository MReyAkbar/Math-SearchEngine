# src/main.py

from pagerank import pagerank
from tfidf import compute_tfidf
from database import (
    fetch_pages_for_processing, 
    fetch_links_for_pagerank, 
    setup_all_tables,
    update_page_scores_in_db  # Pastikan ini diimpor
)
import json

def run_with_database_data():
    """Menjalankan algoritma dengan data dari database."""
    print("Menjalankan dengan data dari database...")
    
    # 1. Mengambil data halaman untuk diproses TF-IDF
    #    Struktur: { page_id_dari_db: content }
    pages_for_tfidf = fetch_pages_for_processing()
    if not pages_for_tfidf:
        print("Tidak ada halaman ditemukan di database. Jalankan scraper terlebih dahulu.")
        return
    
    # 2. Mengambil data link untuk PageRank
    #    Struktur baru: adj_matrix, internal_ids, id_to_url
    #    internal_ids: { page_id_dari_db: internal_id_matriks (0, 1, 2...) }
    #    id_to_url: { page_id_dari_db: url }
    adj_matrix, internal_ids, id_to_url = fetch_links_for_pagerank()
    if adj_matrix is None:
        print("Tidak ada link ditemukan di database. Jalankan scraper terlebih dahulu.")
        return
    
    print(f"Memproses {len(pages_for_tfidf)} halaman dan {len(adj_matrix)} node untuk PageRank...")
    
    # 3. Menghitung PageRank
    #    Hasilnya adalah array numpy berdasarkan urutan internal_id_matriks
    ranks = pagerank(adj_matrix)
    #    Struktur: { internal_id_matriks: score }
    pagerank_scores = {i: float(rank) for i, rank in enumerate(ranks)}
    
    # 4. Menghitung TF-IDF
    #    Struktur: { page_id_dari_db: { kata: skor_tfidf } }
    tfidf_scores = compute_tfidf(pages_for_tfidf)
    
    # 5. Menampilkan hasil teratas (opsional)
    print("\nTop 5 Halaman Berdasarkan PageRank:")
    # Mapping dari internal_id kembali ke page_id lalu ke url
    internal_id_to_page_id = {v: k for k, v in internal_ids.items()}
    sorted_pagerank = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for internal_id, score in sorted_pagerank:
        page_id = internal_id_to_page_id.get(internal_id)
        if page_id and page_id in id_to_url:
            url = id_to_url[page_id]
            print(f"{score:.4f}: {url}")
    
    # 6. Menyimpan skor gabungan ke database
    #    Menggunakan fungsi baru dengan parameter yang sesuai
    if update_page_scores_in_db(pagerank_scores, tfidf_scores, internal_ids, id_to_url):
        print("\nSkor PageRank dan TF-IDF berhasil diperbarui di tabel 'pages'.")
    else:
        print("\nGagal memperbarui skor di database.")


def main():
    """Fungsi utama dengan pilihan menu."""
    print("\n=== Sistem Pencari PageRank & TF-IDF ===")
    print("1. Jalankan dengan data contoh statis (tidak terhubung database)")
    print("2. Proses data dari database (wajib ada data hasil scrape)")
    print("3. Setup tabel di database")
    
    choice = input("\nMasukkan pilihan Anda (1-3): ").strip()
    
    if choice == "1":
        # Fungsi run_example_with_static_data() tidak diubah, jadi bisa dihapus atau dibiarkan
        print("Opsi 1 belum diimplementasikan di versi ini.")
        pass
    elif choice == "2":
        run_with_database_data()
    elif choice == "3":
        if setup_all_tables():
            print("Setup tabel database berhasil!")
        else:
            print("Gagal melakukan setup tabel database.")
    else:
        print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()
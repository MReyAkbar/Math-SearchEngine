# app.py

from flask import Flask, render_template, request
from models import db, Page
import json
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/um_search_engine'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def preprocess_query(query):
    """Membersihkan dan memecah query menjadi kata-kata (token)."""
    if not query:
        return []
    return re.findall(r'\w+', query.lower())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    query_tokens = preprocess_query(query)

    if not query_tokens:
        return render_template('results.html', results=[], query=query)

    # 1. Ambil kandidat halaman dari database yang mengandung kata kunci pertama
    search_pattern = f'%{query_tokens[0]}%'
    candidate_pages = Page.query.filter(Page.content.like(search_pattern)).all()

    ranked_results = []
    for page in candidate_pages:
        # 2. Hitung skor relevansi TF-IDF
        relevance_score = 0.0
        if page.tfidf_scores:
            try:
                # Muat data JSON dari skor TF-IDF yang tersimpan
                doc_tfidf = json.loads(page.tfidf_scores)
                for token in query_tokens:
                    relevance_score += doc_tfidf.get(token, 0.0)
            except (json.JSONDecodeError, TypeError):
                pass

        # Jangan proses halaman yang tidak relevan sama sekali
        if relevance_score == 0.0:
            continue

        # 3. Gabungkan dengan PageRank
        # Bobot bisa disesuaikan. Misal 30% PageRank, 70% Relevansi
        final_score = (0.3 * (page.pagerank_score or 0.0)) + (0.7 * relevance_score)

        ranked_results.append({'page': page, 'score': final_score})

    # 4. Urutkan hasil berdasarkan skor akhir
    sorted_results = sorted(ranked_results, key=lambda x: x['score'], reverse=True)

    # Ambil objek 'page' saja untuk di-render
    final_page_results = [result['page'] for result in sorted_results]

    return render_template('results.html', results=final_page_results, query=query, result_count=len(final_page_results))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
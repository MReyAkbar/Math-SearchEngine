from flask import Flask, render_template, request
from models import db, Page

app = Flask(__name__)
# Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/um_search_engine'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q') # Ambil keyword dari URL (?q=keyword)

    # Cari di database: page yang kontennya mengandung query
    # Urutkan berdasarkan pagerank_score yang sudah dihitung sebelumnya
    results = Page.query.filter(Page.content.like(f'%{query}%')) \
                        .order_by(Page.pagerank_score.desc()) \
                        .all()

    return render_template('results.html', results=results, query=query)

if __name__ == '__main__':
    # Baris ini penting agar Anda bisa membuat database pertama kali
    with app.app_context():
        db.create_all()
    app.run(debug=True)
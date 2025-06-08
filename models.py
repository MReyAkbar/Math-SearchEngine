from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    pagerank = db.Column(db.Float, default=1.0)
    tfidf_scores = db.Column(db.Text, nullable=True) # Untuk menyimpan JSON TF-IDF

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    target_page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
import math
from collections import defaultdict

def compute_tf(doc):
    tf = defaultdict(int)
    words = doc.lower().split()
    for word in words:
        tf[word] += 1
    total_words = len(words)
    for word in tf:
        tf[word] /= total_words
    return tf

def compute_idf(all_docs):
    idf = defaultdict(float)
    N = len(all_docs)
    all_words = set(word for doc in all_docs.values() for word in doc.lower().split())
    for word in all_words:
        df = sum(1 for doc in all_docs.values() if word in doc.lower().split())
        idf[word] = math.log(N / (1 + df))
    return idf

def compute_tfidf(documents):
    idf = compute_idf(documents)
    tfidf_scores = {}
    for doc_id, doc in documents.items():
        tf = compute_tf(doc)
        tfidf = {word: tf[word] * idf[word] for word in tf}
        tfidf_scores[doc_id] = tfidf
    return tfidf_scores
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and "um.ac.id" in parsed.netloc

def crawl_site(start_url, max_pages=20):
    visited = set()
    to_visit = [start_url]
    pages = {}
    links = []  # (from_url, to_url)

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            print(f"Crawling: {url}")
            response = requests.get(url, timeout=5)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else url
            content = soup.get_text(separator=" ", strip=True)
            pages[url] = {"title": title, "content": content}

            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])
                if is_valid_url(link):
                    links.append((url, link))
                    if link not in visited and link not in to_visit:
                        to_visit.append(link)

            visited.add(url)
            time.sleep(1)  # sopan ke server
        except Exception as e:
            print(f"Gagal membuka {url}: {e}")
            continue

    return pages, links

# Contoh penggunaan
if __name__ == "__main__":
    start = "https://www.um.ac.id/"
    page_data, link_data = crawl_site(start)
    print(f"Total halaman dikunjungi: {len(page_data)}")
    for i, (url, data) in enumerate(page_data.items()):
        print(f"[{i}] {url} => Judul: {data['title'][:50]}")

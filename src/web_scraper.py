import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re


def is_valid_url(url, base_domain="um.ac.id"):
    """Check if URL is valid and belongs to the target domain"""
    try:
        parsed = urlparse(url)
        return (bool(parsed.netloc) and 
                bool(parsed.scheme) and 
                base_domain in parsed.netloc and
                not any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js']))
    except:
        return False


def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep Indonesian characters
    text = re.sub(r'[^\w\s\-.,!?()]', ' ', text)
    return text.strip()


def extract_content(soup):
    """Extract meaningful content from HTML"""
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # Try to find main content areas
    content_selectors = [
        'main', 'article', '.content', '#content', 
        '.post-content', '.entry-content', 'section'
    ]
    
    content = ""
    for selector in content_selectors:
        elements = soup.select(selector)
        if elements:
            content = ' '.join([elem.get_text(separator=" ", strip=True) for elem in elements])
            break
    
    # Fallback to body content
    if not content:
        content = soup.get_text(separator=" ", strip=True)
    
    return clean_text(content)


def crawl_site(start_url, max_pages=20, delay=1):
    """
    Crawl a website starting from start_url
    
    Args:
        start_url: Starting URL
        max_pages: Maximum number of pages to crawl
        delay: Delay between requests in seconds
    
    Returns:
        tuple: (pages_dict, links_list)
    """
    visited = set()
    to_visit = [start_url]
    pages = {}
    links = []
    
    print(f"Starting crawl from: {start_url}")
    print(f"Maximum pages: {max_pages}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; Academic Web Crawler 1.0)'
    })

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        
        if url in visited or not is_valid_url(url):
            continue
            
        try:
            print(f"Crawling [{len(visited)+1}/{max_pages}]: {url}")
            
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check if it's HTML content
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type:
                print(f"  Skipping non-HTML content: {content_type}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = ""
            if soup.title:
                title = clean_text(soup.title.string)
            if not title:
                title = url.split('/')[-1] or url
            
            # Extract content
            content = extract_content(soup)
            
            if len(content) < 50:  # Skip pages with very little content
                print(f"  Skipping page with minimal content")
                continue
            
            pages[url] = {
                "title": title[:200],  # Limit title length
                "content": content[:5000]  # Limit content length for database
            }
            
            print(f"  Title: {title[:50]}...")
            print(f"  Content length: {len(content)} chars")
            
            # Extract links
            links_found = 0
            for a in soup.find_all("a", href=True):
                try:
                    link = urljoin(url, a["href"])
                    if is_valid_url(link):
                        links.append((url, link))
                        links_found += 1
                        
                        if (link not in visited and 
                            link not in to_visit and 
                            len(to_visit) < max_pages * 2):  # Limit queue size
                            to_visit.append(link)
                except:
                    continue
            
            print(f"  Found {links_found} valid links")
            visited.add(url)
            
            # Be respectful to the server
            time.sleep(delay)
            
        except requests.exceptions.RequestException as e:
            print(f"  Request error for {url}: {e}")
            continue
        except Exception as e:
            print(f"  Unexpected error for {url}: {e}")
            continue

    print(f"\nCrawling completed!")
    print(f"Total pages crawled: {len(pages)}")
    print(f"Total links found: {len(links)}")
    
    return pages, links


# Example usage
if __name__ == "__main__":
    start = "https://www.um.ac.id/"
    page_data, link_data = crawl_site(start, max_pages=10)
    
    print(f"\n=== CRAWL RESULTS ===")
    print(f"Total pages: {len(page_data)}")
    print(f"Total links: {len(link_data)}")
    
    print(f"\n=== SAMPLE PAGES ===")
    for i, (url, data) in enumerate(list(page_data.items())[:5]):
        print(f"[{i+1}] {url}")
        print(f"    Title: {data['title']}")
        print(f"    Content preview: {data['content'][:100]}...")
        print()
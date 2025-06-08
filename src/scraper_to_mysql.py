from web_scraper import crawl_site
from database import save_scraped_data_to_mysql, setup_all_tables


def main():
    """Main function to scrape and save data"""
    # Setup database tables first
    print("Setting up database tables...")
    if not setup_all_tables():
        print("Failed to setup database tables")
        return
    
    # Start scraping
    start_url = "https://www.um.ac.id/"
    print(f"Starting to crawl from: {start_url}")
    
    try:
        pages, links = crawl_site(start_url, max_pages=100)
        print(f"Crawled {len(pages)} pages and found {len(links)} links")
        
        # Save to database
        if save_scraped_data_to_mysql(pages, links):
            print("Data scraping berhasil disimpan ke MySQL.")
        else:
            print("Failed to save scraped data to MySQL.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")


if __name__ == "__main__":
    main()
from config import scraping_config
from scraper import WebScraper


def main():
    scraper = WebScraper()
    output = []
    
    for source in scraping_config:
        articles = scraper.scrape_articles(**source)
        output.extend(articles)

    scraper.save_to_json('output.json', output)
        
    
if __name__ == "__main__":
    main()
    
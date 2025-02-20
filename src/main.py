from scraping.scraper import BookScraper
from processing.smilarity_analyzer import BookAnalyzer, analyze_books

def main():
    # with BookScraper(batch_size=20, max_workers=10) as scraper:
    #     scraper.scrape_catalog()
    #     scraper.save_to_json()

    analyze_books()

if __name__ == "__main__":
    main()

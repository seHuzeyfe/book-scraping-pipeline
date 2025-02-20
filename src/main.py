from scraping.scraper import BookScraper
from processing.tfidf_smilarity_analyzer import TFIDFBookAnalyzer
from processing.sbert_smilarity_analyzer2 import SBERTBookAnalyzer

def main():
    with BookScraper(batch_size=20, max_workers=10) as scraper:
        scraper.scrape_catalog()
        scraper.save_to_json()

    tfidf_analyzer = TFIDFBookAnalyzer(similarity_threshold=0.6)
    tfidf_analyzer.analyze_and_print_summary()

    sbert_analyzer = SBERTBookAnalyzer(similarity_threshold=0.6)
    sbert_analyzer.analyze_and_print_summary()

if __name__ == "__main__":
    main()

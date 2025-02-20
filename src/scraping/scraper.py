from dataclasses import dataclass
from typing import List, Dict, Optional, Set
import requests
from bs4 import BeautifulSoup
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from time import sleep

@dataclass
class Book:
    """Data Class to store book information"""
    title: str
    rating: str
    description: str
    price: float
    in_stock: bool
    quantity: int = 0

class BookScraper:
    """Scraper to scrape book information from the website"""
    
    def __init__(self, batch_size: int = 20, max_workers: int = 10):
        self.base_url = 'http://books.toscrape.com'
        self.session = requests.Session()
        self.books: List[Book] = []
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.processed_urls: Set[str] = set()
        
    def get_page(self, url: str, retries: int = 3, delay: float = 1.0) -> Optional[BeautifulSoup]:
        """Fetching and parsing the web page with retry mechanism."""
        for attempt in range(retries):
            try:
                if url in self.processed_urls:
                    return None
                    
                sleep(delay)  # Rate limiting
                print(f"Fetching: {url}")  # Debug logging
                response = self.session.get(url)
                response.raise_for_status()
                self.processed_urls.add(url)
                return BeautifulSoup(response.text, 'html.parser')
                
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"Error fetching {url} after {retries} attempts: {str(e)}")
                    return None
                print(f"Attempt {attempt + 1} failed for {url}. Retrying...")
                sleep(delay * (attempt + 1))  # Exponential backoff

    def validate_url(self, url: str) -> str:
        """Validate and clean URLs."""
        if not url.startswith('http'):
            # Remove any '../' sequences
            url = url.replace('../', '')
            # Ensure we have the correct path structure
            if 'catalogue' not in url:
                url = f"catalogue/{url}"
            # Join with base URL
            url = f"{self.base_url}/{url.lstrip('/')}"
        return url

    def process_book(self, book_url: str) -> Optional[Book]:
        """Process a single book URL."""
        try:
            # Validate URL before processing
            book_url = self.validate_url(book_url)
            
            soup = self.get_page(book_url)
            if not soup:
                return None
            
            title = soup.select_one('div.product_main h1').text.strip()
            
            rating_element = soup.select_one('p.star-rating')
            rating = rating_element['class'][1].lower() if rating_element else 'unknown'
            rating_map = {'one':'1', 'two':'2', 'three':'3', 'four':'4', 'five':'5'}
            rating = rating_map.get(rating, 'unknown')
            
            price_str = soup.select_one('p.price_color').text.strip()
            price_str = re.sub(r'[^\d.]', '', price_str)
            price = float(price_str) if price_str else 0.0
            
            stock_text = soup.select_one('p.instock.availability').text.strip()
            in_stock = 'In stock' in stock_text
            quantity_match = re.search(r'\d+', stock_text)
            quantity = int(quantity_match.group()) if quantity_match else 0
            
            desc_element = soup.select_one('div#product_description + p')
            description = desc_element.text.strip() if desc_element else "No description available"
            
            return Book(
                title=title,
                rating=rating,
                description=description,
                price=price,
                in_stock=in_stock,
                quantity=quantity
            )
            
        except Exception as e:
            print(f"Error processing book at {book_url}: {str(e)}")
            return None

    def save_batch(self, books: List[Book], batch_num: int):
        """Save a batch of books to JSON file."""
        if not books:
            return
            
        filename = f'data/books_batch_{batch_num}.json'
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(
                [book.__dict__ for book in books],
                f,
                indent=2,
                ensure_ascii=False
            )
        print(f"Saved batch {batch_num} with {len(books)} books")

    def scrape_catalog(self):
        """Scrape all book catalogs using thread pool and batch saving."""
        book_urls = []
        current_url = f"{self.base_url}/catalogue/page-1.html"  # tart with correct catalog URL
        page_num = 1
        
        # First, collect all book URLs
        while True:
            print(f"Collecting URLs from page {page_num}")
            soup = self.get_page(current_url)
            if not soup:
                break
            
            book_elements = soup.select('article.product_pod')
            if not book_elements:
                break
            
            for book_element in book_elements:
                book_url = book_element.h3.a['href']
                if not book_url.startswith('http'):
                    # Fix: Handle relative URLs correctly
                    book_url = book_url.replace('../../../', '')
                    book_url = f"{self.base_url}/catalogue/{book_url}"
                book_urls.append(book_url)
            
            next_page = soup.select_one('li.next > a')
            if not next_page:
                break
            
            next_url = next_page['href']
            if not next_url.startswith('http'):
                # Fix: Handle pagination URLs correctly
                current_url = f"{self.base_url}/catalogue/{next_url}"
            else:
                current_url = next_url
            
            page_num += 1
        
        print(f"Found {len(book_urls)} books to process")
        
        # Process books using thread pool with batching
        current_batch = []
        batch_num = 1
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.process_book, url): url 
                for url in book_urls
            }
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    book = future.result()
                    if book:
                        current_batch.append(book)
                        self.books.append(book)
                        
                        if len(current_batch) >= self.batch_size:
                            self.save_batch(current_batch, batch_num)
                            batch_num += 1
                            current_batch = []
                            
                    processed_count += 1
                    if processed_count % 10 == 0:  # Progress update every 10 books
                        print(f"Processed {processed_count}/{len(book_urls)} books")
                        
                except Exception as e:
                    print(f"Error processing {url}: {str(e)}")
            
            # Save any remaining books
            if current_batch:
                self.save_batch(current_batch, batch_num)

    def save_to_json(self, filename: str = 'data/books_final.json'):
        """Save all scraped books to a final JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(
                [book.__dict__ for book in self.books],
                f,
                indent=2,
                ensure_ascii=False
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
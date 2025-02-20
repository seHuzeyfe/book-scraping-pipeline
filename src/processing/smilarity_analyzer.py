from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
import json
from collections import defaultdict

class BookAnalyzer:
    """Analyzes book descriptions and groups similar books."""
    
    def __init__(self, similarity_threshold: float = 0.3):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)  # Use both unigrams and bigrams
        )
        self.similarity_threshold = similarity_threshold
        self.books = []
        
    def load_books(self, filename: str = 'data/books_final.json'):
        """Load books from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.books = json.load(f)
            print(f"Loaded {len(self.books)} books")
        except Exception as e:
            print(f"Error loading books: {str(e)}")
            return False
        return True
    
    def preprocess_descriptions(self) -> List[str]:
        """Extract and preprocess book descriptions."""
        return [book['description'] for book in self.books]
    
    def calculate_similarity_matrix(self, descriptions: List[str]) -> np.ndarray:
        """Calculate similarity matrix for all book descriptions."""
        # Transform descriptions to TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(descriptions)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        return similarity_matrix
    
    def find_similar_books(self, similarity_matrix: np.ndarray) -> Dict[int, List[int]]:
        """Find groups of similar books based on similarity threshold."""
        groups = defaultdict(list)
        processed = set()
        
        for i in range(len(similarity_matrix)):
            if i in processed:
                continue
                
            # Find all books similar to book i
            similar_indices = np.where(similarity_matrix[i] > self.similarity_threshold)[0]
            
            if len(similar_indices) > 1:  # Only create group if there are similar books
                group_id = len(groups)
                for idx in similar_indices:
                    groups[group_id].append(idx)
                    processed.add(idx)
        
        return groups
    
    def create_similarity_groups(self) -> Dict[str, List[Dict]]:
        """Create groups of similar books and format the output."""
        descriptions = self.preprocess_descriptions()
        similarity_matrix = self.calculate_similarity_matrix(descriptions)
        groups = self.find_similar_books(similarity_matrix)
        
        # Format the output
        formatted_groups = {}
        for group_id, book_indices in groups.items():
            group_name = f"Group_{group_id + 1}"
            formatted_groups[group_name] = [
                {
                    'title': self.books[idx]['title'],
                    'description': self.books[idx]['description'][:200] + '...',  # Truncate for readability
                    'similarity_score': float(np.mean([similarity_matrix[idx][other_idx] 
                                                     for other_idx in book_indices 
                                                     if idx != other_idx]))
                }
                for idx in book_indices
            ]
        
        return formatted_groups
    
    def save_groups(self, groups: Dict[str, List[Dict]], filename: str = 'data/book_groups.json'):
        """Save grouped books to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(groups, f, indent=2, ensure_ascii=False)
            print(f"Saved groups to {filename}")
        except Exception as e:
            print(f"Error saving groups: {str(e)}")

def analyze_books():
    """Main function to analyze and group books."""
    analyzer = BookAnalyzer(similarity_threshold=0.3)
    
    if analyzer.load_books():
        groups = analyzer.create_similarity_groups()
        analyzer.save_groups(groups)
        
        # Print summary
        print("\nAnalysis Summary:")
        print(f"Total number of groups: {len(groups)}")
        print("\nSample groups:")
        for group_name, books in list(groups.items())[:3]:  # Show first 3 groups
            print(f"\n{group_name}: {len(books)} books")
            for book in books[:2]:  # Show first 2 books in each group
                print(f"- {book['title']} (similarity: {book['similarity_score']:.2f})")

if __name__ == "__main__":
    analyze_books()
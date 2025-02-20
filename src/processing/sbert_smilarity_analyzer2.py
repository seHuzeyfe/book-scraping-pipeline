from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
import json
from collections import defaultdict

class SBERTBookAnalyzer:
    """Analyzes book descriptions using SBERT embeddings."""
    
    def __init__(self, similarity_threshold: float = 0.6, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize with SBERT model.
        
        Args:
            similarity_threshold: Minimum similarity score to group books
            model_name: SBERT model to use (all-MiniLM-L6-v2 is fast and efficient)
        """
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.books = []
        
    def load_books(self, filename: str = 'data/books_final.json'):
        """Load books from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.books = json.load(f)
            print(f"Loaded {len(self.books)} books")
            return True
        except Exception as e:
            print(f"Error loading books: {str(e)}")
            return False
    
    def create_embeddings(self, descriptions: List[str]) -> np.ndarray:
        """Create SBERT embeddings for book descriptions."""
        print("Generating embeddings...")
        return self.model.encode(descriptions, show_progress_bar=True)
    
    def calculate_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosin similarity betveen all embeddings."""
        print("Calculating similarity matrix...")
        return cosine_similarity(embeddings)
    
    def find_similar_books(self, similarity_matrix: np.ndarray) -> Dict[int, List[Tuple[int, float]]]:
        """Find groups of sim,lar books with their similarity scores."""
        groups = defaultdict(list)
        processed = set()
        
        for i in range(len(similarity_matrix)):
            if i in processed:
                continue
            
            # Find books similar to book i
            similar_indices = np.where(similarity_matrix[i] > self.similarity_threshold)[0]
            
            if len(similar_indices) > 1:  # Create group only if there are similar books
                group_id = len(groups)
                for idx in similar_indices:
                    # Store both index and average similarity score
                    avg_similarity = np.mean([
                        similarity_matrix[idx][j] 
                        for j in similar_indices 
                        if j != idx
                    ])
                    groups[group_id].append((idx, float(avg_similarity)))
                    processed.add(idx)
        
        return groups
    
    def create_similarity_groups(self) -> Dict[str, List[Dict]]:
        """Create gruups of similar books usıng SBERT embeddings."""
        # Extract descriptions
        descriptions = [book['description'] for book in self.books]
        
        # Generate embeddings and similarity matrix
        embeddings = self.create_embeddings(descriptions)
        similarity_matrix = self.calculate_similarity_matrix(embeddings)
        groups = self.find_similar_books(similarity_matrix)
        
        # Format output
        formatted_groups = {}
        for group_id, book_indices in groups.items():
            group_name = f"Group_{group_id + 1}"
            formatted_groups[group_name] = [
                {
                    'title': self.books[idx]['title'],
                    'description': self.books[idx]['description'][:200] + '...',
                    'similarity_score': score,
                    'themes': self.extract_themes(self.books[idx]['description'])
                }
                for idx, score in book_indices
            ]
        
        return formatted_groups
    
    def extract_themes(self, description: str, num_themes: int = 3) -> List[str]:
        """Extract main themes from book description using keyword extraction."""
        # keyword extrsction baed on noun phrases
        from textblob import TextBlob
        blob = TextBlob(description)
        noun_phrases = blob.noun_phrases
        return list(set(noun_phrases))[:num_themes]
    
    def save_groups(self, groups: Dict[str, List[Dict]], filename: str = 'data/sbert_book_groups.json'):
        """Save grouped books to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(groups, f, indent=2, ensure_ascii=False)
            print(f"Saved groups to {filename}")
        except Exception as e:
            print(f"Error saving groups: {str(e)}")
    
    def analyze_and_print_summary(self):
        if self.load_books():
            groups = self.create_similarity_groups()
            self.save_groups(groups)
            
            print("\n SBERT method Analysis Summary:")
            print(f"Total books analyzed: {len(self.books)}")
            print(f"Total number of groups: {len(groups)}")
            print("\nSample groups with themes:")
            
            for group_name, books in list(groups.items())[:3]:
                print(f"\n{group_name}: {len(books)} books")
                for book in books:
                    print(f"- {book['title']}")
                    print(f"  Similarity: {book['similarity_score']:.2f}")
                    print(f"  Themes: {', '.join(book['themes'])}")

def main():
    analyzer = SBERTBookAnalyzer(similarity_threshold=0.6)
    analyzer.analyze_and_print_summary()

if __name__ == "__main__":
    main()
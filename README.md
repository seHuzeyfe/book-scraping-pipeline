# Book Scraping and Analysis System

A web scraping solution for books.toscrape.com with data analysis capabilities to group similar books based on descriptions.

## Features
- 📚 Scrapes book metadata (title, rating, price, stock, description)
- 💾 Saves data in JSON format with batch processing
- 🧮 Displays total book count
- 🤖 Groups books by description similarity using NLP techniques
- ⚡ Multi-threaded scraping with retry mechanism

## Technologies Used
- **Python 3.10+**
- Web Scraping: `requests`, `BeautifulSoup4`
- NLP Processing: `scikit-learn`
- Data Handling: `dataclasses`, `json`

## Installation
1. Clone repository:
   ```bash
   git clone https://github.com/seHuzeyfe/book-scraping-pipeline.git
   cd book-scraping-pipeline
   ```

2. Create virtual environment:
   ```bash
   python -m venv book_scraping_pipeline_venv
   source book_scraping_pipeline_venv/bin/activate  # Linux/Mac
   book_scraping_pipeline_venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the complete pipeline:
```bash
python main.py
```

### Process Flow:
#### Scraping Phase:
- Multi-threaded scraping of book data
- Automatic pagination handling
- Saves batches to `data/books_batch_*.json`
- Final output: `data/books_final.json`

#### Analysis Phase:
- Loads scraped data
- Calculates TF-IDF vectors
- Groups books by cosine similarity
- Saves groups to `data/book_groups.json`
- Prints summary to console

## Sample Outputs
### Book Data (`books_final.json`)
```json
[
  {
    "title": "A Light in the Attic",
    "rating": "3",
    "description": "It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love th It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love that Silverstein. Need proof of his genius? RockabyeRockabye baby, in the treetopDon't you know a treetopIs no safe place to rock?And who put you up there,And your cradle, too?Baby, I think someone down here'sGot it in for you. Shel, you never sounded so good. ...more",
    "price": 51.77,
    "in_stock": true,
    "quantity": 22
  },
  {
    "title": "Tipping the Velvet",
    "rating": "1",
    "description": "\"Erotic and absorbing...Written with starling power.\"--\"The New York Times Book Review \" Nan King, an oyster girl, is captivated by the music hall phenomenon Kitty Butler, a male impersonator extraordinaire treading the boards in Canterbury. Through a friend at the box office, Nan manages to visit all her shows and finally meet her heroine. Soon after, she becomes Kitty's \"Erotic and absorbing...Written with starling power.\"--\"The New York Times Book Review \" Nan King, an oyster girl, is captivated by the music hall phenomenon Kitty Butler, a male impersonator extraordinaire treading the boards in Canterbury. Through a friend at the box office, Nan manages to visit all her shows and finally meet her heroine. Soon after, she becomes Kitty's dresser and the two head for the bright lights of Leicester Square where they begin a glittering career as music-hall stars in an all-singing and dancing double act. At the same time, behind closed doors, they admit their attraction to each other and their affair begins. ...more",
    "price": 53.74,
    "in_stock": true,
    "quantity": 20
  },
]
```
![alt text](<Ekran görüntüsü 2025-02-20 115923.png>)



### Similarity Groups (`book_groups.json`)
```json
{
  "Group_1": [
    {
      "title": "Tipping the Velvet",
      "description": "\"Erotic and absorbing...Written with starling power.\"--\"The New York Times Book Review \" Nan King, an oyster girl, is captivated by the music hall phenomenon Kitty Butler, a male impersonator extraord...",
      "similarity_score": 0.38659367311361464
    },
    {
      "title": "Musicophilia: Tales of Music and the Brain",
      "description": "What goes on in human beings when they make or listen to music? What is it about music, what gives it such peculiar power over us, power delectable and beneficent for the most part, but also capable o...",
      "similarity_score": 0.38659367311361464
    }
  ],
}
```

### Console Output
```
Loaded 1000 books
Saved groups to data/book_groups.json

Analysis Summary:
Total number of groups: 205

Sample groups:

Group_1: 2 books
- Tipping the Velvet (similarity: 0.39)
- Musicophilia: Tales of Music and the Brain (similarity: 0.39)

Group_2: 2 books
- Soumission (similarity: 0.33)
- The Nightingale (similarity: 0.33)

Group_3: 5 books
- The Requiem Red (similarity: 0.36)
- How Music Works (similarity: 0.47)

```

## Project Structure
```
.
├── data/                 # Output JSON files
├── scraping/
│   ├── scraper.py       # Main scraping logic
├── processing/
│   ├── similarity_analyzer.py  # NLP analysis
├── main.py              # Entry point
├── README.md
└── requirements.txt
```

## Design Notes
### SOLID Principles:
- **Single Responsibility** (separate scraper/analyzer)
- **Open/Closed** (extendable scraping logic)
- **Dependency Inversion** (abstracted HTTP client)

### Patterns:
- **Factory Method** (Book dataclass)
- **Strategy** (similarity calculation)
- **Observer** (progress tracking)

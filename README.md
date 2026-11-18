# DarGlobal & Wasalt Chatbot

Chatbot over publicly available DarGlobal and Wasalt data, answered by a free OpenRouter model.

## Data (`scrape.py` → `data/corpus.json`)
- **Wasalt**: the sitemaps Wasalt publishes in its `robots.txt` (`cdn.wasalt.sa`): ~60k sale/rent listings
  (type, purpose, size, bedrooms, facing, street width, link), ~2.7k daily-rental units, ~1.6k locations
  with their available categories, plus portfolio statistics.
- **DarGlobal**: `darglobal.co.uk` is protected by an Incapsula bot wall, so its public Wikipedia articles
  (DarGlobal, parent Dar Al Arkan, Trump International Hotel Maldives) are used.

## How it works (`app.py`, stdlib only)
TF-IDF keyword retrieval picks the top documents for the question → injected as context →
OpenRouter free model (`google/gemma-4-31b-it:free`, with fallbacks) answers with source links.

## Run
```bash
python3 scrape.py                       # refresh data (optional, corpus is committed)
docker build -t darglobal-chatbot .
docker run -p 8080:8080 --env-file .env darglobal-chatbot   # .env: OPENROUTER_API_KEY=sk-or-...
```
Open http://localhost:8080

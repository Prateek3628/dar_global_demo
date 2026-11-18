# DarGlobal & Wasalt Chatbot

Mobile-first chatbot that answers questions about DarGlobal and Wasalt from publicly available data,
using a free OpenRouter model. Every answer cites its sources.

## Where answers come from (all used together on each question)
| Source | Freshness | Notes |
|---|---|---|
| **Wasalt sitemaps** (`cdn.wasalt.sa`, listed in Wasalt's `robots.txt`) | re-scraped every `REFRESH_HOURS` (default 1h) | ~60k sale/rent listings, ~2.7k daily rentals, ~1.6k locations, portfolio stats |
| **Wikipedia** — every article mentioning DarGlobal / Dar Al Arkan | re-scraped every `REFRESH_HOURS` | company history, projects, partnerships |
| **Live web search** restricted to `darglobal.co.uk` + `wasalt.sa` (Tavily and/or Brave) | fetched at question time (search-index freshness) | optional; enabled when an API key is set |

`darglobal.co.uk` and Wasalt's listing pages block automated requests (Incapsula / Cloudflare), so
pages are never fetched directly; their content reaches the bot via search-engine results instead.
True real-time data would need an official feed.

## How it works (RAG, `app.py`, Python stdlib only)
1. **Retrieve** – TF-IDF keyword search over the indexed data + live web search, in parallel; failed sources are skipped.
2. **Augment** – results go into the prompt labelled by source and freshness.
3. **Generate** – OpenRouter free model (`google/gemma-4-31b-it:free`, with fallbacks) answers with source links.

## Run
```bash
cp .env.example .env    # add OPENROUTER_API_KEY (+ optional TAVILY_API_KEY / BRAVE_API_KEY)
docker build -t darglobal-chatbot .
docker run -p 8080:8080 --env-file .env darglobal-chatbot
```
Open http://localhost:8080. `python3 scrape.py` regenerates the bundled snapshot in `data/corpus.json`.

| Env var | Required | Purpose |
|---|---|---|
| `OPENROUTER_API_KEY` | yes | LLM calls (free models) |
| `TAVILY_API_KEY` | no | live search (1,000 free/month, tavily.com) |
| `BRAVE_API_KEY` | no | live search (2,000 free/month, brave.com/search/api) |
| `REFRESH_HOURS` | no | background re-scrape interval, `0` disables (default `1`) |
| `MODELS` | no | comma-separated OpenRouter model fallback list |

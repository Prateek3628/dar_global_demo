# What the chatbot can answer — and how it is verified

## Question types

| Type | Example questions | Answered from | Notes |
|---|---|---|---|
| **Wasalt counts** | How many apartments are for rent? · How many 3-bedroom apartments? · How many daily-rental units? | Wasalt sitemap statistics (refreshed hourly) | Counts are *for Wasalt's public sitemap*, which is capped at ~60k listings; the bot says so |
| **Listing search** | Show 4-bedroom villas for rent · Land for sale facing north on a 20m street · Buildings for rent | Indexed listings + live wasalt.sa pages | Rent/sale and bedroom filters are enforced in code; every listing is a link |
| **Locations** | What property types are in Al Khobar? · Farms for daily rental in Riyadh? · Chalets in Jeddah? | Wasalt category pages per city/district | ~1.6k places |
| **Prices / districts** | Price of a 4-bedroom villa for rent? · Villas for rent in Riyadh | Live wasalt.sa search results only | Indexed listings have no price/city; prices appear only when live pages carry them |
| **DarGlobal company** | When did it list on the LSE? · IPO valuation? · Parent company? · Founded? | Wikipedia (refreshed hourly) + live darglobal.co.uk | |
| **DarGlobal projects** | Missoni · Aston Martin (The Astera) · Trump Tower Dubai / Jeddah · Oman · W Residences · Mouawad · Spain | Wikipedia + live darglobal.co.uk press pages | Newest projects come from live search |
| **Out of scope** | Write code · sports · general chat | — | Politely declined with a relevant suggestion |
| **Prompt injection** | "Ignore previous instructions…" | — | Refused; context is treated as data |
| **Investment advice** | Should I buy DarGlobal shares? | — | No advice; suggests verifying with a licensed advisor |
| **Arabic** | كم عدد الشقق المعروضة للإيجار؟ | same sources | Answers in Arabic |

**Cannot be answered** (the bot says so instead of guessing): floor plans, photos, live availability, agent contact
details, exact prices for indexed-only listings, anything not on DarGlobal/Wasalt/Wikipedia pages.

## How correctness is checked (`eval.py`)

* `python eval.py retrieval` — offline, no API calls: does search surface the right documents for each question type?
* `python eval.py e2e [URL]` — 36 real questions against a running server. Each answer is checked for:
  * **Facts** — counts match the data exactly; DarGlobal facts match the source text (dates, values, names).
  * **No invented links** — every link must be a document the model was actually given (the model cites `[n]`
    and the server turns that into the exact URL, so it cannot make links up).
  * **No invented numbers** — every number ≥ 1,000 (prices, sizes, counts) must appear in the model's context.
  * **Filters** — listing links match the requested rent/sale and bedroom count.
  * **Citations** — factual answers carry clickable sources.
  * **Guardrails** — off-topic and injection attempts are refused; no investment advice.

Run e2e against a server started with `REFRESH_HOURS=0` so counts match the bundled snapshot. Full answers are saved to
`eval_results.json` after every question.

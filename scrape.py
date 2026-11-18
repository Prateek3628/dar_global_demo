"""Collect public DarGlobal + Wasalt data into data/corpus.json.

Wasalt: the sitemaps it publishes in robots.txt (cdn.wasalt.sa) -> listings, locations, pages.
DarGlobal: darglobal.co.uk sits behind an Incapsula bot wall, so its public Wikipedia
articles are used instead.
"""
import collections, json, re, urllib.parse, urllib.request

UA = {"User-Agent": "DarGlobal-assignment-bot/1.0 (candidate technical assignment)"}
SITEMAP = "https://cdn.wasalt.sa/sitemap/{}_en_sa.xml.gz"
WIKI = ["DarGlobal", "Dar Al Arkan Real Estate Development Company", "Trump International Hotel Maldives"]


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode()


def locs(name):
    return re.findall(r"<loc>([^<]+)</loc>", get(SITEMAP.format(name)))  # served as plain XML despite .gz


def parse_listing(url):
    """https://wasalt.sa/en/property/sale/villa-333-sqm-facing-east-on-20m-width-street-5841671"""
    purpose, slug = url.split("/property/")[1].split("/", 1)
    num = lambda p: (m := re.search(p, slug)) and int(m.group(1))
    face = re.search(r"facing-((?:north|south|east|west)(?:-(?:east|west))?)", slug)
    return {
        "id": slug.rsplit("-", 1)[-1], "purpose": purpose, "type": slug.split("-")[0],
        "sqm": num(r"(\d+)-sqm"), "bedrooms": num(r"(\d+)-bedroom"),
        "facing": face and face.group(1), "street_m": num(r"(\d+)m-width"), "url": url,
        "title": slug.rsplit("-", 1)[0].replace("-", " "),
    }


def wasalt():
    docs = []
    listings = [l for u in locs("product_sitemap") if "/property/" in u
                if not (l := parse_listing(u))["type"].isdigit()]
    daily = locs("rental_pdp_sitemap")

    by = collections.Counter((l["purpose"], l["type"]) for l in listings)
    lines = [f"- {n} {t} listings for {p}" for (p, t), n in by.most_common()]
    beds = collections.Counter((l["type"], l["bedrooms"]) for l in listings if l["bedrooms"])
    lines += [f"- {n} {t}s with {b} bedrooms" for (t, b), n in beds.most_common(25)]
    daily_types = collections.Counter(u.rsplit("/", 1)[1].split("-for-")[0] for u in daily)
    lines += [f"- {n} {t} units for daily rental / booking" for t, n in daily_types.most_common()]
    docs.append({"source": "Wasalt", "title": "Wasalt listings overview (statistics)",
                 "url": "https://wasalt.sa/en", "always": True,
                 "text": f"Wasalt (wasalt.sa) is a Saudi Arabian property portal. Snapshot of {len(listings)} sale/rent "
                         f"listings and {len(daily)} daily-rental units from its public sitemaps:\n" + "\n".join(lines)})

    # one doc per location: which categories Wasalt has there
    cats = collections.defaultdict(set)
    for u in locs("category_sitemap") + locs("rental_srp_sitemap"):
        m = re.match(r"https://wasalt\.sa/en/(.+?)-for-(sale|rent|daily-rental)-in-(.+)$", u)
        if m and not re.search(r"\d", m.group(3)):  # skip price-filter pages
            cats[m.group(3)].add(f"{m.group(1).replace('-', ' ')} for {m.group(2).replace('-', ' ')}")
    for place, kinds in cats.items():
        name = place.replace("-", " ")
        docs.append({"source": "Wasalt", "title": f"Wasalt properties in {name}",
                     "url": f"https://wasalt.sa/en/properties-for-sale-in-{place}",
                     "text": f"Wasalt has property categories in {name}: {', '.join(sorted(kinds))}."})

    docs += [{"source": "Wasalt", "title": f"Wasalt listing {l['id']}: {l['title']} ({l['purpose']})", "url": l["url"],
              "text": f"{l['title']} for {l['purpose']} on Wasalt. Type {l['type']}"
                      + "".join(f", {k} {l[k]}" for k in ("sqm", "bedrooms", "facing", "street_m") if l[k])}
             for l in listings]
    docs += [{"source": "Wasalt", "title": f"Wasalt page: {u.rsplit('/', 1)[-1] or 'home'}", "url": u,
              "text": f"Wasalt website page {u}"} for u in locs("static_sitemap")]
    return docs


def wikipedia():
    docs = []
    for t in WIKI:
        q = urllib.parse.urlencode({"action": "query", "prop": "extracts", "explaintext": 1,
                                    "format": "json", "redirects": 1, "titles": t})
        page = next(iter(json.loads(get(f"https://en.wikipedia.org/w/api.php?{q}"))["query"]["pages"].values()))
        url = "https://en.wikipedia.org/wiki/" + page["title"].replace(" ", "_")
        for i, chunk in enumerate(re.split(r"\n(?===)", page.get("extract", ""))):
            if chunk.strip():
                docs.append({"source": "DarGlobal", "title": f"{page['title']} ({i})", "url": url,
                             "always": t == "DarGlobal" and i == 0, "text": chunk.strip()})
    return docs


if __name__ == "__main__":
    docs = wikipedia() + wasalt()
    with open("data/corpus.json", "w") as f:
        json.dump(docs, f)
    print(len(docs), "docs;", collections.Counter(d["source"] for d in docs))

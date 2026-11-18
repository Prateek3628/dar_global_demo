"""DarGlobal + Wasalt chatbot: keyword retrieval over data/corpus.json + a free OpenRouter model."""
import collections, json, math, os, re, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KEY = os.environ.get("OPENROUTER_API_KEY", "")
# OpenRouter tries these in order; free models get rate-limited, so keep fallbacks
MODELS = os.environ.get("MODELS", "google/gemma-4-31b-it:free,nvidia/nemotron-3.5-lightning:free,"
                                  "google/gemma-4-26b-a4b-it:free").split(",")
DOCS = json.load(open(os.path.join(os.path.dirname(__file__), "data/corpus.json")))
PAGE = open(os.path.join(os.path.dirname(__file__), "index.html"), "rb").read()


def tokens(s):
    return [w.rstrip("s") if len(w) > 3 else w for w in re.findall(r"[a-z0-9]+", s.lower())]


# ponytail: in-memory TF-IDF over ~60k short docs, swap for embeddings if paraphrase recall matters
INDEX, LEN = collections.defaultdict(list), []
for i, d in enumerate(DOCS):
    toks = set(tokens(d["title"] + " " + d["text"]))
    LEN.append(math.sqrt(len(toks)))
    for t in toks:
        INDEX[t].append(i)
IDF = {t: math.log(len(DOCS) / len(ids)) for t, ids in INDEX.items()}
ALWAYS = [d for d in DOCS if d.get("always")]


def search(q, k=12):
    scores = collections.Counter()
    for t in set(tokens(q)):
        for i in INDEX.get(t, ()):
            scores[i] += IDF[t] / LEN[i]
    return [DOCS[i] for i, _ in scores.most_common(k) if not DOCS[i].get("always")]


SYSTEM = """You are the assistant for a DarGlobal + Wasalt property knowledge base.
DarGlobal (Dar Global PLC) is an international luxury real-estate developer; Wasalt is a Saudi property portal.
Answer ONLY from the context below. If it doesn't contain the answer, say so briefly.
Cite sources as markdown links using the given URLs. When listing properties, show at most 6, each with its link.
Keep answers concise.

Context:
{ctx}"""


def answer(messages):
    q = " ".join(m["content"] for m in messages[-3:] if m["role"] == "user")
    ctx = "\n\n".join(f"[{d['source']}] {d['title']} ({d['url']})\n{d['text']}" for d in ALWAYS + search(q))
    body = {"models": MODELS, "messages": [{"role": "system", "content": SYSTEM.format(ctx=ctx)}] + messages[-8:]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(), {
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/darglobal-assignment", "X-Title": "DarGlobal Wasalt Chatbot"})
    r = json.load(urllib.request.urlopen(req, timeout=90))
    return r["choices"][0]["message"]["content"], r.get("model")


class H(BaseHTTPRequestHandler):
    def send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            return self.send(200, json.dumps({"ok": True, "docs": len(DOCS)}).encode())
        self.send(200, PAGE, "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/chat":
            return self.send(404, b"{}")
        try:
            msgs = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length", 0)), 100_000)))["messages"]
            msgs = [{"role": m["role"], "content": str(m["content"])[:2000]} for m in msgs
                    if m.get("role") in ("user", "assistant")]
            text, model = answer(msgs)
            self.send(200, json.dumps({"reply": text, "model": model}).encode())
        except Exception as e:
            detail = e.read().decode()[:300] if hasattr(e, "read") else str(e)
            self.send(502, json.dumps({"error": f"Model call failed: {detail}"}).encode())


if __name__ == "__main__":
    print(f"{len(DOCS)} docs indexed; serving on :{os.environ.get('PORT', 8080)}")
    ThreadingHTTPServer(("", int(os.environ.get("PORT", 8080))), H).serve_forever()

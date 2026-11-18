"""Run: python test_app.py  (checks the rate limiter, the only non-trivial guardrail logic)."""
import app

rules = ((60, 2), (3600, 3))
assert app.allowed("t", rules, t=0) and app.allowed("t", rules, t=1)
assert not app.allowed("t", rules, t=2)          # 3rd within a minute -> blocked
assert app.allowed("t", rules, t=61)             # minute window passed
assert not app.allowed("t", rules, t=62)         # hourly cap (3) reached
assert app.allowed("t", rules, t=3601)           # old hits expire
assert app.allowed("other", rules, t=2)          # limits are per key
assert app.official("https://www.darglobal.co.uk/press") and app.official("https://wasalt.sa/en")
assert not app.official("https://preprod.darglobal.co.uk/press")
ok = {"https://wasalt.sa/en", "https://en.wikipedia.org/wiki/DarGlobal"}
assert app.unlink_invented("[a](https://wasalt.sa/en) [b](https://en.wikipedia.org/wiki/Dar_Global_PLC)", ok) \
    == "[a](https://wasalt.sa/en) b"
assert app.unlink_invented("see https://fake.example/x and https://wasalt.sa/en", ok) == "see  and https://wasalt.sa/en"
assert app.unlink_invented("[[Live web] T](https://darglobal.co.uk/fake)", ok) == "[Live web] T"   # nested label
docs = [{"url": "https://wasalt.sa/en"}, {"url": "https://en.wikipedia.org/wiki/DarGlobal"}]
assert app.link_citations("Fact [2], other [1][9].", docs) == \
    "Fact [[2]](https://en.wikipedia.org/wiki/DarGlobal), other [[1]](https://wasalt.sa/en)."
print("ok")

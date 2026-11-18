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
print("ok")

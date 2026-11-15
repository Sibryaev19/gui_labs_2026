import json
import os
import urllib.request

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}RUB=X?interval=1m&range=1d"

last_error = ""


def fetch_market_rate(cur):
    req = urllib.request.Request(URL.format(cur), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode("utf-8"))
    meta = data["chart"]["result"][0]["meta"]
    return meta["regularMarketPrice"], meta["regularMarketTime"]


def fetch_rates():
    global last_error
    try:
        usd, t_usd = fetch_market_rate("USD")
    except Exception as e:
        # USD не получен: EUR даже не запрашиваем, ответ всё равно будет отказом
        last_error = "%s: %s" % (type(e).__name__, e)
        return None, ""
    try:
        eur, t_eur = fetch_market_rate("EUR")
    except Exception as e:
        last_error = "%s: %s" % (type(e).__name__, e)
        return None, ""
    rates = {"USD": usd, "EUR": eur}
    t = max(t_usd, t_eur)
    import datetime
    date = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")
    last_error = ""
    return rates, date


def get_rates():
    rates, date = fetch_rates()
    if rates is not None:
        return rates, True, date
    return {
        "USD": float(os.environ.get("RATE_USD_RUB", 90)),
        "EUR": float(os.environ.get("RATE_EUR_RUB", 100)),
    }, False, ""

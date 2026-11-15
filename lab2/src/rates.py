import json
import os
import urllib.request

URL = "https://www.cbr-xml-daily.ru/daily_json.js"


def fetch_cbr_rates():
    try:
        with urllib.request.urlopen(URL, timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
        usd = data["Valute"]["USD"]
        eur = data["Valute"]["EUR"]
        rates = {
            "USD": usd["Value"] / usd["Nominal"],
            "EUR": eur["Value"] / eur["Nominal"],
        }
        return rates, data["Date"][:10]
    except Exception:
        return None, ""


def get_rates():
    rates, date = fetch_cbr_rates()
    if rates is not None:
        return rates, True, date
    return {
        "USD": float(os.environ.get("RATE_USD_RUB", 90)),
        "EUR": float(os.environ.get("RATE_EUR_RUB", 100)),
    }, False, ""

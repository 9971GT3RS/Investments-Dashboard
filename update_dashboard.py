# update_dashboard.py (mit Ölpreis, USD/EUR, Crypto-Charts)
import requests
from datetime import datetime, timedelta, timezone
import json
import os

FMP_API_KEY = "ITys2XTLibnUOmblYKvkn59LlBeLOoWU"
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
NEWSDATA_API_KEY = "pub_8178059be021e6dbfd5d7ad623f9f93f1a9f5"
EXCHANGE_RATE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"

GROUPS = {
    "Shares": [
        "META", "GOOGL", "AMZN", "PYPL", "NVDA", "AMD", "CRWD", "ASML", "MSFT", "CRM", "NOW", "TSLA", "TSM",
        "SQ", "ILMN", "MU", "MRVL", "NKE", "RNKGF", "XOM", "OXY", "UAA", "BABA", "XPEV", "RNMBF", "PLTR"
    ],
    "Indices": ["^GSPC", "^NDX"],
    "Crypto": ["BTC-USD", "ETH-USD"],
    "Other": ["WTI"]
}

SYMBOL_TO_QUERY = {
    "META": "Meta Platforms",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "PYPL": "Paypal",
    "NVDA": "Nvidia",
    "AMD": "Advanced Micro Devices",
    "CRWD": "Crowdstrike",
    "ASML": "ASML Holding",
    "MSFT": "Microsoft",
    "CRM": "Salesforce",
    "NOW": "ServiceNow",
    "TSLA": "Tesla",
    "TSM": "Taiwan Semiconductor",
    "SQ": "Block Inc",
    "ILMN": "Illumina",
    "MU": "Micron Technology",
    "MRVL": "Marvell",
    "NKE": "Nike",
    "RNKGF": "Renk",
    "XOM": "ExxonMobil",
    "OXY": "Occidental Petroleum",
    "UAA": "Under Armour",
    "BABA": "Alibaba",
    "XPEV": "Xpeng",
    "RNMBF": "Rheinmetall",
    "PLTR": "Palantir"
}

ALL_TICKERS = GROUPS["Shares"] + GROUPS["Indices"] + GROUPS["Crypto"] + GROUPS["Other"]

HEADERS = {
    "x-rapidapi-key": YAHOO_API_KEY,
    "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
}

def fetch_stock_data():
    try:
        params = {"symbols": ",".join(ALL_TICKERS), "region": "US"}
        response = requests.get(YAHOO_API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json().get("quoteResponse", {}).get("result", [])
    except Exception as e:
        print("Error fetching stock data:", e)
        return []

def fetch_chart_data():
    cache_file = "chart_cache.json"
    now = datetime.now()
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
            timestamp = datetime.fromisoformat(cache.get("timestamp", "1970-01-01"))
            if (now - timestamp).total_seconds() < 86400:
                return cache.get("data", {})

    chart_data = {}
    for group in GROUPS:
        for symbol in GROUPS[group]:
            try:
                url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?timeseries=30&apikey={FMP_API_KEY}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json().get("historical", [])
                chart_data[symbol] = list(reversed([{
                    "label": entry["date"],
                    "value": entry["close"]
                } for entry in data]))
            except Exception as e:
                print(f"[CHART] Error for {symbol}: {e}")

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump({"timestamp": now.isoformat(), "data": chart_data}, f)

    return chart_data

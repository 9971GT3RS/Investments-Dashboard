# update_dashboard.py (Earnings fix: Zeitraum erweitert + mehr News pro Aktie)
import requests
from datetime import datetime, timedelta, timezone
import json
import os

FMP_API_KEY = "ITys2XTLibnUOmblYKvkn59LlBeLOoWU"
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
GNEWS_API_KEY = "83df462ceeaf456d4d178309ca672e41"
EXCHANGE_RATE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"
GNEWS_API_URL = "https://gnews.io/api/v4/search"
EARNINGS_API = "https://financialmodelingprep.com/api/v3/earning_calendar"

GROUPS = {
    "Shares": [
        "META", "GOOGL", "AMZN", "PYPL", "NVDA", "AMD", "CRWD", "ASML", "MSFT", "CRM", "NOW", "TSLA", "TSM",
        "SQ", "ILMN", "MU", "MRVL", "NKE", "RNKGF", "XOM", "OXY", "UAA", "BABA", "XPEV", "RNMBF", "PLTR"
    ],
    "Indices": ["^GSPC", "^NDX"],
    "Crypto": ["BTC-USD", "ETH-USD"]
}

NEWS_QUERY_OVERRIDES = {
    "META": "Meta Platforms",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "PYPL": "Paypal",
    "NVDA": "Nvidia",
    "AMD": "AMD",
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
    "XOM": "Exxon",
    "OXY": "Occidental Petroleum",
    "UAA": "Under Armour",
    "BABA": "Alibaba",
    "XPEV": "XPeng",
    "RNMBF": "Rheinmetall",
    "PLTR": "Palantir",
    "^GSPC": "S&P 500",
    "^NDX": "Nasdaq 100",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum"
}

ALL_TICKERS = GROUPS["Shares"] + GROUPS["Indices"] + GROUPS["Crypto"]

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

def fetch_news(query):
    cache_file = f"news_cache_{query}.json"
    now = datetime.now(timezone.utc)

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
            timestamp = datetime.fromisoformat(cache["fetched"])
            if (now - timestamp).total_seconds() < 3600:
                return cache["articles"]

    try:
        params = {"q": query, "token": GNEWS_API_KEY, "lang": "en", "max": 20, "sort_by": "publishedAt"}
        response = requests.get(GNEWS_API_URL, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"fetched": now.isoformat(), "articles": articles}, f)
        return articles
    except Exception as e:
        print(f"News error for {query}:", e)
        return []

def fetch_earnings_dates():
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        future = (datetime.today() + timedelta(days=60)).strftime("%Y-%m-%d")
        url = f"{EARNINGS_API}?from={today}&to={future}&apikey={FMP_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {item['symbol']: datetime.strptime(item['date'], "%Y-%m-%d").strftime("%d.%m.%Y") for item in data}
    except Exception as e:
        print("Earnings fetch error:", e)
        return {}

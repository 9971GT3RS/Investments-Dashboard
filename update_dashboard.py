# update_dashboard.py (mit echten Earnings-Terminen + News-Overrides für bessere Treffer)
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
        params = {"q": query, "token": GNEWS_API_KEY, "lang": "en", "max": 5, "sort_by": "publishedAt"}
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
        url = f"{EARNINGS_API}?apikey={FMP_API_KEY}&limit=1000"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {item['symbol']: datetime.strptime(item['date'], "%Y-%m-%d").strftime("%d.%m.%Y") for item in data}
    except Exception as e:
        print("Earnings fetch error:", e)
        return {}

def build_html(data):
    utc_now = datetime.now(timezone.utc)
    berlin_offset = timedelta(hours=2)
    berlin_time = (utc_now + berlin_offset).strftime("%d.%m.%Y – %H:%M")

    content = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Market Dashboard</title>
</head>
<body>
<h1>Market News Dashboard</h1>
<p>Last updated: {berlin_time} (Berlin Time)</p>
"""

    exchange_rate = 1.0
    try:
        exchange_rate = requests.get(EXCHANGE_RATE_API).json()['rates']['EUR']
    except:
        content += "<p style='color:red;'>⚠️ EUR conversion failed</p>"

    data_by_symbol = {item.get('symbol'): item for item in data}
    earnings_map = fetch_earnings_dates()

    for group_name, tickers in GROUPS.items():
        content += f"<h2>{group_name}</h2>"
        for symbol in tickers:
            item = data_by_symbol.get(symbol)
            if not item:
                continue
            name = item.get('shortName') or symbol
            price_usd = item.get('regularMarketPrice', 'N/A')
            change = item.get('regularMarketChangePercent')
            change_text = f"{change:.2f}%" if isinstance(change, (int, float)) else "N/A"
            earnings_date = earnings_map.get(symbol, "N/A")

            price_eur = float(price_usd) * exchange_rate if isinstance(price_usd, (int, float)) else "N/A"

            content += f"<h3>{name} ({symbol})</h3>"
            content += f"<p>Price: ${price_usd} ({change_text}) / €{price_eur:.2f}</p>"
            content += f"<p>Next earnings: {earnings_date}</p>"

            query = NEWS_QUERY_OVERRIDES.get(symbol, name.split(',')[0])
            articles = fetch_news(query)
            if articles:
                for article in articles:
                    content += f"<li><a href='{article['url']}' target='_blank'>{article['title']}</a></li>"
            else:
                content += "<p><i>No recent news available.</i></p>"

    content += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

# update_dashboard.py (stabilisierte Version ohne News – nur Kurse + Earnings)
import requests
from datetime import datetime, timedelta, timezone
import json
import os

FMP_API_KEY = "ITys2XTLibnUOmblYKvkn59LlBeLOoWU"
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
EXCHANGE_RATE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"
EARNINGS_API = "https://financialmodelingprep.com/api/v3/earning_calendar"

GROUPS = {
    "Shares": [
        "META", "GOOGL", "AMZN", "PYPL", "NVDA", "AMD", "CRWD", "ASML", "MSFT", "CRM", "NOW", "TSLA", "TSM",
        "SQ", "ILMN", "MU", "MRVL", "NKE", "RNKGF", "XOM", "OXY", "UAA", "BABA", "XPEV", "RNMBF", "PLTR"
    ],
    "Indices": ["^GSPC", "^NDX"],
    "Crypto": ["BTC-USD", "ETH-USD"]
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

def fetch_earnings_dates():
    print("[DEBUG] Fetching earnings dates...")
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        future = (datetime.today() + timedelta(days=90)).strftime("%Y-%m-%d")
        url = f"{EARNINGS_API}?from={today}&to={future}&apikey={FMP_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"[DEBUG] Received {len(data)} earnings entries")
        print("[DEBUG] Sample symbols:", [d['symbol'] for d in data[:10]])
        return {item['symbol']: datetime.strptime(item['date'], "%Y-%m-%d").strftime("%d.%m.%Y") for item in data if item['symbol'] in GROUPS['Shares']}
    except Exception as e:
        print("Earnings fetch error:", e)
        return {}

def build_html(data):
    utc_now = datetime.now(timezone.utc)
    berlin_time = (utc_now + timedelta(hours=2)).strftime("%d.%m.%Y – %H:%M")

    earnings_map = fetch_earnings_dates()

    try:
        exchange_rate = requests.get(EXCHANGE_RATE_API).json()['rates']['EUR']
    except:
        exchange_rate = 1.0

    data_by_symbol = {item.get('symbol'): item for item in data}
    
    html = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Market Dashboard</title>
</head>
<body>
<h1>Market Dashboard</h1>
<p>Last updated: {berlin_time} (Berlin Time)</p>
"""

    for group_name, tickers in GROUPS.items():
        html += f"<h2>{group_name}</h2>"
        for symbol in sorted(tickers):
            item = data_by_symbol.get(symbol)
            if not item:
                continue
            name = item.get('shortName') or symbol
            price_usd = item.get('regularMarketPrice', 'N/A')
            change = item.get('regularMarketChangePercent')
            change_text = f"{change:.2f}%" if isinstance(change, (int, float)) else "N/A"
            price_eur = float(price_usd) * exchange_rate if isinstance(price_usd, (int, float)) else "N/A"
            earnings_date = earnings_map.get(symbol, "N/A")

            html += f"<h3>{name} ({symbol})</h3>"
            html += f"<p>Price: ${price_usd} ({change_text}) / €{price_eur:.2f}</p>"
            html += f"<p>Next earnings: {earnings_date}</p>"

    html += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

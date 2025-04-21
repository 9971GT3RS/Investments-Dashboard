# update_dashboard.py (Rollback zur stabilen Version ohne Charts)
import requests
from datetime import datetime, timedelta, timezone
import json

FMP_API_KEY = "ITys2XTLibnUOmblYKvkn59LlBeLOoWU"
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
GNEWS_API_KEY = "83df462ceeaf456d4d178309ca672e41"
EXCHANGE_RATE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"

TICKERS = ["META", "TSLA"]

HEADERS = {
    "x-rapidapi-key": YAHOO_API_KEY,
    "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
}

def fetch_stock_data():
    try:
        params = {"symbols": ",".join(TICKERS), "region": "US"}
        response = requests.get(YAHOO_API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json().get("quoteResponse", {}).get("result", [])
    except Exception as e:
        print("Error fetching stock data:", e)
        return []

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

    for item in data:
        symbol = item.get('symbol', 'N/A')
        name = item.get('shortName') or symbol
        price_usd = item.get('regularMarketPrice', 'N/A')
        change = item.get('regularMarketChangePercent')
        change_text = f"{change:.2f}%" if isinstance(change, (int, float)) else "N/A"
        earnings_date = "24.04.2024"

        price_eur = float(price_usd) * exchange_rate if isinstance(price_usd, (int, float)) else "N/A"

        content += f"<h3>{name} ({symbol})</h3>"
        content += f"<p>Price: ${price_usd} ({change_text}) / €{price_eur:.2f}</p>"
        content += f"<p>Next earnings: {earnings_date}</p>"

    content += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

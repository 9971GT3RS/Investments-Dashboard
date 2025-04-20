# update_dashboard.py (mit abgesichertem Chart-Fetching und Fehlerbehandlung)
import requests
from datetime import datetime, timedelta, timezone
import json

# === CONFIG ===
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
GNEWS_API_KEY = "83df462ceeaf456d4d178309ca672e41"
EXCHANGE_RATE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"
CHART_API_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/"

TICKERS = ["META", "TSLA"]
CHART_ENABLED_TICKERS = ["META", "TSLA"]

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

def fetch_chart_data(ticker):
    try:
        url = f"{CHART_API_BASE}{ticker}?range=30d&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}  # Yahoo blockt Requests ohne UA
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()["chart"]["result"]
        if not result:
            return [], []
        chart = result[0]
        timestamps = chart.get("timestamp")
        prices = chart.get("indicators", {}).get("quote", [{}])[0].get("close")
        if not timestamps or not prices:
            return [], []
        dates = [datetime.utcfromtimestamp(ts).strftime("%d.%m") for ts in timestamps if ts]
        prices = [p for p in prices if p is not None]
        if len(dates) != len(prices):
            min_len = min(len(dates), len(prices))
            dates, prices = dates[:min_len], prices[:min_len]
        return dates, prices
    except Exception as e:
        print(f"Chart data error for {ticker}:", e)
        return [], []

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
  <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
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

        if symbol in CHART_ENABLED_TICKERS:
            dates, prices = fetch_chart_data(symbol)
            if dates and prices:
                chart_id = f"chart_{symbol}"
                content += f"<canvas id='{chart_id}' width='400' height='150'></canvas>"
                content += f"<script>new Chart(document.getElementById('{chart_id}').getContext('2d'), {{
                    type: 'line',
                    data: {{ labels: {json.dumps(dates)}, datasets: [{{ label: 'USD', data: {json.dumps(prices)}, fill: false, borderColor: 'blue', tension: 0.1 }}] }},
                    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
                }});</script>"
            else:
                content += f"<p style='color:orange;'>Chart data not available for {symbol}</p>"

    content += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

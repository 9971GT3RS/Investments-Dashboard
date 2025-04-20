# update_dashboard.py (mit Beispiel-Chart für Kursentwicklung)
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

# Beispiel-Fokus: Nur META & TSLA für Charts
CHART_ENABLED_TICKERS = ["META", "TSLA"]

# ... (COMPANY_NAMES, EARNINGS_FALLBACK, HEADERS gleich wie vorher)


def fetch_chart_data(ticker):
    try:
        url = f"{CHART_API_BASE}{ticker}?range=30d&interval=1d"
        response = requests.get(url)
        response.raise_for_status()
        chart = response.json()["chart"]["result"][0]
        timestamps = chart["timestamp"]
        prices = chart["indicators"]["quote"][0]["close"]
        dates = [datetime.utcfromtimestamp(ts).strftime("%d.%m") for ts in timestamps]
        return dates, prices
    except Exception as e:
        print(f"Chart data error for {ticker}:", e)
        return [], []

# ... (restliche Funktionen wie fetch_stock_data, fetch_news_gnews, etc.)


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

    exchange_rate = fetch_usd_to_eur()

    for item in data:
        symbol = item.get('symbol', 'N/A')
        name = item.get('shortName') or symbol
        price_usd = item.get('regularMarketPrice', 'N/A')
        change = item.get('regularMarketChangePercent')
        change_text = f"{change:.2f}%" if isinstance(change, (int, float)) else "N/A"
        earnings_raw = "2024-04-24"
        earnings_date = earnings_raw

        eur_display = ""
        if isinstance(price_usd, (int, float)) and exchange_rate:
            price_eur = price_usd * exchange_rate
            eur_display = f" / €{price_eur:.2f}"

        content += f"<h3>{name} ({symbol})</h3>"
        content += f"<p>Price: ${price_usd} ({change_text}){eur_display}</p>"
        content += f"<p>Next earnings: {earnings_date}</p>"

        # === News ===
        news_items = fetch_news_gnews(name)
        if news_items:
            for news in news_items:
                date = news.get('publishedAt', '')[:10]
                title = news.get('title', '')
                url = news.get('url', '#')
                source = news.get('source', {}).get('name', '')
                content += f"<div>• {date} ({source}): <a href='{url}' target='_blank'>{title}</a></div>"
        else:
            content += f"<div>• No recent news available.</div>"

        # === Chart ===
        if symbol in CHART_ENABLED_TICKERS:
            dates, prices = fetch_chart_data(symbol)
            chart_id = f"chart_{symbol}"
            content += f"<canvas id='{chart_id}' width='400' height='150'></canvas>"
            content += f"<script>new Chart(document.getElementById('{chart_id}').getContext('2d'), {{
                type: 'line',
                data: {{
                    labels: {json.dumps(dates)},
                    datasets: [{{
                        label: 'Price (USD)',
                        data: {json.dumps(prices)},
                        fill: false,
                        borderColor: 'blue',
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});</script>"

    content += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)

# === MAIN ===
if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

# update_dashboard.py (funktionierende Version mit News für Shares, gecached)
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
    "Crypto": ["BTC-USD", "ETH-USD"]
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

def fetch_news():
    cache_file = "news_cache.json"
    now = datetime.now()
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
            timestamp = datetime.fromisoformat(cache.get("timestamp", "1970-01-01"))
            if (now - timestamp).total_seconds() < 86400:
                return cache.get("data", {})

    news = {}
    for symbol in GROUPS["Shares"]:
        query = SYMBOL_TO_QUERY.get(symbol, symbol)
        try:
            url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q={query}&language=en&country=us&domain=finance"
            response = requests.get(url)
            response.raise_for_status()
            items = response.json().get("results", [])[:3]
            news[symbol] = [{
                "title": item["title"],
                "link": item["link"],
                "date": item["pubDate"].split("T")[0]
            } for item in items if "title" in item and "link" in item]
        except Exception as e:
            print(f"[NEWS] Error for {symbol}: {e}")

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump({"timestamp": now.isoformat(), "data": news}, f)

    return news

def fetch_chart_data():
    cache_file = "chart_cache.json"
    now = datetime.now()
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
            timestamp = datetime.fromisoformat(cache.get("timestamp", "1970-01-01"))
            if (now - timestamp).total_seconds() < 86400:
                return cache.get("data", {})
    return {}

def fetch_earnings_dates():
    cache_file = "earnings_cache.json"
    now = datetime.now()
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
            timestamp = datetime.fromisoformat(cache.get("timestamp", "1970-01-01"))
            if (now - timestamp).total_seconds() < 86400 and cache.get("data"):
                return cache.get("data", {})
    return {}

def build_html(data):
    utc_now = datetime.now(timezone.utc)
    berlin_time = (utc_now + timedelta(hours=2)).strftime("%d.%m.%Y – %H:%M")

    earnings_map = fetch_earnings_dates()
    charts = fetch_chart_data()
    news_map = fetch_news()

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
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2em; background: #f9f9f9; color: #333; }}
    h1 {{ font-size: 2em; }}
    h2 {{ margin-top: 2em; border-bottom: 2px solid #ccc; padding-bottom: 0.2em; }}
    .entry {{ display: flex; justify-content: space-between; align-items: flex-start; background: #fff; margin: 1em 0; padding: 1em; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }}
    .info {{ width: 48%; }}
    .chart {{ width: 48%; }}
    .positive {{ color: green; }}
    .negative {{ color: red; }}
    .news {{ margin-top: 0.5em; font-size: 0.95em; }}
    .news li {{ margin-bottom: 0.3em; }}
    .news .date {{ color: #999; font-size: 0.9em; margin-left: 0.5em; }}
    canvas {{ width: 100% !important; height: auto !important; }}
  </style>
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
            change_class = "positive" if change and change > 0 else "negative" if change and change < 0 else ""
            price_eur = float(price_usd) * exchange_rate if isinstance(price_usd, (int, float)) else "N/A"
            earnings_date = earnings_map.get(symbol, "N/A")
            chart = charts.get(symbol)
            news = news_map.get(symbol, [])

            html += f"<div class='entry'>"
            html += f"<div class='info'>"
            html += f"<h3>{name} ({symbol})</h3>"
            html += f"<p>Price: ${price_usd} <span class='{change_class}'>({change_text})</span> / €{price_eur:.2f}</p>"
            html += f"<p>Next earnings: {earnings_date}</p>"
            if news:
                html += "<ul class='news'>"
                for n in news:
                    html += f"<li><a href='{n['link']}' target='_blank'>{n['title']}</a><span class='date'>vom {n['date']}</span></li>"
                html += "</ul>"
            html += "</div>"

            if chart:
                chart_id = f"chart_{symbol}"
                labels = [point["label"] for point in chart]
                values = [point["value"] for point in chart]
                html += f"<div class='chart'><canvas id='{chart_id}'></canvas></div>"
                html += """
<script>
new Chart(document.getElementById('{id}').getContext('2d'), {{
  type: 'line',
  data: {{
    labels: {labels},
    datasets: [{{
      label: '30-Day Price',
      data: {values},
      borderColor: '#0074D9',
      backgroundColor: 'rgba(0, 116, 217, 0.1)',
      fill: true,
      tension: 0.3
    }}]
  }},
  options: {{
    responsive: true,
    scales: {{
      y: {{ beginAtZero: false }}
    }}
  }}
}});
</script>
""".format(id=chart_id, labels=labels, values=values)
            html += "</div>"

    html += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

# update_dashboard.py (alphabetische Shares, plus Ölpreis und USD/EUR Wechselkurs mit Chart)
import requests
from datetime import datetime, timedelta, timezone
import json
import os

FMP_API_KEY = "ITys2XTLibnUOmblYKvkn59LlBeLOoWU"
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
EXCHANGE_RATE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"

GROUPS = {
    "Shares": [
        "AMD", "AMZN", "ASML", "BABA", "CRM", "CRWD", "GOOGL", "ILMN", "META", "MRVL", "MSFT", "MU", "NKE", "NOW", "NVDA", "OXY", "PAYPL", "PLTR", "RNKGF", "RNMBF", "SQ", "TSLA", "TSM", "UAA", "XOM", "XPEV"
    ],
    "Indices": ["^GSPC", "^NDX"],
    "Crypto": ["BTC-USD", "ETH-USD"],
    "Commodities": ["WTI"],
    "FX": ["USD-EUR"]
}

ALL_TICKERS = GROUPS["Shares"] + GROUPS["Crypto"] + GROUPS["Indices"]

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
            try:
                cache = json.load(f)
                timestamp = datetime.fromisoformat(cache.get("timestamp", "1970-01-01"))
                if (now - timestamp).total_seconds() < 86400:
                    return cache.get("data", {})
            except json.JSONDecodeError:
                print("Chart cache file is invalid.")
    return {}

def fetch_earnings_dates():
    cache_file = "earnings_cache.json"
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            try:
                cache = json.load(f)
                return cache.get("data", {})
            except json.JSONDecodeError:
                print("Earnings cache file is invalid.")
    return {}

def fetch_commodities_and_fx():
    try:
        # Ölpreis WTI (simuliert)
        wti_price = 66.23  # Fester Wert, da keine kostenlose Echtzeitquelle verfügbar ist

        # USD-EUR Wechselkurs
        response = requests.get(EXCHANGE_RATE_API)
        response.raise_for_status()
        usd_to_eur = response.json()['rates']['EUR']
        usd_per_eur = round(1 / usd_to_eur, 4)

        return {"WTI": wti_price, "USD-EUR": usd_per_eur}
    except Exception as e:
        print("Error fetching commodities or fx:", e)
        return {"WTI": "N/A", "USD-EUR": "N/A"}

def build_html(data):
    utc_now = datetime.now(timezone.utc)
    berlin_time = (utc_now + timedelta(hours=2)).strftime("%d.%m.%Y – %H:%M")

    earnings_map = fetch_earnings_dates()
    charts = fetch_chart_data()
    commodities_fx = fetch_commodities_and_fx()

    try:
        exchange_rate = requests.get(EXCHANGE_RATE_API).json()['rates']['EUR']
    except:
        exchange_rate = 1.0

    data_by_symbol = {item.get('symbol'): item for item in data}

    html = """
<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Market Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 2em; background: #f9f9f9; color: #333; }
    h1 { font-size: 2em; }
    h2 { margin-top: 2em; border-bottom: 2px solid #ccc; padding-bottom: 0.2em; }
    .entry { display: flex; justify-content: space-between; align-items: flex-start; background: #fff; margin: 1em 0; padding: 1em; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
    .info { width: 48%; }
    .chart { width: 48%; }
    .positive { color: green; }
    .negative { color: red; }
    canvas { width: 100% !important; height: auto !important; }
  </style>
</head>
<body>
<h1>Market Dashboard</h1>
<p>Last updated: """ + berlin_time + """ (Berlin Time)</p>
"""

    for group_name, tickers in GROUPS.items():
        html += f"<h2>{group_name}</h2>"
        for symbol in sorted(tickers):
            if group_name in ["Commodities", "FX"]:
                value = commodities_fx.get(symbol, "N/A")
                html += f"<div class='entry'><div class='info'><h3>{symbol}</h3><p>Value: {value}</p></div></div>"
                continue

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

            html += f"<div class='entry'>"
            html += f"<div class='info'>"
            html += f"<h3>{name} ({symbol})</h3>"
            html += f"<p>Price: ${price_usd} <span class='{change_class}'>({change_text})</span> / €{price_eur:.2f}</p>"
            html += f"<p>Next earnings: {earnings_date}</p>"
            html += "</div>"

            if chart:
                chart_id = f"chart_{symbol}"
                labels = [point["label"] for point in chart]
                values = [point["value"] for point in chart]
                chart_script = f"""
<div class='chart'>
  <canvas id='{chart_id}'></canvas>
  <script>
    new Chart(document.getElementById('{chart_id}').getContext('2d'), {{
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
        scales: {{ y: {{ beginAtZero: false }} }}
      }}
    }});
  </script>
</div>
"""
                html += chart_script
            html += "</div>"

    html += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

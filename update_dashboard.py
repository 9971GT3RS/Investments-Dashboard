# update_dashboard.py (vollständig – inkl. build_html und main block)
import requests
from datetime import datetime, timedelta, timezone
import json
import os

FMP_API_KEY = "ITys2XTLibnUOmblYKvkn59LlBeLOoWU"
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
NEWSDATA_API_KEY = "pub_8178059be021e6dbfd5d7ad623f9f93f1a9f5"
EXCHANGE_RATE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"
EARNINGS_API = "https://financialmodelingprep.com/api/v3/earning_calendar"

GROUPS = { ... }  # gleich wie bisher
NEWS_QUERY_OVERRIDES = { ... }  # gleich wie bisher
ALL_TICKERS = GROUPS["Shares"] + GROUPS["Indices"] + GROUPS["Crypto"]
HEADERS = { ... }  # gleich wie bisher

# fetch_stock_data(), fetch_news(), fetch_earnings_dates() – alles wie oben

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
<h1>Market News Dashboard</h1>
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

            query = NEWS_QUERY_OVERRIDES.get(symbol, name)
            news = fetch_news(query)
            if news:
                html += "<ul>"
                for article in news[:5]:
                    html += f"<li><a href='{article['link']}' target='_blank'>{article['title']}</a></li>"
                html += "</ul>"
            else:
                html += "<p><i>No recent news available.</i></p>"

    html += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

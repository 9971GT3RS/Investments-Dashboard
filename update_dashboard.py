# update_dashboard.py (mit Yahoo Finance Kursdaten + echte News via FMP)
import requests
from datetime import datetime, timedelta

# === CONFIG ===
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
FMP_API_KEY = "ITys2XTLibnUOmblYKvkn59LlBeLOoWU"  # ✅ dein FMP API-Key

TICKERS = ["META", "GOOGL", "AMZN", "PYPL", "NVDA", "AMD", "CRWD", "ASML", "MSFT",
           "CRM", "NOW", "TSLA", "TSM", "SQ", "ILMN", "MU", "MRVL", "NKE", "RENK.DE",
           "XOM", "OXY", "UAA", "BABA", "XPEV"]

HEADERS = {
    "x-rapidapi-key": YAHOO_API_KEY,
    "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
}

# === FUNCTIONS ===
def fetch_stock_data():
    try:
        params = {"symbols": ",".join(TICKERS), "region": "US"}
        response = requests.get(YAHOO_API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json().get("quoteResponse", {}).get("result", [])
    except Exception as e:
        print("Error fetching stock data:", e)
        return None

def fetch_news_fmp(ticker):
    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&limit=5&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        one_week_ago = datetime.now() - timedelta(days=7)
        return [n for n in news_data if datetime.strptime(n['publishedDate'], "%Y-%m-%d %H:%M:%S") >= one_week_ago]
    except Exception as e:
        print(f"News error for {ticker}:", e)
        return []

def build_html(data):
    now = datetime.now().strftime("%B %d, %Y – %H:%M")
    content = f"""
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><title>Market Dashboard</title></head>
<body>
<h1>Market News Dashboard</h1>
<p>Last updated: {now}</p>
"""

    if not data:
        content += "<p><strong style='color:red;'>⚠️ Could not load stock data. Please check your API key or limits.</strong></p>"
    else:
        for item in data:
            name = item.get('shortName') or item.get('symbol', 'N/A')
            symbol = item.get('symbol', 'N/A')
            price = item.get('regularMarketPrice', 'N/A')
            change = item.get('regularMarketChangePercent')
            change_text = f"{change:.2f}%" if isinstance(change, (int, float)) else "N/A"
            content += f"<h3>{name} ({symbol})</h3>"
            content += f"<p>Price: ${price} ({change_text})</p>"
            content += f"<p>Next earnings: [manual entry or API]</p>"

            news_items = fetch_news_fmp(symbol)
            if news_items:
                for news in news_items:
                    title = news['title']
                    date = news['publishedDate'].split(" ")[0]
                    summary = news.get('text', '')
                    url = news.get('url', '#')
                    content += f"<div>• {date}: <a href='{url}' target='_blank'>{title}</a> – {summary}</div>"
            else:
                content += f"<div>• No recent news available.</div>"

    content += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)

# === MAIN ===
if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

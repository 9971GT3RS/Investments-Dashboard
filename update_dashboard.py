# update_dashboard.py
import requests
from datetime import datetime, timedelta

# === CONFIG ===
YAHOO_API_URL = "https://yfapi.net/v6/finance/quote"
x-rapidapi-key = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"

TICKERS = ["META", "GOOGL", "AMZN", "PYPL", "NVDA", "AMD", "CRWD", "ASML", "MSFT",
           "CRM", "NOW", "TSLA", "TSM", "SQ", "ILMN", "MU", "MRVL", "NKE", "RENK.DE",
           "XOM", "OXY", "UAA", "BABA", "XPEV"]

HEADERS = {
    "x-api-key": API_KEY,
    "accept": "application/json"
}

# === FUNCTIONS ===
def fetch_stock_data():
    try:
        response = requests.get(YAHOO_API_URL, headers=HEADERS, params={"symbols": ",".join(TICKERS)})
        response.raise_for_status()
        return response.json().get("quoteResponse", {}).get("result", [])
    except Exception as e:
        print("Error fetching stock data:", e)
        return None

def fetch_dummy_news():
    today = datetime.now()
    last_week = today - timedelta(days=7)
    return [
        {"title": "Sample News Title", "date": today.strftime("%Y-%m-%d"), "summary": "Example summary from the past week."},
        {"title": "Older News", "date": last_week.strftime("%Y-%m-%d"), "summary": "This would be deleted automatically."}
    ]

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
            for news in fetch_dummy_news():
                date = datetime.strptime(news['date'], "%Y-%m-%d")
                if date >= datetime.now() - timedelta(days=7):
                    content += f"<div>• {news['date']}: {news['title']} – {news['summary']}</div>"

    content += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)

# === MAIN ===
if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

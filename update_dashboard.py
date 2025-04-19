# update_dashboard.py
import requests
from datetime import datetime, timedelta

YAHOO_API_URL = "https://yfapi.net/v6/finance/quote"
API_KEY = "YOUR_RAPIDAPI_KEY"

TICKERS = ["META", "GOOGL", "AMZN", "PYPL", "NVDA", "AMD", "CRWD", "ASML", "MSFT",
           "CRM", "NOW", "TSLA", "TSM", "SQ", "ILMN", "MU", "MRVL", "NKE", "RENK.DE",
           "XOM", "OXY", "UAA", "BABA", "XPEV"]

HEADERS = {
    "x-api-key": API_KEY,
    "accept": "application/json"
}

def fetch_stock_data():
    response = requests.get(YAHOO_API_URL, headers=HEADERS, params={"symbols": ",".join(TICKERS)})
    if response.status_code == 200:
        return response.json()["quoteResponse"]["result"]
    else:
        print("Error fetching stock data:", response.text)
        return []

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
    for item in data:
        content += f"<h3>{item['shortName']} ({item['symbol']})</h3>"
        content += f"<p>Price: ${item['regularMarketPrice']} ({item['regularMarketChangePercent']:.2f}%)</p>"
        content += f"<p>Next earnings: [manual entry or API]</p>"
        for news in fetch_dummy_news():
            if datetime.strptime(news['date'], "%Y-%m-%d") >= datetime.now() - timedelta(days=7):
                content += f"<div>• {news['date']}: {news['title']} – {news['summary']}</div>"
    content += "</body></html>"
    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

# update_dashboard.py (mit Debug-Infos für Earnings und EUR-Kurs)
import requests
from datetime import datetime, timedelta, timezone

# === CONFIG ===
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
FMP_API_KEY = "ITys2XTLibnUOmblYKvkn59LlBeLOoWU"
EXCHANGE_RATE_API = "https://api.exchangerate.host/latest?base=USD&symbols=EUR"

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

def fetch_all_earnings():
    today = datetime.today().strftime("%Y-%m-%d")
    future = (datetime.today() + timedelta(days=120)).strftime("%Y-%m-%d")
    url = f"https://financialmodelingprep.com/api/v3/earning_calendar?from={today}&to={future}&apikey={FMP_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Earnings calendar error:", e)
        return []

def get_earnings_for_ticker(ticker, earnings_data):
    normalized = ticker.upper().replace(".DE", "")
    for entry in earnings_data:
        if entry['symbol'].upper().replace(".DE", "") == normalized:
            return entry.get('date', 'N/A')
    return "N/A (not found in earnings calendar)"

def fetch_usd_to_eur():
    try:
        response = requests.get(EXCHANGE_RATE_API)
        response.raise_for_status()
        data = response.json()
        return data['rates']['EUR']
    except Exception as e:
        print("Exchange rate error:", e)
        return None

def build_html(data):
    utc_now = datetime.now(timezone.utc)
    berlin_offset = timedelta(hours=2)
    berlin_time = (utc_now + berlin_offset).strftime("%B %d, %Y – %H:%M")

    content = f"""
<!DOCTYPE html>
<html lang='en'>
<head><meta charset='UTF-8'><title>Market Dashboard</title></head>
<body>
<h1>Market News Dashboard</h1>
<p>Last updated: {berlin_time} (Berlin Time)</p>
"""

    earnings_data = fetch_all_earnings()
    exchange_rate = fetch_usd_to_eur()

    if exchange_rate is None:
        content += "<p><strong style='color:red;'>⚠️ EUR conversion unavailable (API error)</strong></p>"

    if not data:
        content += "<p><strong style='color:red;'>⚠️ Could not load stock data. Please check your API key or limits.</strong></p>"
    else:
        for item in data:
            name = item.get('shortName') or item.get('symbol', 'N/A')
            symbol = item.get('symbol', 'N/A')
            price_usd = item.get('regularMarketPrice', 'N/A')
            change = item.get('regularMarketChangePercent')
            change_text = f"{change:.2f}%" if isinstance(change, (int, float)) else "N/A"
            earnings_date = get_earnings_for_ticker(symbol, earnings_data)

            if isinstance(price_usd, (int, float)) and exchange_rate:
                price_eur = price_usd * exchange_rate
                eur_display = f" / €{price_eur:.2f}"
            else:
                eur_display = " (EUR unavailable)"

            content += f"<h3>{name} ({symbol})</h3>"
            content += f"<p>Price: ${price_usd} ({change_text}){eur_display}</p>"
            content += f"<p>Next earnings: {earnings_date}</p>"

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

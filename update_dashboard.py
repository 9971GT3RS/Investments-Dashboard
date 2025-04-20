# update_dashboard.py (mit GNews API für zuverlässige Finanznachrichten)
import requests
from datetime import datetime, timedelta, timezone

# === CONFIG ===
YAHOO_API_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
YAHOO_API_KEY = "90bd89d333msh8e2d2a6b2dca946p1b69edjsn6f4c7fe55d2a"
GNEWS_API_KEY = "83df462ceeaf456d4d178309ca672e41"
EXCHANGE_RATE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"

TICKERS = ["META", "GOOGL", "AMZN", "PYPL", "NVDA", "AMD", "CRWD", "ASML", "MSFT",
           "CRM", "NOW", "TSLA", "TSM", "SQ", "XYZ", "ILMN", "MU", "MRVL", "NKE",
           "RNKGF", "RNMBF", "PLTR", "XOM", "OXY", "UAA", "BABA", "XPEV",
           "^GSPC", "^NDX", "BTC-USD", "ETH-USD"]

COMPANY_NAMES = {
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
    "XYZ": "Block Inc",
    "ILMN": "Illumina",
    "MU": "Micron Technology",
    "MRVL": "Marvell Technology",
    "NKE": "Nike",
    "RNKGF": "Renk",
    "RNMBF": "Rheinmetall",
    "PLTR": "Palantir",
    "XOM": "ExxonMobil",
    "OXY": "Occidental Petroleum",
    "UAA": "Under Armour",
    "BABA": "Alibaba",
    "XPEV": "Xpeng",
    "^GSPC": "S&P 500",
    "^NDX": "Nasdaq 100",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum"
}

EARNINGS_FALLBACK = {
    "META": "2024-04-24",
    "GOOGL": "2024-04-23",
    "AMZN": "2024-04-25",
    "PYPL": "2024-05-01",
    "NVDA": "2024-05-22",
    "AMD": "2024-04-30",
    "CRWD": "2024-06-01",
    "ASML": "2024-04-17",
    "MSFT": "2024-04-25",
    "CRM": "2024-06-05",
    "NOW": "2024-04-24",
    "TSLA": "2024-04-23",
    "TSM": "2024-04-18",
    "SQ": "2024-05-02",
    "XYZ": "2024-05-02",
    "ILMN": "2024-05-07",
    "MU": "2024-06-20",
    "MRVL": "2024-06-05",
    "NKE": "2024-06-27",
    "RNKGF": "2024-08-12",
    "RNMBF": "2024-05-08",
    "PLTR": "2024-05-06",
    "XOM": "2024-04-26",
    "OXY": "2024-05-08",
    "UAA": "2024-05-09",
    "BABA": "2024-05-15",
    "XPEV": "2024-05-20"
}

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

def fetch_news_gnews(company_name):
    try:
        url = f"https://gnews.io/api/v4/search?q=\"{company_name}\"&token={GNEWS_API_KEY}&lang=en&max=3"
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return articles
    except Exception as e:
        print(f"GNews error for {company_name}:", e)
        return []

def fetch_usd_to_eur():
    try:
        response = requests.get(EXCHANGE_RATE_API)
        response.raise_for_status()
        data = response.json()
        return data['rates']['EUR']
    except Exception as e:
        print("Exchange rate error:", e)
        return None

def format_date_german(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d.%m.%Y")
    except:
        return date_str

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

    exchange_rate = fetch_usd_to_eur()
    if exchange_rate is None:
        content += "<p><strong style='color:red;'>⚠️ EUR conversion unavailable (API error)</strong></p>"

    sorted_data = sorted(data, key=lambda x: x.get('shortName', x.get('symbol', '')))

    for item in sorted_data:
        symbol = item.get('symbol', 'N/A')
        name = item.get('shortName') or symbol
        price_usd = item.get('regularMarketPrice', 'N/A')
        change = item.get('regularMarketChangePercent')
        change_text = f"{change:.2f}%" if isinstance(change, (int, float)) else "N/A"
        earnings_raw = EARNINGS_FALLBACK.get(symbol, 'N/A')
        earnings_date = format_date_german(earnings_raw)

        if isinstance(price_usd, (int, float)) and exchange_rate:
            price_eur = price_usd * exchange_rate
            eur_display = f" / €{price_eur:.2f}"
        else:
            eur_display = " (EUR unavailable)"

        content += f"<h3>{name} ({symbol})</h3>"
        content += f"<p>Price: ${price_usd} ({change_text}){eur_display}</p>"
        content += f"<p>Next earnings: {earnings_date}</p>"

        company_name = COMPANY_NAMES.get(symbol, name)
        news_items = fetch_news_gnews(company_name)
        if news_items:
            for news in news_items:
                date = format_date_german(news.get('publishedAt', ''))
                title = news.get('title', '')
                url = news.get('url', '#')
                source = news.get('source', {}).get('name', '')
                content += f"<div>• {date} ({source}): <a href='{url}' target='_blank'>{title}</a></div>"
        else:
            content += f"<div>• No recent news available.</div>"

    content += "</body></html>"

    with open("boersen-dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)

# === MAIN ===
if __name__ == "__main__":
    stock_data = fetch_stock_data()
    build_html(stock_data)

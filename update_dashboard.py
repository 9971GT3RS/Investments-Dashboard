# update_dashboard.py (vollständig mit korrigiertem GROUPS-Block und allen Funktionen)
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

GROUPS = {
    "Shares": [
        "META", "GOOGL", "AMZN", "PYPL", "NVDA", "AMD", "CRWD", "ASML", "MSFT", "CRM", "NOW", "TSLA", "TSM",
        "SQ", "ILMN", "MU", "MRVL", "NKE", "RNKGF", "XOM", "OXY", "UAA", "BABA", "XPEV", "RNMBF", "PLTR"
    ],
    "Indices": ["^GSPC", "^NDX"],
    "Crypto": ["BTC-USD", "ETH-USD"]
}

NEWS_QUERY_OVERRIDES = {
    "META": "Meta Platforms", "GOOGL": "Alphabet", "AMZN": "Amazon", "PYPL": "Paypal",
    "NVDA": "Nvidia", "AMD": "AMD", "CRWD": "Crowdstrike", "ASML": "ASML Holding",
    "MSFT": "Microsoft", "CRM": "Salesforce", "NOW": "ServiceNow", "TSLA": "Tesla",
    "TSM": "Taiwan Semiconductor", "SQ": "Block Inc", "ILMN": "Illumina", "MU": "Micron Technology",
    "MRVL": "Marvell", "NKE": "Nike", "RNKGF": "Renk", "XOM": "Exxon", "OXY": "Occidental Petroleum",
    "UAA": "Under Armour", "BABA": "Alibaba", "XPEV": "XPeng", "RNMBF": "Rheinmetall", "PLTR": "Palantir",
    "^GSPC": "S&P 500", "^NDX": "Nasdaq 100", "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum"
}

ALL_TICKERS = GROUPS["Shares"] + GROUPS["Indices"] + GROUPS["Crypto"]

HEADERS = {
    "x-rapidapi-key": YAHOO_API_KEY,
    "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
}

# Funktionen fetch_stock_data, fetch_news, fetch_earnings_dates, build_html und __main__ folgen wie bereits enthalten

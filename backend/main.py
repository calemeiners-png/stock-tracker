from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import requests
from datetime import datetime, timedelta
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

SCAN_LIST = [
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "ARKK", "ARKW", "ARKG",
    "XLF", "XLK", "XLE", "XLV", "XLI", "XLB", "XLU", "XLP", "XLY",
    "GLD", "SLV", "USO", "TLT", "HYG", "LQD", "EEM", "VXX", "SQQQ",
    "TQQQ", "SPXU", "UVXY", "BITI", "BITO",
    "AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "AMZN", "META", "TSLA",
    "AVGO", "ORCL", "AMD", "INTC", "QCOM", "TXN", "MU", "AMAT", "LRCX",
    "KLAC", "MRVL", "SMCI", "ARM", "ASML",
    "CRM", "ADBE", "NOW", "SNOW", "PLTR", "DDOG", "NET", "CRWD", "ZS",
    "PANW", "OKTA", "MDB", "GTLB", "HUBS", "TEAM", "WDAY", "VEEV",
    "SHOP", "TWLO", "ZM", "DOCU", "BOX", "DOCN",
    "JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "SCHW", "AXP",
    "V", "MA", "PYPL", "SQ", "COF", "USB", "PNC", "TFC", "BX", "KKR",
    "XOM", "CVX", "COP", "SLB", "OXY", "EOG", "PXD", "MPC", "VLO",
    "PSX", "HAL", "BKR", "DVN", "FANG", "APA", "HES",
    "JNJ", "PFE", "UNH", "ABBV", "MRK", "LLY", "BMY", "AMGN", "GILD",
    "BIIB", "REGN", "VRTX", "MRNA", "BNTX", "ILMN", "DXCM", "ISRG",
    "SYK", "MDT", "ABT", "TMO", "DHR", "A", "IDXX",
    "WMT", "HD", "MCD", "SBUX", "NKE", "TGT", "COST", "LOW", "TJX",
    "BABA", "JD", "PDD", "MELI", "SE", "GRAB", "DASH", "UBER", "LYFT",
    "ABNB", "BKNG", "EXPE", "MAR", "HLT",
    "DIS", "NFLX", "PARA", "WBD", "CMCSA", "T", "VZ", "TMUS", "CHTR",
    "SPOT", "RBLX", "EA", "TTWO",
    "F", "GM", "RIVN", "LCID", "NIO", "LI", "XPEV",
    "AMT", "PLD", "CCI", "EQIX", "SPG", "O", "VICI", "AVB", "EQR",
    "BA", "LMT", "RTX", "NOC", "GD", "HON", "GE", "CAT", "DE",
    "MMM", "EMR", "ETN", "ITW", "PH", "ROK",
    "COIN", "MSTR", "RIOT", "MARA", "CLSK", "CIFR", "HUT",
    "SOFI", "HOOD", "UPST", "AFRM", "LC",
    "PLUG", "FCEL", "BLNK", "CHPT", "ENVX", "LAZR", "JOBY", "ACHR",
]

SCAN_LIST = list(dict.fromkeys(SCAN_LIST))


@app.get("/")
def root():
    return {"status": "Stock Tracker API is running"}


@app.get("/stock/{ticker}")
def get_stock(ticker: str):
    ticker = ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol required")
    stock = yf.Ticker(ticker)
    try:
        info = stock.info or {}
    except Exception:
        info = {}
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    change_pct = info.get("52WeekChange")
    name = info.get("longName") or info.get("shortName") or ticker
    return {
        "ticker": ticker,
        "name": name,
        "price": price,
        "change_pct": change_pct,
        "volume": info.get("volume"),
        "market_cap": info.get("marketCap"),
    }


@app.get("/scan")
def scan_market():
    results = []
    threshold = 2.0
    for ticker in SCAN_LIST:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
            name = info.get("longName") or info.get("shortName") or ticker
            volume = info.get("volume") or 0
            avg_volume = info.get("averageVolume") or 1
            if not price or not prev_close:
                continue
            change_pct = ((price - prev_close) / prev_close) * 100
            volume_ratio = volume / avg_volume if avg_volume else 1
            if abs(change_pct) >= threshold:
                results.append({
                    "ticker": ticker,
                    "name": name,
                    "price": round(price, 2),
                    "change_pct": round(change_pct, 2),
                    "volume_ratio": round(volume_ratio, 2),
                    "direction": "up" if change_pct > 0 else "down",
                    "scanned_at": datetime.now().isoformat(),
                })
        except Exception:
            continue
    results.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return {"movers": results, "total": len(results), "scanned": len(SCAN_LIST)}


@app.get("/chart/{ticker}")
def get_chart(ticker: str, period: str = "6mo"):
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period=period)
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data found")
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime("%b %d"),
                "price": round(row["Close"], 2),
                "volume": int(row["Volume"]),
            })
        return {"ticker": ticker.upper(), "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/news/{ticker}")
def get_news(ticker: str):
    try:
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker.upper()}&from={start}&to={end}&token={FINNHUB_API_KEY}"
        res = requests.get(url, timeout=10)
        data = res.json()
        articles = []
        for item in data[:5]:
            articles.append({
                "headline": item.get("headline", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                "summary": item.get("summary", "")[:200],
                "datetime": datetime.fromtimestamp(item.get("datetime", 0)).strftime("%b %d, %Y"),
            })
        return {"ticker": ticker.upper(), "articles": articles}
    except Exception:
        return {"ticker": ticker.upper(), "articles": []}


@app.get("/volume-spikes")
def volume_spikes():
    results = []
    threshold = 3.0
    for ticker in SCAN_LIST:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
            name = info.get("longName") or info.get("shortName") or ticker
            volume = info.get("volume") or 0
            avg_volume = info.get("averageVolume") or 1
            if not price or not volume or not avg_volume:
                continue
            volume_ratio = volume / avg_volume
            if volume_ratio >= threshold:
                change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
                results.append({
                    "ticker": ticker,
                    "name": name,
                    "price": round(price, 2),
                    "change_pct": round(change_pct, 2),
                    "volume": volume,
                    "avg_volume": avg_volume,
                    "volume_ratio": round(volume_ratio, 2),
                    "direction": "up" if change_pct > 0 else "down",
                    "scanned_at": datetime.now().isoformat(),
                })
        except Exception:
            continue
    results.sort(key=lambda x: x["volume_ratio"], reverse=True)
    return {"spikes": results, "total": len(results), "scanned": len(SCAN_LIST)}
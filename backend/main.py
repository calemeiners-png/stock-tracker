from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Big list of stocks and ETFs to scan
SCAN_LIST = [
    # Major ETFs
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "ARK", "ARKK", "ARKW",
    # Tech
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD",
    "INTC", "CRM", "ORCL", "NFLX", "ADBE", "PYPL", "SHOP", "SNOW",
    # Finance
    "JPM", "BAC", "GS", "MS", "WFC", "V", "MA", "AXP",
    # Energy
    "XOM", "CVX", "COP", "SLB", "OXY",
    # Health
    "JNJ", "PFE", "UNH", "ABBV", "MRK", "LLY",
    # Consumer
    "WMT", "AMZN", "HD", "MCD", "SBUX", "NKE", "DIS",
]


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
    """
    Scan all tickers and return ones moving significantly today.
    Flags anything up or down more than 2% on the day.
    """
    results = []
    threshold = 2.0  # percent

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

    # Sort by biggest movers first
    results.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return {"movers": results, "total": len(results), "scanned": len(SCAN_LIST)}
@app.get("/chart/{ticker}")
def get_chart(ticker: str, period: str = "6mo"):
    """Return historical price data for charting."""
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
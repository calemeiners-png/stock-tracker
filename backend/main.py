from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import requests
import concurrent.futures
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

# Focused list for faster volume spike scanning
VOLUME_SCAN_LIST = [
    "SPY", "QQQ", "TQQQ", "SQQQ", "UVXY", "VXX",
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL", "AMD",
    "PLTR", "COIN", "MSTR", "RIOT", "MARA",
    "JPM", "BAC", "GS", "V", "MA",
    "XOM", "CVX", "OXY",
    "ZS", "CRWD", "NET", "PANW", "SNOW", "DDOG",
    "SOFI", "HOOD", "UPST", "AFRM",
    "NIO", "RIVN", "LCID", "F", "GM",
    "JNJ", "PFE", "MRNA", "LLY", "UNH",
    "BABA", "PDD", "JD", "BIDU",
    "ARKK", "GLD", "SLV", "USO",
]


def fetch_ticker_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        fast = stock.fast_info
        price = fast.last_price
        prev_close = fast.previous_close
        volume = fast.last_volume
        avg_volume = fast.three_month_average_volume
        return {
            "price": price,
            "prev_close": prev_close,
            "volume": volume,
            "avg_volume": avg_volume,
        }
    except Exception:
        return None


@app.get("/")
def root():
    return {"status": "Stock Tracker API is running"}


@app.get("/stock/{ticker}")
def get_stock(ticker: str):
    ticker = ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol required")
    try:
        stock = yf.Ticker(ticker)
        try:
            fast = stock.fast_info
            price = fast.last_price
            prev_close = fast.previous_close
            market_cap = fast.market_cap
            volume = fast.three_month_average_volume
            change_pct = ((price - prev_close) / prev_close) if price and prev_close else None
            name = ticker
            try:
                info = stock.info or {}
                name = info.get("longName") or info.get("shortName") or ticker
            except Exception:
                pass
            return {
                "ticker": ticker,
                "name": name,
                "price": round(price, 2) if price else None,
                "change_pct": round(change_pct, 4) if change_pct else None,
                "volume": int(volume) if volume else None,
                "market_cap": int(market_cap) if market_cap else None,
            }
        except Exception:
            pass
        hist = stock.history(period="2d")
        if not hist.empty and len(hist) >= 1:
            price = round(hist["Close"].iloc[-1], 2)
            prev_close = round(hist["Close"].iloc[-2], 2) if len(hist) >= 2 else price
            volume = int(hist["Volume"].iloc[-1])
            change_pct = round((price - prev_close) / prev_close, 4) if prev_close else None
            return {
                "ticker": ticker,
                "name": ticker,
                "price": price,
                "change_pct": change_pct,
                "volume": volume,
                "market_cap": None,
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    raise HTTPException(status_code=404, detail="No data found")


@app.get("/scan")
def scan_market():
    results = []
    threshold = 2.0

    def check_ticker(ticker):
        data = fetch_ticker_data(ticker)
        if not data:
            return None
        price = data["price"]
        prev_close = data["prev_close"]
        volume = data["volume"]
        avg_volume = data["avg_volume"]
        if not price or not prev_close:
            return None
        change_pct = ((price - prev_close) / prev_close) * 100
        volume_ratio = volume / avg_volume if avg_volume else 1
        if abs(change_pct) >= threshold:
            return {
                "ticker": ticker,
                "name": ticker,
                "price": round(price, 2),
                "change_pct": round(change_pct, 2),
                "volume_ratio": round(volume_ratio, 2),
                "direction": "up" if change_pct > 0 else "down",
                "scanned_at": datetime.now().isoformat(),
            }
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(check_ticker, t): t for t in SCAN_LIST}
        for future in concurrent.futures.as_completed(future_to_ticker, timeout=120):
            try:
                result = future.result(timeout=5)
                if result:
                    results.append(result)
            except Exception:
                continue

    results.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return {"movers": results, "total": len(results), "scanned": len(SCAN_LIST)}


@app.get("/chart/{ticker}")
def get_chart(ticker: str, period: str = "6mo"):
    try:
        # Map custom periods to yfinance periods
        period_map = {
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "2y": "2y",
            "5y": "5y",
            "10y": "10y",
        }
        yf_period = period_map.get(period, "6mo")

        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period=yf_period)
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data found")

        data = []
        for date, row in hist.iterrows():
            # Include year for longer periods
            if period in ("1y", "2y", "5y", "10y"):
                date_str = date.strftime("%b %d '%y")
            else:
                date_str = date.strftime("%b %d")

            data.append({
                "date": date_str,
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
def volume_spikes(threshold: float = 3.0):
    results = []

    def check_ticker(ticker):
        data = fetch_ticker_data(ticker)
        if not data:
            return None
        price = data["price"]
        prev_close = data["prev_close"]
        volume = data["volume"]
        avg_volume = data["avg_volume"]
        if not price or not volume or not avg_volume:
            return None
        volume_ratio = volume / avg_volume
        if volume_ratio >= threshold:
            change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
            return {
                "ticker": ticker,
                "name": ticker,
                "price": round(price, 2),
                "change_pct": round(change_pct, 2),
                "volume": int(volume),
                "avg_volume": int(avg_volume),
                "volume_ratio": round(volume_ratio, 2),
                "direction": "up" if change_pct > 0 else "down",
                "scanned_at": datetime.now().isoformat(),
            }
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(check_ticker, t): t for t in VOLUME_SCAN_LIST}
        for future in concurrent.futures.as_completed(future_to_ticker, timeout=120):
            try:
                result = future.result(timeout=5)
                if result:
                    results.append(result)
            except Exception:
                continue

    results.sort(key=lambda x: x["volume_ratio"], reverse=True)
    return {"spikes": results, "total": len(results), "scanned": len(VOLUME_SCAN_LIST)}


@app.get("/insider/{ticker}")
def get_insider_trades(ticker: str):
    """Fetch recent insider trades for a ticker from Finnhub."""
    try:
        url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={ticker.upper()}&token={FINNHUB_API_KEY}"
        res = requests.get(url, timeout=10)
        data = res.json()

        trades = []
        for item in data.get("data", [])[:10]:
            shares = item.get("share", 0)
            price = item.get("price", 0)
            value = round(shares * price) if shares and price else 0
            trade_type = item.get("transactionCode", "")

            # Simplify transaction codes
            if trade_type in ("P", "Buy"):
                action = "buy"
            elif trade_type in ("S", "Sell"):
                action = "sell"
            else:
                action = trade_type.lower()

            trades.append({
                "name": item.get("name", "Unknown"),
                "title": item.get("position", ""),
                "action": action,
                "shares": shares,
                "price": price,
                "value": value,
                "date": item.get("transactionDate", ""),
                "filing_date": item.get("filingDate", ""),
            })

        return {"ticker": ticker.upper(), "trades": trades}
    except Exception as e:
        return {"ticker": ticker.upper(), "trades": []}


@app.get("/insider-feed")
def insider_feed():
    """Get recent insider trades across all major stocks."""
    try:
        # Finnhub provides a general insider transactions endpoint
        tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL",
                   "JPM", "BAC", "GS", "XOM", "CVX", "UNH", "LLY", "V", "MA"]
        all_trades = []

        def fetch_insider(ticker):
            try:
                url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={ticker}&token={FINNHUB_API_KEY}"
                res = requests.get(url, timeout=10)
                data = res.json()
                trades = []
                for item in data.get("data", [])[:3]:
                    shares = item.get("share", 0)
                    price = item.get("price", 0)
                    value = round(shares * price) if shares and price else 0
                    trade_type = item.get("transactionCode", "")
                    if trade_type in ("P", "Buy"):
                        action = "buy"
                    elif trade_type in ("S", "Sell"):
                        action = "sell"
                    else:
                        action = trade_type.lower()
                    if action in ("buy", "sell"):
                        trades.append({
                            "ticker": ticker,
                            "name": item.get("name", "Unknown"),
                            "title": item.get("position", ""),
                            "action": action,
                            "shares": shares,
                            "price": price,
                            "value": value,
                            "date": item.get("transactionDate", ""),
                        })
                return trades
            except Exception:
                return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_insider, t): t for t in tickers}
            for future in concurrent.futures.as_completed(futures, timeout=30):
                try:
                    result = future.result(timeout=5)
                    all_trades.extend(result)
                except Exception:
                    continue

        all_trades.sort(key=lambda x: x.get("date", ""), reverse=True)
        return {"trades": all_trades[:30]}
    except Exception as e:
        return {"trades": []}
    

@app.get("/market")
def get_market():
    """Fetch prices for all market overview stocks at once."""
    market_lists = {
        "Indices": ["SPY", "QQQ", "DIA", "IWM", "VTI"],
        "Tech": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD"],
        "Finance": ["JPM", "BAC", "GS", "V", "MA"],
        "Energy": ["XOM", "CVX", "COP", "OXY"],
        "Health": ["JNJ", "PFE", "LLY", "UNH"],
        "Consumer": ["WMT", "HD", "MCD", "SBUX", "NKE"],
        "Crypto": ["COIN", "MSTR", "RIOT", "MARA"],
        "EV & Auto": ["TSLA", "RIVN", "NIO", "F", "GM"],
    }

    all_tickers = list({t for tickers in market_lists.values() for t in tickers})
    prices = {}

    def fetch(ticker):
        try:
            stock = yf.Ticker(ticker)
            fast = stock.fast_info
            price = fast.last_price
            prev_close = fast.previous_close
            change_pct = ((price - prev_close) / prev_close) * 100 if price and prev_close else 0
            return ticker, {
                "ticker": ticker,
                "price": round(price, 2) if price else None,
                "change_pct": round(change_pct, 2) if change_pct else 0,
                "direction": "up" if change_pct >= 0 else "down",
            }
        except Exception:
            return ticker, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch, t): t for t in all_tickers}
        for future in concurrent.futures.as_completed(futures, timeout=30):
            try:
                ticker, data = future.result(timeout=5)
                if data:
                    prices[ticker] = data
            except Exception:
                continue

    result = {}
    for category, tickers in market_lists.items():
        result[category] = [prices[t] for t in tickers if t in prices]

    return result


@app.get("/week52")
def week52():
    results_high = []
    results_low = []

    # Use focused list for speed
    WEEK52_LIST = [
        "SPY", "QQQ", "DIA", "IWM", "ARKK",
        "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD",
        "AVGO", "ORCL", "CRM", "ADBE", "PLTR", "SNOW", "NET", "CRWD",
        "JPM", "BAC", "GS", "V", "MA", "PYPL",
        "XOM", "CVX", "COP", "OXY",
        "JNJ", "PFE", "LLY", "UNH", "MRNA",
        "WMT", "HD", "MCD", "SBUX", "NKE", "AMZN",
        "COIN", "MSTR", "RIOT", "MARA",
        "TSLA", "RIVN", "NIO", "F", "GM",
        "BA", "LMT", "RTX", "HON",
        "SOFI", "HOOD", "UPST",
        "DIS", "NFLX", "SPOT",
        "GLD", "SLV", "USO", "TLT",
    ]
    WEEK52_LIST = list(dict.fromkeys(WEEK52_LIST))

    def check_ticker(ticker):
        try:
            stock = yf.Ticker(ticker)
            fast = stock.fast_info
            price = fast.last_price
            high_52 = fast.year_high
            low_52 = fast.year_low

            if not price or not high_52 or not low_52:
                return None

            pct_from_high = ((price - high_52) / high_52) * 100
            pct_from_low = ((price - low_52) / low_52) * 100

            return {
                "ticker": ticker,
                "price": round(price, 2),
                "high_52": round(high_52, 2),
                "low_52": round(low_52, 2),
                "pct_from_high": round(pct_from_high, 2),
                "pct_from_low": round(pct_from_low, 2),
            }
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_ticker, t): t for t in WEEK52_LIST}
        for future in concurrent.futures.as_completed(futures, timeout=60):
            try:
                result = future.result(timeout=5)
                if not result:
                    continue
                if result["pct_from_high"] >= -5:
                    results_high.append({**result, "signal": "near_high"})
                if result["pct_from_low"] <= 5:
                    results_low.append({**result, "signal": "near_low"})
            except Exception:
                continue

    results_high.sort(key=lambda x: x["pct_from_high"], reverse=True)
    results_low.sort(key=lambda x: x["pct_from_low"])

    return {
        "near_highs": results_high,
        "near_lows": results_low,
        "total_highs": len(results_high),
        "total_lows": len(results_low),
        "scanned": len(WEEK52_LIST),
    }
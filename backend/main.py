from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import requests
import concurrent.futures
from datetime import datetime, timedelta
import os
import resend

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
resend.api_key = RESEND_API_KEY

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

BROAD_LIST = [
    "SPY", "QQQ", "IWM", "DIA", "ARKK",
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD",
    "AVGO", "ORCL", "CRM", "ADBE", "PLTR", "SNOW", "NET", "CRWD",
    "DDOG", "ZS", "PANW", "MDB", "SHOP", "COIN", "MSTR",
    "JPM", "BAC", "GS", "MS", "WFC", "V", "MA", "PYPL", "SQ",
    "XOM", "CVX", "COP", "OXY", "SLB", "HAL",
    "JNJ", "PFE", "LLY", "UNH", "MRNA", "ABBV", "AMGN",
    "WMT", "HD", "MCD", "SBUX", "NKE", "TGT", "COST",
    "RIVN", "NIO", "F", "GM", "LCID",
    "BA", "LMT", "RTX", "HON", "GE", "CAT",
    "RIOT", "MARA", "HOOD", "SOFI", "UPST", "AFRM",
    "DIS", "NFLX", "SPOT", "RBLX",
    "BABA", "PDD", "JD", "BIDU",
    "GLD", "SLV", "USO", "TLT", "VXX",
]
BROAD_LIST = list(dict.fromkeys(BROAD_LIST))

NAMES = {
    "AAPL": "Apple Inc.", "MSFT": "Microsoft", "NVDA": "NVIDIA", "GOOGL": "Alphabet (Google)",
    "GOOG": "Alphabet (Google)", "AMZN": "Amazon", "META": "Meta Platforms", "TSLA": "Tesla",
    "AVGO": "Broadcom", "ORCL": "Oracle", "AMD": "Advanced Micro Devices", "INTC": "Intel",
    "QCOM": "Qualcomm", "TXN": "Texas Instruments", "MU": "Micron Technology",
    "AMAT": "Applied Materials", "LRCX": "Lam Research", "KLAC": "KLA Corporation",
    "MRVL": "Marvell Technology", "SMCI": "Super Micro Computer", "ARM": "Arm Holdings",
    "ASML": "ASML Holding", "CRM": "Salesforce", "ADBE": "Adobe", "NOW": "ServiceNow",
    "SNOW": "Snowflake", "PLTR": "Palantir", "DDOG": "Datadog", "NET": "Cloudflare",
    "CRWD": "CrowdStrike", "ZS": "Zscaler", "PANW": "Palo Alto Networks", "OKTA": "Okta",
    "MDB": "MongoDB", "GTLB": "GitLab", "HUBS": "HubSpot", "TEAM": "Atlassian",
    "WDAY": "Workday", "VEEV": "Veeva Systems", "SHOP": "Shopify", "TWLO": "Twilio",
    "ZM": "Zoom", "DOCU": "DocuSign", "BOX": "Box", "DOCN": "DigitalOcean",
    "JPM": "JPMorgan Chase", "BAC": "Bank of America", "GS": "Goldman Sachs",
    "MS": "Morgan Stanley", "WFC": "Wells Fargo", "C": "Citigroup", "BLK": "BlackRock",
    "SCHW": "Charles Schwab", "AXP": "American Express", "V": "Visa", "MA": "Mastercard",
    "PYPL": "PayPal", "SQ": "Block (Square)", "COF": "Capital One", "USB": "U.S. Bancorp",
    "PNC": "PNC Financial", "TFC": "Truist Financial", "BX": "Blackstone", "KKR": "KKR",
    "XOM": "ExxonMobil", "CVX": "Chevron", "COP": "ConocoPhillips", "SLB": "SLB",
    "OXY": "Occidental Petroleum", "EOG": "EOG Resources", "PXD": "Pioneer Natural Resources",
    "MPC": "Marathon Petroleum", "VLO": "Valero Energy", "PSX": "Phillips 66",
    "HAL": "Halliburton", "BKR": "Baker Hughes", "DVN": "Devon Energy", "APA": "APA Corp",
    "HES": "Hess Corporation", "JNJ": "Johnson & Johnson", "PFE": "Pfizer",
    "UNH": "UnitedHealth Group", "ABBV": "AbbVie", "MRK": "Merck", "LLY": "Eli Lilly",
    "BMY": "Bristol-Myers Squibb", "AMGN": "Amgen", "GILD": "Gilead Sciences",
    "BIIB": "Biogen", "REGN": "Regeneron", "VRTX": "Vertex Pharmaceuticals",
    "MRNA": "Moderna", "BNTX": "BioNTech", "ILMN": "Illumina", "DXCM": "DexCom",
    "ISRG": "Intuitive Surgical", "SYK": "Stryker", "MDT": "Medtronic", "ABT": "Abbott",
    "TMO": "Thermo Fisher", "DHR": "Danaher", "IDXX": "IDEXX Laboratories",
    "WMT": "Walmart", "HD": "Home Depot", "MCD": "McDonald's", "SBUX": "Starbucks",
    "NKE": "Nike", "TGT": "Target", "COST": "Costco", "LOW": "Lowe's", "TJX": "TJX Companies",
    "BABA": "Alibaba", "JD": "JD.com", "PDD": "PDD Holdings", "MELI": "MercadoLibre",
    "SE": "Sea Limited", "GRAB": "Grab", "DASH": "DoorDash", "UBER": "Uber",
    "LYFT": "Lyft", "ABNB": "Airbnb", "BKNG": "Booking Holdings", "EXPE": "Expedia",
    "MAR": "Marriott", "HLT": "Hilton", "DIS": "Disney", "NFLX": "Netflix",
    "PARA": "Paramount", "WBD": "Warner Bros. Discovery", "CMCSA": "Comcast",
    "T": "AT&T", "VZ": "Verizon", "TMUS": "T-Mobile", "CHTR": "Charter Communications",
    "SPOT": "Spotify", "RBLX": "Roblox", "EA": "Electronic Arts", "TTWO": "Take-Two Interactive",
    "F": "Ford Motor", "GM": "General Motors", "RIVN": "Rivian", "LCID": "Lucid Motors",
    "NIO": "NIO Inc.", "LI": "Li Auto", "XPEV": "XPeng", "AMT": "American Tower",
    "PLD": "Prologis", "CCI": "Crown Castle", "EQIX": "Equinix", "SPG": "Simon Property",
    "O": "Realty Income", "VICI": "VICI Properties", "AVB": "AvalonBay", "EQR": "Equity Residential",
    "BA": "Boeing", "LMT": "Lockheed Martin", "RTX": "RTX Corporation", "NOC": "Northrop Grumman",
    "GD": "General Dynamics", "HON": "Honeywell", "GE": "GE Aerospace", "CAT": "Caterpillar",
    "DE": "Deere & Company", "MMM": "3M", "EMR": "Emerson Electric", "ETN": "Eaton",
    "ITW": "Illinois Tool Works", "PH": "Parker Hannifin", "ROK": "Rockwell Automation",
    "COIN": "Coinbase", "MSTR": "MicroStrategy", "RIOT": "Riot Platforms", "MARA": "Marathon Digital",
    "CLSK": "CleanSpark", "CIFR": "Cipher Mining", "HUT": "Hut 8 Mining",
    "SOFI": "SoFi Technologies", "HOOD": "Robinhood", "UPST": "Upstart", "AFRM": "Affirm",
    "LC": "LendingClub", "PLUG": "Plug Power", "FCEL": "FuelCell Energy", "BLNK": "Blink Charging",
    "CHPT": "ChargePoint", "ENVX": "Enovix", "LAZR": "Luminar Technologies",
    "JOBY": "Joby Aviation", "ACHR": "Archer Aviation",
    "SPY": "S&P 500 ETF", "QQQ": "Nasdaq 100 ETF", "IWM": "Russell 2000 ETF",
    "DIA": "Dow Jones ETF", "VTI": "Vanguard Total Market ETF", "VOO": "Vanguard S&P 500 ETF",
    "ARKK": "ARK Innovation ETF", "ARKW": "ARK Next Gen ETF", "ARKG": "ARK Genomics ETF",
    "XLF": "Financial Select ETF", "XLK": "Technology Select ETF", "XLE": "Energy Select ETF",
    "XLV": "Health Care Select ETF", "XLI": "Industrial Select ETF", "XLB": "Materials Select ETF",
    "XLU": "Utilities Select ETF", "XLP": "Consumer Staples ETF", "XLY": "Consumer Discretionary ETF",
    "GLD": "Gold ETF", "SLV": "Silver ETF", "USO": "Oil ETF", "TLT": "20+ Year Treasury ETF",
    "HYG": "High Yield Bond ETF", "LQD": "Investment Grade Bond ETF", "EEM": "Emerging Markets ETF",
    "VXX": "Volatility ETF", "SQQQ": "ProShares UltraPro Short QQQ", "TQQQ": "ProShares UltraPro QQQ",
    "SPXU": "ProShares UltraPro Short S&P500", "UVXY": "ProShares Ultra VIX",
    "BITI": "ProShares Short Bitcoin ETF", "BITO": "ProShares Bitcoin ETF",
    "BIDU": "Baidu", "FANG": "Diamondback Energy", "A": "Agilent Technologies",
}


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
            name = NAMES.get(ticker, ticker)
            try:
                info = stock.info or {}
                name = info.get("longName") or info.get("shortName") or name
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
                "name": NAMES.get(ticker, ticker),
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
                "name": NAMES.get(ticker, ticker),
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
        period_map = {
            "1mo": "1mo", "3mo": "3mo", "6mo": "6mo",
            "1y": "1y", "2y": "2y", "5y": "5y", "10y": "10y",
        }
        yf_period = period_map.get(period, "6mo")
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period=yf_period)
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data found")
        data = []
        for date, row in hist.iterrows():
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
                "name": NAMES.get(ticker, ticker),
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
    except Exception:
        return {"ticker": ticker.upper(), "trades": []}


@app.get("/insider-feed")
def insider_feed():
    try:
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
    except Exception:
        return {"trades": []}


@app.get("/week52")
def week52():
    results_high = []
    results_low = []

    WEEK52_LIST = [
        "SPY", "QQQ", "DIA", "IWM", "ARKK",
        "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD",
        "AVGO", "ORCL", "CRM", "ADBE", "PLTR", "SNOW", "NET", "CRWD",
        "JPM", "BAC", "GS", "V", "MA", "PYPL",
        "XOM", "CVX", "COP", "OXY",
        "JNJ", "PFE", "LLY", "UNH", "MRNA",
        "WMT", "HD", "MCD", "SBUX", "NKE",
        "COIN", "MSTR", "RIOT", "MARA",
        "RIVN", "NIO", "F", "GM",
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
                "name": NAMES.get(ticker, ticker),
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


@app.get("/market")
def get_market():
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
                "name": NAMES.get(ticker, ticker),
                "price": round(price, 2) if price else None,
                "change_pct": round(change_pct, 2) if change_pct else 0,
                "direction": "up" if change_pct >= 0 else "down",
            }
        except Exception:
            return ticker, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch, t): t for t in all_tickers}
        for future in concurrent.futures.as_completed(futures, timeout=60):
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


@app.get("/gainers-losers")
def gainers_losers():
    results = []

    def check_ticker(ticker):
        try:
            stock = yf.Ticker(ticker)
            fast = stock.fast_info
            price = fast.last_price
            prev_close = fast.previous_close
            if not price or not prev_close:
                return None
            change_pct = ((price - prev_close) / prev_close) * 100
            return {
                "ticker": ticker,
                "name": NAMES.get(ticker, ticker),
                "price": round(price, 2),
                "change_pct": round(change_pct, 2),
                "direction": "up" if change_pct > 0 else "down",
            }
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_ticker, t): t for t in BROAD_LIST}
        for future in concurrent.futures.as_completed(futures, timeout=90):
            try:
                result = future.result(timeout=5)
                if result:
                    results.append(result)
            except Exception:
                continue

    results.sort(key=lambda x: x["change_pct"], reverse=True)
    gainers = results[:10]
    losers = list(reversed(results[-10:]))

    return {
        "gainers": gainers,
        "losers": losers,
        "updated": datetime.now().isoformat(),
    }


@app.get("/gainers-losers/{period}")
def gainers_losers_period(period: str):
    period_map = {
        "1d": "2d",
        "1w": "5d",
        "1mo": "1mo",
        "3mo": "3mo",
        "1y": "1y",
    }
    yf_period = period_map.get(period, "5d")
    results = []

    def check_ticker(ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=yf_period)
            if hist.empty or len(hist) < 2:
                return None
            start_price = hist["Close"].iloc[0]
            end_price = hist["Close"].iloc[-1]
            change_pct = ((end_price - start_price) / start_price) * 100
            return {
                "ticker": ticker,
                "name": NAMES.get(ticker, ticker),
                "price": round(end_price, 2),
                "start_price": round(start_price, 2),
                "change_pct": round(change_pct, 2),
                "direction": "up" if change_pct > 0 else "down",
            }
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_ticker, t): t for t in BROAD_LIST}
        for future in concurrent.futures.as_completed(futures, timeout=90):
            try:
                result = future.result(timeout=5)
                if result:
                    results.append(result)
            except Exception:
                continue

    results.sort(key=lambda x: x["change_pct"], reverse=True)
    gainers = results[:10]
    losers = list(reversed(results[-10:]))

    return {
        "gainers": gainers,
        "losers": losers,
        "period": period,
        "updated": datetime.now().isoformat(),
    }


@app.get("/market-news")
def market_news():
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
        res = requests.get(url, timeout=10)
        data = res.json()
        articles = []
        for item in data[:20]:
            articles.append({
                "headline": item.get("headline", ""),
                "summary": item.get("summary", "")[:300],
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                "image": item.get("image", ""),
                "datetime": datetime.fromtimestamp(item.get("datetime", 0)).strftime("%b %d, %Y %I:%M %p"),
            })
        return {"articles": articles, "updated": datetime.now().isoformat()}
    except Exception:
        return {"articles": [], "updated": datetime.now().isoformat()}


@app.post("/send-alert-email")
def send_alert_email(data: dict):
    try:
        ticker = data.get("ticker", "")
        target_price = data.get("target_price", "")
        current_price = data.get("current_price", "")
        direction = data.get("direction", "")
        email = data.get("email", "")

        if not email or not ticker:
            return {"success": False, "error": "Missing email or ticker"}

        params = {
            "from": "Stock Tracker <onboarding@resend.dev>",
            "to": [email],
            "subject": f"🔔 {ticker} Price Alert Triggered!",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #f1f5f9; padding: 2rem; border-radius: 12px;">
                    <h1 style="color: #3b82f6;">📈 Stock Tracker Alert</h1>
                    <p style="font-size: 1.1rem;">Your price alert for <strong>{ticker}</strong> has been triggered!</p>
                    <div style="background: #1e293b; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
                        <p style="margin: 0.5rem 0;"><strong>Stock:</strong> {ticker}</p>
                        <p style="margin: 0.5rem 0;"><strong>Target Price:</strong> ${target_price}</p>
                        <p style="margin: 0.5rem 0;"><strong>Current Price:</strong> ${current_price}</p>
                        <p style="margin: 0.5rem 0;"><strong>Direction:</strong> Went {direction} your target</p>
                    </div>
                    <p style="color: #64748b; font-size: 0.85rem;">This alert has been removed from your active alerts.</p>
                    <a href="https://stock-tracker-smoky-kappa.vercel.app" style="display: inline-block; background: #3b82f6; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; margin-top: 1rem;">Open Stock Tracker</a>
                </div>
            """,
        }

        email_response = resend.Emails.send(params)
        return {"success": True, "id": email_response.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}
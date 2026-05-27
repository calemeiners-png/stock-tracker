# Stock Tracker API

Simple FastAPI service that returns basic stock info using yfinance.

Quick start:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Endpoints:

- `GET /` — health check
- `GET /stock/{ticker}` — stock info for `ticker` (e.g. AAPL)

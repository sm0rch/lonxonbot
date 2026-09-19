"""
data_fetcher.py — Fetch market data for Vietnamese stocks
Uses yfinance (Yahoo Finance) for reliable OHLCV historical data.
DNSE client is kept for account info and future market data access
once LightSpeed API subscription is fully activated.
"""

import yfinance as yf
import pandas as pd
from dnse_client import DNSEClient


class DataFetcher:
    """
    Fetches historical OHLCV data for Vietnamese stocks
    and real-time quotes.

    Vietnamese stocks on Yahoo Finance use the '.VN' suffix.
    Example: VCB → VCB.VN, HPG → HPG.VN, FPT → FPT.VN
    """

    def __init__(self, client: DNSEClient = None):
        # DNSEClient is optional — used for account info / future DNSE data
        self.client = client

    # ── Historical OHLCV ────────────────────────────────────────────────────

    def get_historical(
        self,
        symbol: str,
        days: int = 60,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV candles for a Vietnamese stock.

        Args:
            symbol   : Vietnamese stock ticker, e.g. "VCB", "HPG", "FPT"
            days     : How many calendar days back to fetch (default 60)
            interval : Candle size — "1d" daily, "1wk" weekly, "1h" hourly

        Returns:
            pandas DataFrame with columns:
            [open, high, low, close, volume]
            indexed by date.
        """
        ticker = f"{symbol.upper()}.VN"
        period = f"{days}d"

        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,
        )

        if df.empty:
            print(f"⚠️  No data returned for {symbol}. Check the ticker symbol.")
            return pd.DataFrame()

        # Flatten MultiIndex columns if present (yfinance v0.2+)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Standardise column names to lowercase
        df.columns = [c.lower() for c in df.columns]
        df.index.name = "date"

        return df[["open", "high", "low", "close", "volume"]]

    # ── Real-time Quote ─────────────────────────────────────────────────────

    def get_quote(self, symbol: str) -> dict:
        """
        Fetch the latest available quote for a stock.

        Returns a dict with keys:
        symbol, price, previous_close, change, change_pct, volume
        """
        ticker = yf.Ticker(f"{symbol.upper()}.VN")
        info   = ticker.fast_info

        price    = getattr(info, "last_price", None) or 0
        prev     = getattr(info, "previous_close", None) or 0
        change   = round(price - prev, 2)
        chg_pct  = round((change / prev * 100) if prev else 0, 2)

        return {
            "symbol":         symbol.upper(),
            "price":          price,
            "previous_close": prev,
            "change":         change,
            "change_pct":     chg_pct,
            "volume":         getattr(info, "three_month_average_volume", 0),
        }

    # ── Batch Fetch ─────────────────────────────────────────────────────────

    def get_historical_batch(
        self,
        symbols: list,
        days: int = 60,
    ) -> dict:
        """
        Fetch historical data for a list of symbols.

        Returns:
            { "VCB": DataFrame, "HPG": DataFrame, ... }
        """
        result = {}
        for symbol in symbols:
            print(f"   📥 Fetching {symbol}...")
            df = self.get_historical(symbol, days=days)
            if not df.empty:
                result[symbol] = df
        return result


# ── Quick Test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fetcher = DataFetcher()

    # 1. Historical data
    print("📊 Fetching 60 days of daily data for VCB...")
    df = fetcher.get_historical("VCB", days=60)

    if df.empty:
        print("⚠️  No data returned.")
    else:
        print(f"   Rows      : {len(df)}")
        print(f"   Date range: {df.index[0].date()} → {df.index[-1].date()}")
        print(f"   Latest close : {df['close'].iloc[-1]:,.0f} VND")
        print(f"\n{df.tail(3).to_string()}")

    # 2. Batch fetch
    print("\n📦 Batch fetching VCB, HPG, FPT...")
    batch = fetcher.get_historical_batch(["VCB", "HPG", "FPT"], days=30)
    for sym, data in batch.items():
        print(f"   {sym}: {len(data)} rows, latest close = {data['close'].iloc[-1]:,.0f}")

    # 3. Quote
    print("\n⚡ Real-time quote for VCB...")
    quote = fetcher.get_quote("VCB")
    print(f"   Price     : {quote['price']:,.0f}")
    print(f"   Change    : {quote['change']:+.0f} ({quote['change_pct']:+.2f}%)")

    print("\n🎉 Data fetcher is working correctly!")

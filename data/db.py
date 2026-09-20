"""
data/db.py — Lưu và đọc dữ liệu OHLCV từ SQLite
Dữ liệu được lưu local → không cần gọi API mỗi lần
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Đường dẫn file database
DB_PATH = Path(__file__).parent.parent / "data" / "market.db"
DB_PATH.parent.mkdir(exist_ok=True)


def _get_connection():
    """Tạo kết nối tới SQLite database."""
    return sqlite3.connect(DB_PATH)


def save(symbol: str, df: pd.DataFrame, table_type: str = "daily") -> None:
    """
    Lưu DataFrame OHLCV vào SQLite.

    Args:
        symbol:     Mã cổ phiếu, ví dụ "VCB"
        df:         DataFrame với cột [open, high, low, close, volume]
        table_type: "daily"        → nến ngày (backtest)
                    "intraday_5m"  → nến 5 phút (live)
                    "intraday_15m" → nến 15 phút
    """
    if df.empty:
        return

    df = df.copy()
    df.index = df.index.astype(str)
    df["symbol"] = symbol.upper()

    table_name = f"ohlcv_{symbol.upper()}_{table_type}"

    with _get_connection() as conn:
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists="replace",
            index=True,
            index_label="date",
        )


def load(symbol: str, days: int = 60, table_type: str = "daily") -> pd.DataFrame:
    """
    Đọc dữ liệu OHLCV từ SQLite.

    Args:
        symbol:     Mã cổ phiếu, ví dụ "VCB"
        days:       Số dòng muốn lấy
        table_type: "daily" / "intraday_5m" / "intraday_15m"

    Returns:
        DataFrame hoặc DataFrame rỗng nếu chưa có dữ liệu
    """
    table = f"ohlcv_{symbol.upper()}_{table_type}"

    with _get_connection() as conn:
        check = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone()

        if not check:
            return pd.DataFrame()

        df = pd.read_sql(
            f"SELECT * FROM {table} ORDER BY date DESC LIMIT {days}",
            conn,
            index_col="date",
            parse_dates=["date"],
        )

    df = df.sort_index()
    df = df.drop(columns=["symbol"], errors="ignore")
    return df


def get_all_symbols() -> list:
    """
    Lấy danh sách tất cả mã cổ phiếu đang có trong DB.

    Returns:
        ["VCB", "HPG", "FPT", ...]
    """
    with _get_connection() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ohlcv_%'"
        ).fetchall()

    return [t[0].replace("ohlcv_", "") for t in tables]

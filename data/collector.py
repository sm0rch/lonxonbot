"""
data/collector.py — Thu thập dữ liệu từ internet và lưu vào database
Hỗ trợ 2 loại dữ liệu:
  - Nến NGÀY (1d)  : Dùng cho backtest dài hạn
  - Nến 5 PHÚT (5m): Dùng cho bot chạy live trong phiên giao dịch
"""

from data_fetcher import DataFetcher
import data.db as db
from datetime import datetime
import pytz

# Khởi tạo fetcher (dùng yfinance)
fetcher = DataFetcher()

# Múi giờ Việt Nam
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

# ── Kiểm tra giờ giao dịch ──────────────────────────────────

def is_market_open() -> bool:
    """
    Kiểm tra thị trường có đang mở cửa không.
    HOSE/HNX: 9:15 – 11:30 và 13:00 – 14:45
    """
    now = datetime.now(VN_TZ)
    
    # Bỏ qua cuối tuần
    if now.weekday() >= 5:
        return False

    hhmm = now.hour * 100 + now.minute
    
    morning   = 915 <= hhmm <= 1130
    afternoon = 1300 <= hhmm <= 1445
    
    return morning or afternoon


# ── Nến NGÀY — Dùng cho Backtest ───────────────────────────

def fetch_daily(symbol: str, days: int = 90) -> bool:
    """
    Lấy nến ngày (1d) của 1 mã và lưu vào DB.
    Dùng để backtest và phân tích dài hạn.
    """
    try:
        df = fetcher.get_historical(symbol, days=days, interval="1d")
        if df.empty:
            print(f"  ⚠️  {symbol}: Không có dữ liệu ngày")
            return False

        db.save(symbol, df, table_type="daily")
        print(f"  ✅ {symbol}: {len(df)} ngày | {df.index[0].date()} → {df.index[-1].date()}")
        return True
    except Exception as e:
        print(f"  ❌ {symbol}: Lỗi — {e}")
        return False


def update_daily(watchlist: list, days: int = 90) -> None:
    """
    Cập nhật nến ngày cho toàn bộ watchlist.
    Thường chạy 1 lần/ngày vào đầu phiên hoặc sau khi đóng cửa.
    """
    print(f"\n📅 CẬP NHẬT NẾN NGÀY ({len(watchlist)} mã)")
    print("─" * 45)

    success = sum(fetch_daily(sym, days=days) for sym in watchlist)

    print("─" * 45)
    print(f"✅ Xong: {success}/{len(watchlist)} mã\n")


# ── Nến 5 PHÚT — Dùng cho Bot Chạy Live ───────────────────

def fetch_intraday(symbol: str, days: int = 5, interval: str = "5m") -> bool:
    """
    Lấy nến intraday (5m / 15m) của 1 mã và lưu vào DB.
    Dùng để bot phát tín hiệu MUA/BÁN trong phiên.

    Giới hạn yfinance:
      - interval="5m"  → Tối đa 60 ngày gần nhất
      - interval="15m" → Tối đa 60 ngày gần nhất
    """
    try:
        df = fetcher.get_historical(symbol, days=days, interval=interval)
        if df.empty:
            return False

        # Chuyển về giờ VN cho dễ debug
        if df.index.tz is not None:
            df.index = df.index.tz_convert(VN_TZ)
        else:
            df.index = df.index.tz_localize("UTC").tz_convert(VN_TZ)

        table_type = f"intraday_{interval}"   # ví dụ: "intraday_5m"
        db.save(symbol, df, table_type=table_type)
        return True
    except Exception as e:
        print(f"  ❌ {symbol} [{interval}]: Lỗi — {e}")
        return False


def update_intraday(watchlist: list, interval: str = "5m") -> None:
    """
    Cập nhật nến intraday cho toàn bộ watchlist.
    Engine sẽ gọi hàm này mỗi 5 phút trong giờ giao dịch.
    """
    if not is_market_open():
        print("⏰ Thị trường đang đóng cửa — bỏ qua cập nhật intraday.")
        return

    now_str = datetime.now(VN_TZ).strftime("%H:%M")
    print(f"\n⚡ CẬP NHẬT INTRADAY {interval.upper()} lúc {now_str} ({len(watchlist)} mã)")

    success = 0
    for sym in watchlist:
        if fetch_intraday(sym, days=5, interval=interval):
            success += 1

    print(f"   ✅ {success}/{len(watchlist)} mã cập nhật thành công")


# ── Hàm tiện ích cũ (giữ lại để không vỡ code cũ) ──────────

def fetch_ohlcv(symbol: str, days: int = 90) -> bool:
    """Alias của fetch_daily — giữ để tương thích với code cũ."""
    return fetch_daily(symbol, days=days)


def update_database(watchlist: list, days: int = 90) -> None:
    """Alias của update_daily — giữ để tương thích với code cũ."""
    update_daily(watchlist, days=days)


# ── Quick Test ──────────────────────────────────────────────
if __name__ == "__main__":
    WATCHLIST = ["VCB", "HPG", "FPT"]

    print("=" * 50)
    print("TEST 1 — Nến ngày (backtest)")
    update_daily(WATCHLIST, days=30)

    print("=" * 50)
    print("TEST 2 — Nến 5 phút (live trong phiên)")
    # Tạm thời bỏ qua kiểm tra giờ để test
    for sym in WATCHLIST:
        result = fetch_intraday(sym, days=3, interval="5m")
        print(f"  {'✅' if result else '❌'} {sym}")

    print()
    print("TEST 3 — Đọc nến 5 phút từ DB")
    df = db.load("VCB", days=50, table_type="intraday_5m")
    if not df.empty:
        print(f"  VCB: {len(df)} nến 5 phút")
        print(df.tail(3).to_string())
    else:
        print("  Chưa có dữ liệu intraday (có thể đang ngoài giờ giao dịch)")

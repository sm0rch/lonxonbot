"""
data/collector.py — Thu thập dữ liệu từ internet và lưu vào database
Sử dụng DataFetcher (yfinance) để lấy dữ liệu.
"""

from data_fetcher import DataFetcher
import data.db as db

# Khởi tạo fetcher (không cần client lúc này vì dùng yfinance)
fetcher = DataFetcher()

def fetch_ohlcv(symbol: str, days: int = 90) -> bool:
    """
    Lấy dữ liệu 1 mã và lưu vào DB.
    
    Args:
        symbol: Mã cổ phiếu
        days: Số ngày cần lấy
        
    Returns:
        True nếu thành công, False nếu thất bại
    """
    print(f"📥 Lấy dữ liệu {symbol}...")
    try:
        df = fetcher.get_historical(symbol, days=days)
        if df.empty:
            print(f"⚠️ Không có dữ liệu cho {symbol}")
            return False
            
        # Lưu vào DB
        db.save(symbol, df)
        print(f"✅ Đã lưu {symbol} ({len(df)} dòng)")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi lấy {symbol}: {e}")
        return False


def update_database(watchlist: list, days: int = 90) -> None:
    """
    Cập nhật dữ liệu cho toàn bộ watchlist.
    
    Args:
        watchlist: ["VCB", "HPG", "FPT", ...]
        days: Số ngày cần lấy
    """
    print(f"\n🔄 BẮT ĐẦU CẬP NHẬT DATABASE ({len(watchlist)} mã)")
    print("-" * 40)
    
    success_count = 0
    for symbol in watchlist:
        if fetch_ohlcv(symbol, days=days):
            success_count += 1
            
    print("-" * 40)
    print(f"🎉 Cập nhật xong: {success_count}/{len(watchlist)} mã thành công.\n")


# ── Quick Test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test cập nhật 1 vài mã
    TEST_WATCHLIST = ["VCB", "HPG", "FPT", "VNM", "MWG"]
    
    # 1. Thu thập và lưu
    update_database(TEST_WATCHLIST, days=60)
    
    # 2. Đọc thử từ DB ra xem có không
    print("🔍 Kiểm tra dữ liệu trong DB:")
    saved_symbols = db.get_all_symbols()
    print(f"   Các mã đang có trong DB: {', '.join(saved_symbols)}")
    
    if saved_symbols:
        test_sym = saved_symbols[0]
        df = db.load(test_sym, days=5)
        print(f"\n📊 5 ngày gần nhất của {test_sym}:")
        print(df.to_string())

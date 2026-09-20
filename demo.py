"""
demo.py — File demo cho cả nhóm xem (chạy trên Terminal)
Kết hợp Data Module và Mock Strategy.
"""

from data.collector import update_database
from data.db import load
from strategies.mock import generate_signal

# Danh sách mã muốn demo
WATCHLIST = ["VCB", "HPG", "FPT", "VNM", "MWG", "SSI", "STB", "TCB"]

def run_demo():
    print("=" * 60)
    print("🚀 FINTECH BOT — DEMO HỆ THỐNG BACKEND 🚀")
    print("=" * 60)
    
    # Bước 1: Cập nhật dữ liệu
    print("\n[1] Đang cập nhật dữ liệu OHLCV mới nhất từ thị trường...")
    update_database(WATCHLIST, days=60)
    
    # Bước 2: Quét chiến lược
    print("\n[2] Đang chạy chiến lược phân tích (Mock Strategy)...")
    print("-" * 60)
    print(f"{'MÃ':<6} | {'HÀNH ĐỘNG':<10} | {'GIÁ (VND)':<12} | {'ĐỘ TIN CẬY':<10}")
    print("-" * 60)
    
    signals_found = 0
    for symbol in WATCHLIST:
        # Lấy dữ liệu từ SQLite (rất nhanh)
        df_full = load(symbol, days=60)
        if df_full.empty:
            continue
            
        # Chạy giả lập cho 5 ngày gần nhất để chắc chắn có tín hiệu demo
        for i in range(5, 0, -1):
            if i == 1:
                df = df_full.copy()
                date_str = "Hôm nay"
            else:
                df = df_full.iloc[:-i+1].copy() # Cắt bỏ i-1 ngày cuối
                date_str = f"Cách đây {i-1} ngày"

            df.attrs["ticker"] = symbol
            
            # Chạy chiến lược
            signal = generate_signal(df, fundamentals={})
            
            if signal:
                signals_found += 1
                action = f"🟢 {signal.action}" if signal.action == "BUY" else f"🔴 {signal.action}"
                print(f"{symbol:<6} | {action:<10} | {signal.price:>10,.0f} | {signal.confidence:>9.0%} | {date_str}")
                print(f"       ↳ Lý do: {signal.reason}\n")
            
    print("-" * 60)
    if signals_found == 0:
        print("⚪ Không phát hiện tín hiệu nào hôm nay.")
    else:
        print(f"🎉 Tổng cộng: Phát hiện {signals_found} tín hiệu.")
        
    print("\n✅ Hệ thống Backend đã sẵn sàng!")
    print("👉 Chờ nhóm nghiên cứu giao file 'strategies/real.py'")
    print("👉 Chờ Coder B hoàn thiện Telegram Bot")
    print("=" * 60)

if __name__ == "__main__":
    run_demo()

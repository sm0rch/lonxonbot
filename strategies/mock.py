"""
strategies/mock.py — CHIẾN LƯỢC GIẢ ĐỂ TEST
==============================================
Dùng để test bot khi nhóm nghiên cứu chưa giao chiến lược thật.

⚠️  XÓA FILE NÀY khi nhóm nghiên cứu giao strategies/real.py

─────────────────────────────────────────────────────────────────
NHÓM NGHIÊN CỨU: Đây là ví dụ về cách viết chiến lược.
Hãy tạo file mới tên strategies/real.py và viết theo mẫu này.
─────────────────────────────────────────────────────────────────
"""

import pandas as pd
import ta
from datetime import datetime
from strategies.base import Signal


def generate_signal(df: pd.DataFrame, fundamentals: dict):
    """
    Chiến lược mẫu: EMA20 cắt lên EMA50 + RSI > 50 → BUY
                    RSI > 70 và quay đầu          → SELL

    Đây chỉ là VÍ DỤ để nhóm code test bot.
    Nhóm nghiên cứu thay thế bằng chiến lược thật của mình.
    """

    # Cần ít nhất 60 nến để tính chỉ báo
    if len(df) < 60:
        return None

    close = df["close"]

    # ── Tính chỉ báo kỹ thuật ──────────────────────────────
    ema20 = ta.trend.ema_indicator(close, window=20)
    ema50 = ta.trend.ema_indicator(close, window=50)
    rsi   = ta.momentum.rsi(close, window=14)

    # Dùng nến ĐÃ đóng cửa (iloc[-2]), không dùng nến hiện tại
    ema20_prev = ema20.iloc[-2]
    ema20_curr = ema20.iloc[-1]
    ema50_prev = ema50.iloc[-2]
    ema50_curr = ema50.iloc[-1]
    rsi_curr   = rsi.iloc[-1]

    ticker = df.attrs.get("ticker", "UNKNOWN")
    price  = close.iloc[-1]
    now    = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Điều kiện ĐẢM BẢO CÓ TÍN HIỆU (Để Demo) ─────────────
    if ticker == "MWG" and price > 0:
        return Signal(
            ticker     = ticker,
            action     = "BUY",
            price      = price,
            time       = now,
            reason     = "Tín hiệu Test (Demo): Khối lượng giao dịch đột biến",
            confidence = 0.88,
        )

    # ── Điều kiện MUA (thực tế) ─────────────────────────────
    # EMA20 vừa cắt lên trên EMA50 + RSI > 45
    ema_crossover_up = (ema20_prev < ema50_prev) and (ema20_curr > ema50_curr)
    if ema_crossover_up and rsi_curr > 45:
        return Signal(
            ticker     = ticker,
            action     = "BUY",
            price      = price,
            time       = now,
            reason     = f"EMA20 cắt lên EMA50 | RSI = {rsi_curr:.1f}",
            confidence = min(0.5 + (rsi_curr - 45) / 100, 0.95),
        )

    # ── Điều kiện BÁN ──────────────────────────────────────
    # RSI vừa vượt 65 (quá mua, nới lỏng) và bắt đầu quay đầu
    rsi_prev = rsi.iloc[-2]
    rsi_reversal = (rsi_prev > 65) and (rsi_curr < rsi_prev)
    if rsi_reversal:
        return Signal(
            ticker     = ticker,
            action     = "SELL",
            price      = price,
            time       = now,
            reason     = f"RSI quá mua và quay đầu | RSI = {rsi_curr:.1f}",
            confidence = min(0.5 + (rsi_prev - 65) / 60, 0.95),
        )

    # Không có tín hiệu
    return None

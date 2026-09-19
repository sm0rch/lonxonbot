"""
strategies/base.py — HỢP ĐỒNG KỸ THUẬT
========================================
File này định nghĩa cấu trúc dữ liệu và chữ ký hàm mà
NHÓM NGHIÊN CỨU phải tuân theo khi viết chiến lược.

⚠️  QUY TẮC BẮT BUỘC:
- KHÔNG được đổi tên class Signal
- KHÔNG được đổi tên hoặc kiểu tham số của generate_signal()
- CHỈ được thay đổi code BÊN TRONG hàm generate_signal()
"""

from dataclasses import dataclass
from typing import Optional
import pandas as pd


# ══════════════════════════════════════════════════════════
#  Signal — Kết quả trả về của mỗi tín hiệu
# ══════════════════════════════════════════════════════════

@dataclass
class Signal:
    """
    Đại diện cho một tín hiệu MUA hoặc BÁN.

    Ví dụ:
        Signal(
            ticker     = "VCB",
            action     = "BUY",
            price      = 59900.0,
            time       = "2026-09-19 14:30",
            reason     = "EMA20 cắt lên EMA50, RSI > 50",
            confidence = 0.85
        )
    """
    ticker:     str    # Mã cổ phiếu, ví dụ: "VCB", "HPG", "FPT"
    action:     str    # Chỉ được là "BUY" hoặc "SELL"
    price:      float  # Giá tại thời điểm phát tín hiệu (VND)
    time:       str    # Thời gian, định dạng "YYYY-MM-DD HH:MM"
    reason:     str    # Giải thích ngắn gọn tại sao BUY/SELL
    confidence: float  # Độ tin cậy từ 0.0 (thấp) đến 1.0 (cao)

    def __post_init__(self):
        """Kiểm tra dữ liệu hợp lệ khi tạo Signal."""
        if self.action not in ("BUY", "SELL"):
            raise ValueError(f"action phải là 'BUY' hoặc 'SELL', nhận được: '{self.action}'")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence phải từ 0.0 đến 1.0, nhận được: {self.confidence}")


# ══════════════════════════════════════════════════════════
#  generate_signal() — Hàm nhóm nghiên cứu phải implement
# ══════════════════════════════════════════════════════════

def generate_signal(df: pd.DataFrame, fundamentals: dict) -> Optional[Signal]:
    """
    Phân tích dữ liệu và trả về tín hiệu MUA/BÁN nếu có.

    ┌─────────────────────────────────────────────────────┐
    │  NHÓM NGHIÊN CỨU: Viết chiến lược của mình vào ĐÂY │
    └─────────────────────────────────────────────────────┘

    Tham số:
        df (pd.DataFrame): Bảng dữ liệu OHLCV đã chuẩn hóa.
            Cột: [open, high, low, close, volume]
            Index: date (datetime)
            Ví dụ:
                            open     high      low    close    volume
                date
                2026-09-17  59000  60000.0  58800.0  59600.0   5395900
                2026-09-18  60000  61000.0  59800.0  59900.0  10362600

        fundamentals (dict): Dữ liệu tài chính cơ bản của mã cổ phiếu.
            Các key thường dùng:
                "roe"       → ROE (Return on Equity), ví dụ: 0.18 = 18%
                "pe"        → P/E ratio, ví dụ: 12.5
                "pb"        → P/B ratio, ví dụ: 1.8
                "eps"       → EPS (VND), ví dụ: 5200
                "revenue_growth" → Tăng trưởng doanh thu, ví dụ: 0.15 = 15%
            Nếu không có dữ liệu cơ bản, dict này sẽ rỗng: {}

    Trả về:
        Signal  → nếu phát hiện tín hiệu MUA hoặc BÁN
        None    → nếu không có tín hiệu (giữ nguyên, không làm gì)

    ⚠️  QUAN TRỌNG — Tránh Look-ahead Bias:
        ĐÚNG  ✅: Dùng df['close'].iloc[-2]  (nến đã đóng cửa)
        SAI   ❌: Dùng df['close'].iloc[-1]  (nến hiện tại chưa đóng)
    """

    # ──────────────────────────────────────────────────────
    # NHÓM NGHIÊN CỨU VIẾT CODE TỪ ĐÂY XUỐNG
    # ──────────────────────────────────────────────────────

    # Hiện tại để trống — nhóm nghiên cứu sẽ điền vào
    # Xem file strategies/mock.py để hiểu ví dụ

    raise NotImplementedError(
        "Nhóm nghiên cứu chưa implement chiến lược.\n"
        "Hãy xem strategies/mock.py để hiểu cách viết,\n"
        "sau đó thay thế hàm này bằng chiến lược thật."
    )

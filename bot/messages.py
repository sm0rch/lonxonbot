"""
bot/messages.py — CHỨA CÁC TEMPLATE TIN NHẮN THEO SPEC
Coder B chỉ cần vào đây sửa chữ, không lo hỏng logic bot.
"""

from strategies.base import StockDataResult

# ── M0: /start ─────────────────────────────────────────────
WELCOME_MESSAGE = """
👋 <b>Chào mừng đến với FinBot</b>

Bot phát tín hiệu Mua/Bán cổ phiếu Việt Nam dựa trên
chiến lược kết hợp Phân tích cơ bản và Phân tích kỹ thuật.

<b>Bắt đầu nhanh:</b>
• Gõ mã cổ phiếu bất kỳ, ví dụ <code>HPG</code>
• /signals — tín hiệu hôm nay
• /market — trạng thái thị trường
• /subscribe — nhận thông báo tự động

⚠️ Thông tin chỉ mang tính tham khảo, không phải
khuyến nghị đầu tư. Người dùng tự chịu trách nhiệm
với quyết định của mình.
"""

# ── M3: TỔNG KẾT MÃ ────────────────────────────────────────
def build_m3_summary(data: StockDataResult) -> str:
    """Tạo tin nhắn M3 (Tổng kết)"""
    icon = "🟢" if data.price.change >= 0 else "🔴"
    sign = "+" if data.price.change > 0 else ""
    
    # Lấy thông tin tín hiệu (nếu có)
    action_str = f"{data.signal.action}" if data.signal else "Không có"
    
    return f"""
🏢 <b>{data.ticker} — {data.company_name}</b>
🏭 Ngành: {data.sector} · Sàn: {data.exchange}

━━━━━━━━━━━━━━━━━━━━
💵 <b>{data.price.current:,.2f}</b>  {icon} {sign}{data.price.change:,.2f} ({sign}{data.price.change_pct:.2f}%)
📊 KL: {data.price.volume:,.0f} · GT: {data.price.value:,.0f}
📉 Thấp/Cao: {data.price.low:,.2f} / {data.price.high:,.2f}
🔺 Trần: {data.price.ceiling:,.2f} · 🔻 Sàn: {data.price.floor:,.2f}
━━━━━━━━━━━━━━━━━━━━

<b>📍 Trạng thái hiện tại</b>
Tín hiệu: <b>{action_str}</b>
Xu hướng: {data.technical.trend}
Độ mạnh xu hướng (ADX): {data.technical.adx:.1f}

<b>⚡ Nhanh</b>
RSI14: {data.technical.rsi14:.1f}
EMA20/50: {data.technical.ema20:.2f} / {data.technical.ema50:.2f}

<i>Cập nhật {data.market_updated_at} · Nguồn: {data.data_source}</i>
"""

# ── M3.1: Phân tích kỹ thuật ───────────────────────────────
def build_m3_1_technical(data: StockDataResult) -> str:
    return f"""
📊 <b>PHÂN TÍCH KỸ THUẬT — {data.ticker}</b>

<b>Xu hướng</b>
EMA20:  {data.technical.ema20:.2f}
EMA50:  {data.technical.ema50:.2f}
EMA200: {data.technical.ema200:.2f}

<b>Động lượng</b>
RSI14: {data.technical.rsi14:.1f}
MACD:  {data.technical.macd:.2f}

<b>Khối lượng</b>
Tỷ lệ so với TB 20 phiên: {data.technical.volume_ratio_20:.2f}x

<i>Cập nhật {data.technical_updated_at}</i>
"""

# ── Các hàm phụ trợ thông báo lỗi (Mục 6) ──────────────────
def error_not_found(ticker: str, suggestion: str = None) -> str:
    msg = f"❓ Không tìm thấy mã <b>{ticker}</b>\nMã cổ phiếu Việt Nam gồm 3 ký tự chữ cái."
    if suggestion:
        msg += f"\n\nÝ bạn là: <b>{suggestion}</b>?"
    return msg

def error_market_closed(next_open: str) -> str:
    return f"🌙 <b>Thị trường đã đóng cửa</b>\n\nPhiên tiếp theo: {next_open}"

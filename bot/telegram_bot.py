"""
bot/telegram_bot.py — BỘ KHUNG (SKELETON) BOT TELEGRAM
Đã xử lý sẵn Inline Keyboard và CallbackQuery để Coder B đỡ cực.
"""

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters
)
from telegram.constants import ParseMode

from bot.messages import WELCOME_MESSAGE, build_m3_summary, build_m3_1_technical
from data_fetcher import DataFetcher
from strategies.base import StockDataResult, PriceData, TechnicalData, FundamentalData, SignalDetail, History90d

# ── HÀM GIẢ LẬP DỮ LIỆU ĐỂ TEST GIAO DIỆN ─────────────────
def get_mock_stock_data(ticker: str) -> StockDataResult:
    """Tạo dữ liệu giả khớp chuẩn Spec để test giao diện trước khi có Engine thật"""
    return StockDataResult(
        ticker=ticker.upper(), company_name="Công ty Test", exchange="HOSE", sector="Test",
        data_source="MOCK", is_stale=False,
        market_updated_at="14:00 20/09", technical_updated_at="14:00",
        fundamental_asof="Q2/2026", fundamental_published_at="20/07",
        price=PriceData(26.5, 0.6, 2.31, 25.9, 26.75, 25.85, 25.9, 27.75, 24.15, 18420, 488000),
        technical=TechnicalData(26.12, 25.94, 24.38, 58.3, 0.18, 0.12, 28.4, 0.82, 2.1, "UPTREND", "STRONG"),
        fundamental=FundamentalData("Q2", 12.4, 1.6, 2100, 17.2, 9.4, 18.6, 24.3, 0.68, 169000, 14.8, 1.8),
        levels={}, 
        signal=SignalDetail("BUY", "10:35", 8.2, 3, [], "Mock lý do", 29.8, 25.1, 2.3, 8.0),
        history_90d=History90d([], None, 0, 0, 0, 0, 0, 0)
    )

# ── CÁC HÀM XỬ LÝ LỆNH CHÍNH ──────────────────────────────

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start"""
    # Tạo bàn phím dưới tin nhắn
    keyboard = [
        [InlineKeyboardButton("🌐 Thị trường", callback_data="cmd:market"),
         InlineKeyboardButton("📖 Hướng dẫn", callback_data="cmd:help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        WELCOME_MESSAGE, 
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def handle_text_or_stock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Xử lý khi user gõ mã cổ phiếu (VD: 'HPG') 
    hoặc dùng lệnh /stock HPG
    """
    text = update.message.text.strip()
    
    # Nếu là lệnh /stock HPG -> lấy chữ HPG
    if text.startswith("/stock"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("Vui lòng nhập mã. VD: /stock HPG")
            return
        ticker = parts[1].upper()
    else:
        # Nếu gõ khơi khơi 'HPG'
        ticker = text.upper()
        if len(ticker) != 3: # Chỉ xử lý nếu đúng 3 ký tự
            return

    # TODO: Tích hợp logic tìm kiếm mã gần đúng (E01) ở đây
    
    # Sinh giao diện M3 (Tổng kết)
    data = get_mock_stock_data(ticker)
    msg_text = build_m3_summary(data)
    
    # Tạo Inline Keyboard 6 nút theo Spec
    keyboard = [
        [InlineKeyboardButton("📊 Kỹ thuật", callback_data=f"stock:{ticker}:ta"),
         InlineKeyboardButton("💰 Cơ bản", callback_data=f"stock:{ticker}:fa")],
        [InlineKeyboardButton("🎯 Hỗ trợ/KC", callback_data=f"stock:{ticker}:levels"),
         InlineKeyboardButton("📜 Lịch sử", callback_data=f"stock:{ticker}:history")],
        [InlineKeyboardButton("📈 Biểu đồ", callback_data=f"stock:{ticker}:chart"),
         InlineKeyboardButton("🔍 Chi tiết", callback_data=f"stock:{ticker}:detail")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(msg_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


# ── BẮT SỰ KIỆN KHI BẤM NÚT (INLINE KEYBOARD) ─────────────

async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Hàm cực kỳ quan trọng! Nó sẽ bắt mọi click chuột vào nút bấm.
    """
    query = update.callback_query
    await query.answer() # Báo cho Telegram biết đã nhận click
    
    # callback_data có dạng "stock:HPG:ta" hoặc "stock:HPG:summary"
    data_parts = query.data.split(":")
    
    if data_parts[0] == "stock":
        ticker = data_parts[1]
        screen = data_parts[2]
        
        mock_data = get_mock_stock_data(ticker)
        
        keyboard = [[InlineKeyboardButton("⬅️ Quay lại", callback_data=f"stock:{ticker}:summary")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if screen == "summary":
                # Quay về màn hình M3 gốc (6 nút)
                kb_summary = [
                    [InlineKeyboardButton("📊 Kỹ thuật", callback_data=f"stock:{ticker}:ta"),
                     InlineKeyboardButton("💰 Cơ bản", callback_data=f"stock:{ticker}:fa")],
                    [InlineKeyboardButton("🎯 Hỗ trợ/KC", callback_data=f"stock:{ticker}:levels"),
                     InlineKeyboardButton("📜 Lịch sử", callback_data=f"stock:{ticker}:history")],
                    [InlineKeyboardButton("📈 Biểu đồ", callback_data=f"stock:{ticker}:chart"),
                     InlineKeyboardButton("🔍 Chi tiết", callback_data=f"stock:{ticker}:detail")]
                ]
                await query.edit_message_text(
                    text=build_m3_summary(mock_data),
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(kb_summary)
                )
                
            elif screen == "ta": # Phân tích kỹ thuật (M3.1)
                await query.edit_message_text(
                    text=build_m3_1_technical(mock_data),
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup # Chỉ có nút quay lại
                )
                
            # TODO: Coder B code tiếp các màn hình khác (fa, levels, history...) ở đây
            else:
                await query.edit_message_text(
                    text=f"Màn hình '{screen}' đang được Coder B xây dựng...",
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            print(f"Lỗi khi edit message: {e}")
            # Telegram sẽ báo lỗi nếu text mới giống y hệt text cũ, ta có thể bỏ qua

# ── KHỞI ĐỘNG BOT ──────────────────────────────────────────

def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        print("❌ LỖI: Chưa có TELEGRAM_TOKEN trong môi trường!")
        return

    app = Application.builder().token(token).build()

    # 1. Bắt các lệnh / (commands)
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("stock", handle_text_or_stock_cmd))
    
    # 2. Bắt text gõ tự do (VD: gõ "HPG" cũng nhận)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_or_stock_cmd))
    
    # 3. Bắt sự kiện bấm nút (Inline Keyboard)
    app.add_handler(CallbackQueryHandler(button_click_handler))

    print("🤖 Bot đang chạy (Skeleton mode)...")
    app.run_polling()

if __name__ == "__main__":
    main()

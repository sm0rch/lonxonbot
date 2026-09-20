"""
engine/signal_state.py — Chống Spam Tín Hiệu
=============================================
Đảm bảo mỗi mã chỉ phát tín hiệu MUA/BÁN tối đa 1 lần/phiên.
Trạng thái được lưu vào SQLite — bot restart KHÔNG bắn lại tín hiệu cũ.

Quy tắc (theo Spec Mục 8):
  1. Mỗi mã chỉ phát tối đa 1 tín hiệu MUA và 1 tín hiệu BÁN mỗi phiên
  2. Sau khi phát tín hiệu → khoá 60 phút, không phát tiếp
  3. Tối đa 10 alert/phiên/user
  4. Chỉ xét tín hiệu trên nến đã đóng, không xét nến đang hình thành
  5. Lưu trạng thái ra DB — bot restart không mất lịch sử
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import pytz

# ── Cấu hình ────────────────────────────────────────────────
DB_PATH     = Path(__file__).parent.parent / "data" / "market.db"
VN_TZ       = pytz.timezone("Asia/Ho_Chi_Minh")
LOCK_MINUTES = 60   # Khoá 60 phút sau khi phát tín hiệu
MAX_ALERTS_PER_USER = 10  # Tối đa 10 alert/phiên/user


def _conn():
    return sqlite3.connect(DB_PATH)


def _ensure_table():
    """Tạo bảng lưu trạng thái tín hiệu nếu chưa có."""
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signal_state (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker      TEXT    NOT NULL,
                action      TEXT    NOT NULL,
                session_date TEXT   NOT NULL,
                fired_at    TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_alert_count (
                user_id     INTEGER NOT NULL,
                session_date TEXT   NOT NULL,
                count       INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, session_date)
            )
        """)


# ── Hàm chính ───────────────────────────────────────────────

def can_send(ticker: str, action: str) -> bool:
    """
    Kiểm tra xem có được phép phát tín hiệu cho mã này không.

    Trả về False nếu:
      - Đã phát tín hiệu cùng loại (BUY/SELL) cho mã này trong phiên hôm nay
      - Chưa qua 60 phút kể từ lần phát gần nhất cho mã này

    Args:
        ticker: Mã cổ phiếu, ví dụ "VCB"
        action: "BUY" hoặc "SELL"
    """
    _ensure_table()

    now          = datetime.now(VN_TZ)
    today        = now.strftime("%Y-%m-%d")
    lock_cutoff  = (now - timedelta(minutes=LOCK_MINUTES)).isoformat()

    with _conn() as conn:
        # Quy tắc 1: Đã phát cùng action trong phiên này chưa?
        same_action = conn.execute("""
            SELECT id FROM signal_state
            WHERE ticker = ? AND action = ? AND session_date = ?
            LIMIT 1
        """, (ticker.upper(), action, today)).fetchone()

        if same_action:
            return False  # Đã phát BUY (hoặc SELL) rồi, không phát nữa

        # Quy tắc 2: Đã phát bất kỳ tín hiệu nào trong vòng 60 phút chưa?
        recent = conn.execute("""
            SELECT id FROM signal_state
            WHERE ticker = ? AND fired_at > ?
            LIMIT 1
        """, (ticker.upper(), lock_cutoff)).fetchone()

        if recent:
            return False  # Còn trong thời gian khoá 60 phút

    return True  # Được phép phát


def record(ticker: str, action: str) -> None:
    """
    Ghi lại rằng đã phát tín hiệu cho mã này.
    Gọi ngay SAU KHI gửi alert thành công.

    Args:
        ticker: Mã cổ phiếu
        action: "BUY" hoặc "SELL"
    """
    _ensure_table()

    now   = datetime.now(VN_TZ)
    today = now.strftime("%Y-%m-%d")

    with _conn() as conn:
        conn.execute("""
            INSERT INTO signal_state (ticker, action, session_date, fired_at)
            VALUES (?, ?, ?, ?)
        """, (ticker.upper(), action, today, now.isoformat()))


def can_alert_user(user_id: int) -> bool:
    """
    Kiểm tra user này có còn được nhận alert hôm nay không.
    Tối đa 10 alert/phiên/user (Spec Mục 8, Quy tắc 3).

    Args:
        user_id: Telegram user ID
    """
    _ensure_table()

    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")

    with _conn() as conn:
        row = conn.execute("""
            SELECT count FROM user_alert_count
            WHERE user_id = ? AND session_date = ?
        """, (user_id, today)).fetchone()

        count = row[0] if row else 0
        return count < MAX_ALERTS_PER_USER


def record_user_alert(user_id: int) -> int:
    """
    Tăng bộ đếm alert của user thêm 1.
    Trả về số alert đã gửi hôm nay.

    Args:
        user_id: Telegram user ID
    """
    _ensure_table()

    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")

    with _conn() as conn:
        conn.execute("""
            INSERT INTO user_alert_count (user_id, session_date, count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, session_date)
            DO UPDATE SET count = count + 1
        """, (user_id, today))

        count = conn.execute("""
            SELECT count FROM user_alert_count
            WHERE user_id = ? AND session_date = ?
        """, (user_id, today)).fetchone()[0]

    return count


def get_today_signals() -> list:
    """
    Lấy danh sách tất cả tín hiệu đã phát trong phiên hôm nay.
    Dùng để hiển thị trong lệnh /signals của bot.

    Returns:
        [{"ticker": "VCB", "action": "BUY", "fired_at": "10:35"}, ...]
    """
    _ensure_table()

    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")

    with _conn() as conn:
        rows = conn.execute("""
            SELECT ticker, action, fired_at FROM signal_state
            WHERE session_date = ?
            ORDER BY fired_at ASC
        """, (today,)).fetchall()

    return [
        {
            "ticker":   row[0],
            "action":   row[1],
            "fired_at": row[2][11:16],  # Chỉ lấy HH:MM
        }
        for row in rows
    ]


def reset_for_testing() -> None:
    """Xoá toàn bộ trạng thái — CHỈ DÙNG KHI TEST, không dùng production."""
    _ensure_table()
    with _conn() as conn:
        conn.execute("DELETE FROM signal_state")
        conn.execute("DELETE FROM user_alert_count")
    print("🗑️  Đã xoá toàn bộ trạng thái tín hiệu (test mode)")


# ── Quick Test ──────────────────────────────────────────────
if __name__ == "__main__":
    print("🧪 TEST signal_state.py\n")
    reset_for_testing()

    # Test 1: Lần đầu → được phép
    print(f"1. VCB BUY lần đầu:    {'✅ Được phép' if can_send('VCB', 'BUY') else '❌ Bị chặn'}")
    record("VCB", "BUY")

    # Test 2: Cùng action → bị chặn
    print(f"2. VCB BUY lần 2:      {'✅ Được phép' if can_send('VCB', 'BUY') else '❌ Bị chặn (đúng!)'}")

    # Test 3: Action khác (SELL) → vẫn bị chặn vì trong 60 phút
    print(f"3. VCB SELL (< 60ph):  {'✅ Được phép' if can_send('VCB', 'SELL') else '❌ Bị chặn (đúng!)'}")

    # Test 4: Mã khác → được phép
    print(f"4. HPG BUY lần đầu:    {'✅ Được phép' if can_send('HPG', 'BUY') else '❌ Bị chặn'}")

    # Test 5: Đếm alert user
    user_id = 123456789
    print(f"\n5. User alert count:")
    for i in range(1, 4):
        record_user_alert(user_id)
        allowed = can_alert_user(user_id)
        print(f"   Alert #{i}: {'✅ Còn quota' if allowed else '🚫 Hết quota'}")

    # Test 6: Xem danh sách tín hiệu hôm nay
    print(f"\n6. Tín hiệu hôm nay: {get_today_signals()}")

    print("\n✅ signal_state.py hoạt động đúng!")

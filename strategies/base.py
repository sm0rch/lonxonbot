"""
strategies/base.py — HỢP ĐỒNG DỮ LIỆU (Theo Spec v1.1 Mục 9)
===========================================================
Định nghĩa cấu trúc dữ liệu mà hàm generate_signal() trả về.
Nhóm Nghiên cứu phải tuân thủ nghiêm ngặt cấu trúc này.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import pandas as pd


@dataclass
class PriceData:
    current: float; change: float; change_pct: float
    open: float; high: float; low: float
    ref: float; ceiling: float; floor: float
    volume: int; value: int

@dataclass
class TechnicalData:
    ema20: float; ema50: float; ema200: float
    rsi14: float; macd: float; macd_signal: float
    adx: float; atr14: float
    volume_ratio_20: float
    trend: str             # UPTREND | DOWNTREND | SIDEWAYS
    trend_strength: str    # WEAK | MODERATE | STRONG

@dataclass
class FundamentalData:
    quarter: str           # Ví dụ: "Q2/2026"
    pe: float; pb: float; eps: float
    roe: float; roa: float
    revenue_growth_yoy: float; profit_growth_yoy: float
    debt_to_equity: float
    market_cap: int
    sector_pe: float; sector_pb: float

@dataclass
class PriceLevel:
    price: float
    label: str

@dataclass
class SignalDetail:
    action: str            # BUY | SELL | HOLD | WATCH
    triggered_at: str      # ISO format
    score: float           # Thang điểm (ví dụ 8.2)
    rank: int              # Hạng trong rổ
    conditions_passed: List[str]
    explanation: str       # Đoạn văn xuôi do nhóm NC build
    target: float
    stoploss: float
    rr_ratio: float
    model_weight_pct: float

@dataclass
class TradeRecord:
    buy_date: str; buy_price: float
    sell_date: str; sell_price: float
    return_pct: float; holding_days: int

@dataclass
class OpenTrade:
    buy_date: str; buy_price: float

@dataclass
class History90d:
    closed_trades: List[TradeRecord]
    open_trade: Optional[OpenTrade]
    buy_count: int; sell_count: int
    win_rate: float; avg_return: float
    cumulative_return: float; avg_holding_days: int

@dataclass
class StockDataResult:
    """Object tổng hợp cuối cùng trả về cho Bot (Luồng B) hoặc Engine (Luồng A)"""
    ticker: str
    company_name: str
    exchange: str          # HOSE | HNX | UPCOM
    sector: str
    data_source: str
    is_stale: bool
    
    market_updated_at: str
    technical_updated_at: str
    fundamental_asof: str
    fundamental_published_at: str
    
    price: PriceData
    technical: TechnicalData
    fundamental: FundamentalData
    levels: Dict[str, List[PriceLevel]]  # {"resistance": [...], "support": [...]}
    signal: SignalDetail
    history_90d: History90d


# ══════════════════════════════════════════════════════════
# Hàm xử lý cấp Thị Trường (Market Context)
# ══════════════════════════════════════════════════════════

@dataclass
class SectorChange:
    name: str; change_pct: float

@dataclass
class MarketContext:
    vnindex: Dict[str, float]  # {"value": 1284.56, "change": 8.42, "change_pct": 0.66}
    liquidity_value: int
    breadth: Dict[str, int]    # {"advancing": 312, "declining": 145, "unchanged": 88}
    money_flow: str            # INFLOW | OUTFLOW | NEUTRAL
    foreign_net_value: int     # Dương = mua ròng, Âm = bán ròng
    leading_sectors: List[SectorChange]
    lagging_sectors: List[SectorChange]
    market_updated_at: str


# ══════════════════════════════════════════════════════════
# Giao diện cho Nhóm Nghiên Cứu
# ══════════════════════════════════════════════════════════

def analyze_stock(ticker: str, df_ohlcv: pd.DataFrame, fundamentals: dict) -> StockDataResult:
    """
    Hàm phân tích 1 mã cổ phiếu, trả về đầy đủ data theo format Spec Mục 9.
    Nhóm NC viết logic bên trong hàm này.
    """
    raise NotImplementedError("Nhóm NC cần implement hàm analyze_stock")

def analyze_market(market_data: dict) -> MarketContext:
    """
    Hàm phân tích trạng thái toàn thị trường, gọi 1 lần mỗi vòng quét.
    """
    raise NotImplementedError("Nhóm NC cần implement hàm analyze_market")

"""
Japanese Stock Backtest
Version : 1.0.0

config.py

バックテスト共通設定
"""

from pathlib import Path


class Config:
    """バックテスト共通設定"""

    # ==========================================================
    # Project
    # ==========================================================
    PROJECT_NAME = "JapaneseStockBacktest"
    VERSION = "1.0.0"

    # ==========================================================
    # Initial Portfolio
    # ==========================================================
    INITIAL_CASH = 5_000_000          # 初期資金（円）
    INITIAL_SHARES = 100              # 初回購入株数

    # ==========================================================
    # Trading Rule
    # ==========================================================
    MAX_BUY_COUNT = 10                # 最大ナンピン回数
    AVERAGING_RATE = 0.06             # ナンピン率（6%）
    PROFIT_TARGET = 0.03              # 利益確定率（3%）

    # ==========================================================
    # CSV
    # ==========================================================
    CSV_FILE = Path("sample_data") / "7201.csv"

    # 使用列
    DATE_COLUMN = "日付"
    OPEN_COLUMN = "始値"
    HIGH_COLUMN = "高値"
    LOW_COLUMN = "安値"
    CLOSE_COLUMN = "終値"

    # 読み飛ばす列（存在していても使用しない）
    IGNORE_COLUMNS = [
        "出来高",
        "変化率％"
    ]

    REQUIRED_COLUMNS = [
        DATE_COLUMN,
        OPEN_COLUMN,
        HIGH_COLUMN,
        LOW_COLUMN,
        CLOSE_COLUMN,
    ]

    # ==========================================================
    # Output
    # ==========================================================
    OUTPUT_DIR = Path("output")

    TRADE_HISTORY_FILE = OUTPUT_DIR / "trade_history.csv"
    STATISTICS_FILE = OUTPUT_DIR / "statistics.csv"
    EXCEL_FILE = OUTPUT_DIR / "BacktestResult.xlsx"
    CHART_FILE = OUTPUT_DIR / "equity_curve.png"

    # ==========================================================
    # Display
    # ==========================================================
    PRICE_DIGITS = 2

    # ==========================================================
    # Debug
    # ==========================================================
    DEBUG = False

    # ==========================================================
    # Utility
    # ==========================================================
    @classmethod
    def create_output_directory(cls):
        """
        outputフォルダを作成する
        """
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

"""
Japanese Stock Backtest
Version 1.0

config.py
システム全体で使用する設定ファイル
"""

from dataclasses import dataclass


@dataclass
class Config:

    # ============================
    # 資金設定
    # ============================

    INITIAL_CASH = 5_000_000

    INITIAL_SHARES = 100

    MAX_BUY_COUNT = 10


    # ============================
    # 売買ルール
    # ============================

    AVERAGING_RATE = 0.06

    PROFIT_TARGET = 0.03


    # ============================
    # ファイル
    # ============================

    CSV_FILE = "sample_data/7201.csv"

    OUTPUT_DIR = "output"


    # ============================
    # 手数料
    # ============================

    COMMISSION = 0.0


    # ============================
    # デバッグ
    # ============================

    DEBUG = True

"""
Japanese Stock Backtest
Version 1.0

trade_engine.py
バックテスト実行エンジン
"""

from pathlib import Path

import pandas as pd

from config import Config


class TradeEngine:

    def __init__(self, portfolio):

        self.portfolio = portfolio

        self.config = Config()

        self.df = None

    def load_csv(self):

        csv_path = Path(self.config.CSV_FILE)

        if not csv_path.exists():
            raise FileNotFoundError(
                f"CSVが見つかりません：{csv_path}"
            )

        self.df = pd.read_csv(csv_path)

        # 日付を datetime に変換
        self.df["日付"] = pd.to_datetime(self.df["日付"])

        # 日付順に並べる
        self.df = self.df.sort_values("日付")

        self.df.reset_index(drop=True, inplace=True)

        return self.df

"""
Japanese Stock Backtest
Version 1.0.1

trade_engine.py
バックテスト実行エンジン
"""

from pathlib import Path
import pandas as pd

from config import Config


class TradeEngine:

    REQUIRED_COLUMNS = [
        "日付",
        "終値",
        "始値",
        "高値",
        "安値",
    ]

    def __init__(self, portfolio):

        self.config = Config()
        self.portfolio = portfolio
        self.df = None

    def load_csv(self):

        csv_path = Path(self.config.CSV_FILE)

        if not csv_path.exists():
            raise FileNotFoundError(
                f"CSVファイルが見つかりません：{csv_path}"
            )

        df = pd.read_csv(csv_path)

        # 必須列チェック
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                raise ValueError(f"必須列がありません：{col}")

        # 日付変換
        df["日付"] = pd.to_datetime(df["日付"])

        # 数値変換
        numeric_columns = [
            "始値",
            "高値",
            "安値",
            "終値",
        ]

        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 欠損値除去
        df = df.dropna(subset=numeric_columns)

        # 日付順
        df = df.sort_values("日付")

        df.reset_index(drop=True, inplace=True)

        self.df = df

        if self.config.DEBUG:
            print("CSV読込完了")
            print(f"データ件数 : {len(df)}")
            print(df.head())

        return df
  
def run(self):
    """
    バックテスト実行
    """

    if self.df is None:
        self.load_csv()

    for _, row in self.df.iterrows():

        date = row["日付"].strftime("%Y-%m-%d")
        close = float(row["終値"])

        # 初回購入
        if not self.portfolio.has_stock():

            success = self.portfolio.buy(date, close)

            if self.config.DEBUG:
                if success:
                    print(f"{date} 初回購入 {close:.1f}円")
                else:
                    print(f"{date} 購入失敗")

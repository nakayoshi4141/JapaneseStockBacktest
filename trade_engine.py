"""
Japanese Stock Backtest
Version : 1.0.0

trade_engine.py

バックテストエンジン
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any

import pandas as pd

from config import Config
from portfolio import Portfolio


@dataclass
class TradeRecord:
    """
    売買履歴
    """

    date: str
    action: str
    price: float
    shares: int
    cash: float
    total_shares: int
    average_price: float
    realized_profit: float


class TradeEngine:
    """
    バックテストエンジン
    """

    def __init__(self):

        self.portfolio = Portfolio(
            initial_cash=Config.INITIAL_CASH
        )

        self.trade_history: List[TradeRecord] = []

        self.asset_history: List[Dict[str, Any]] = []

        self.data: pd.DataFrame | None = None

    # =====================================================
    # CSV
    # =====================================================

    def load_csv(self) -> None:
        """
        CSV読込
        """

        self.data = pd.read_csv(
            Config.CSV_FILE,
            encoding="utf-8-sig"
        )

        missing = [
            col
            for col in Config.REQUIRED_COLUMNS
            if col not in self.data.columns
        ]

        if missing:
            raise ValueError(
                f"CSVに必要列がありません : {missing}"
            )

        self.data = self.data[
            Config.REQUIRED_COLUMNS
        ].copy()

        self.data[Config.DATE_COLUMN] = pd.to_datetime(
            self.data[Config.DATE_COLUMN]
        )

        self.data.sort_values(
            Config.DATE_COLUMN,
            inplace=True
        )

        self.data.reset_index(
            drop=True,
            inplace=True
        )

    # =====================================================
    # History
    # =====================================================

    def add_trade_history(
        self,
        date,
        action,
        price,
        shares,
        realized_profit=0.0
    ) -> None:
        """
        売買履歴追加
        """

        self.trade_history.append(

            TradeRecord(
                date=str(date.date()),
                action=action,
                price=price,
                shares=shares,
                cash=self.portfolio.cash,
                total_shares=self.portfolio.total_shares,
                average_price=self.portfolio.average_price,
                realized_profit=realized_profit
            )

        )

    def add_asset_history(
        self,
        date,
        close_price
    ) -> None:
        """
        資産推移追加
        """

        self.asset_history.append(

            {
                "Date": str(date.date()),
                "Cash": self.portfolio.cash,
                "MarketValue":
                    self.portfolio.market_value(
                        close_price
                    ),
                "TotalAssets":
                    self.portfolio.total_assets(
                        close_price
                    )
            }

        )
    # =====================================================
    # Trading
    # =====================================================

    def execute_buy(
        self,
        date,
        price: float,
        is_average_down: bool = False
    ) -> None:
        """
        買付
        """

        shares = Config.INITIAL_SHARES

        if not self.portfolio.can_buy(price, shares):
            return

        self.portfolio.buy(price, shares)

        self.add_trade_history(
            date=date,
            action="BUY" if not is_average_down else "AVERAGE_DOWN",
            price=price,
            shares=shares
        )

    def execute_sell(
        self,
        date,
        price: float
    ) -> None:
        """
        全売却
        """

        shares = self.portfolio.total_shares

        realized_profit = self.portfolio.sell_all(price)

        self.add_trade_history(
            date=date,
            action="SELL",
            price=price,
            shares=shares,
            realized_profit=realized_profit
        )

    # =====================================================
    # Daily Process
    # =====================================================

    def process_one_day(
        self,
        row
    ) -> None:
        """
        1営業日の処理
        """

        date = row[Config.DATE_COLUMN]
        close_price = float(row[Config.CLOSE_COLUMN])

        # -----------------------------
        # ポジション無し
        # -----------------------------
        if not self.portfolio.has_position:

            self.execute_buy(
                date=date,
                price=close_price,
                is_average_down=False
            )

            self.add_asset_history(
                date,
                close_price
            )

            return

        # -----------------------------
        # 利益確定
        # -----------------------------
        if self.portfolio.should_take_profit(
            close_price,
            Config.PROFIT_TARGET
        ):

            self.execute_sell(
                date=date,
                price=close_price
            )

            self.add_asset_history(
                date,
                close_price
            )

            return

        # -----------------------------
        # ナンピン
        # -----------------------------
        averaging_count = (
            self.portfolio.buy_count - 1
        )

        if (
            averaging_count < Config.MAX_BUY_COUNT
            and
            self.portfolio.should_average_down(
                close_price,
                Config.AVERAGING_RATE
            )
        ):

            self.execute_buy(
                date=date,
                price=close_price,
                is_average_down=True
            )

        # -----------------------------
        # 資産記録
        # -----------------------------
        self.add_asset_history(
            date,
            close_price
        ) 
    # =====================================================
    # Backtest Run
    # =====================================================

    def run(self) -> None:
        """
        バックテスト実行
        """

        if self.data is None:
            raise RuntimeError(
                "CSVデータが読み込まれていません"
            )

        for _, row in self.data.iterrows():

            self.process_one_day(row)

    # =====================================================
    # Result Data
    # =====================================================

    def get_trade_history_df(
        self
    ) -> pd.DataFrame:
        """
        売買履歴DataFrame取得
        """

        if not self.trade_history:
            return pd.DataFrame()

        return pd.DataFrame(
            [
                {
                    "日付": record.date,
                    "取引": record.action,
                    "価格": record.price,
                    "株数": record.shares,
                    "現金": record.cash,
                    "保有株数": record.total_shares,
                    "平均取得単価":
                        record.average_price,
                    "実現損益":
                        record.realized_profit
                }
                for record in self.trade_history
            ]
        )

    def get_asset_history_df(
        self
    ) -> pd.DataFrame:
        """
        資産推移DataFrame取得
        """

        return pd.DataFrame(
            self.asset_history
        )

    # =====================================================
    # Summary
    # =====================================================

    def get_final_assets(
        self
    ) -> float:
        """
        最終資産取得
        """

        if not self.asset_history:
            return Config.INITIAL_CASH

        return (
            self.asset_history[-1]
            ["TotalAssets"]
        )

    def get_position_status(
        self
    ) -> dict:
        """
        現在ポジション情報取得
        """

        return (
            self.portfolio
            .position_summary()
        )
            # =====================================================
    # Validation
    # =====================================================

    def validate_data(self) -> None:
        """
        データ検証
        """

        if self.data is None:
            raise RuntimeError(
                "データが読み込まれていません"
            )

        if len(self.data) == 0:
            raise ValueError(
                "CSVデータが空です"
            )

        if self.data.isnull().any().any():

            raise ValueError(
                "CSVに欠損値があります"
            )

    # =====================================================
    # Debug
    # =====================================================

    def debug_print(
        self,
        message: str
    ) -> None:
        """
        Debug表示
        """

        if Config.DEBUG:
            print(
                f"[DEBUG] {message}"
            )

    # =====================================================
    # Result Summary
    # =====================================================

    def summary(self) -> dict:
        """
        バックテスト結果概要
        """

        trade_count = len(
            self.trade_history
        )

        final_assets = (
            self.get_final_assets()
        )

        profit = (
            final_assets
            -
            Config.INITIAL_CASH
        )

        return {
            "initial_cash":
                Config.INITIAL_CASH,

            "final_assets":
                final_assets,

            "profit":
                profit,

            "return_rate":
                profit
                /
                Config.INITIAL_CASH,

            "trade_count":
                trade_count
        }

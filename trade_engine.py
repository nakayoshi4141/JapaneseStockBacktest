"""
Japanese Stock Backtest
Version : 1.0.0 Release

trade_engine.py

日産自動車(7201)
バックテストエンジン

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

import pandas as pd

from config import Config
from portfolio import Portfolio


# =====================================================
# Trade Record
# =====================================================

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


# =====================================================
# Trade Engine
# =====================================================

class TradeEngine:
    """
    バックテスト実行エンジン
    """

    def __init__(self):

        self.portfolio = Portfolio(
            initial_cash=Config.INITIAL_CASH
        )

        self.trade_history: List[TradeRecord] = []

        self.asset_history: List[Dict[str, Any]] = []

        self.data: pd.DataFrame | None = None


    # =================================================
    # CSV Load
    # =================================================

    def load_csv(self) -> None:
        """
        CSV読込

        対応:
        ・CP932
        ・日付変換
        ・必要列抽出
        """

        self.data = pd.read_csv(
            Config.CSV_FILE,
            encoding="cp932"
        )


        # ------------------------------
        # Column Check
        # ------------------------------

        required_columns = [
            Config.DATE_COLUMN,
            Config.PRICE_COLUMN
        ]


        missing = [
            col
            for col in required_columns
            if col not in self.data.columns
        ]


        if missing:

            raise ValueError(
                f"CSV必要列不足 : {missing}"
            )


        # ------------------------------
        # Select Columns
        # ------------------------------

        self.data = self.data[
            required_columns
        ].copy()


        # ------------------------------
        # Date Convert
        # ------------------------------

        self.data[
            Config.DATE_COLUMN
        ] = pd.to_datetime(
            self.data[
                Config.DATE_COLUMN
            ]
        )


        # ------------------------------
        # Sort
        # ------------------------------

        self.data.sort_values(
            Config.DATE_COLUMN,
            inplace=True
        )


        self.data.reset_index(
            drop=True,
            inplace=True
        )


    # =================================================
    # Validation
    # =================================================

    def validate_data(self) -> None:
        """
        データ検証
        """

        if self.data is None:

            raise RuntimeError(
                "CSV未読込です"
            )


        if len(self.data) == 0:

            raise ValueError(
                "CSVデータが空です"
            )


        if self.data.isnull().any().any():

            raise ValueError(
                "CSVに欠損があります"
            )

    # =================================================
    # Trade History
    # =================================================

    def add_trade_history(
        self,
        date,
        action: str,
        price: float,
        shares: int,
        realized_profit: float = 0.0
    ) -> None:
        """
        売買履歴追加
        """

        record = TradeRecord(

            date=str(
                date.date()
            ),

            action=action,

            price=float(
                price
            ),

            shares=int(
                shares
            ),

            cash=float(
                self.portfolio.cash
            ),

            total_shares=int(
                self.portfolio.total_shares
            ),

            average_price=float(
                self.portfolio.average_price
            ),

            realized_profit=float(
                realized_profit
            )
        )


        self.trade_history.append(
            record
        )


    # =================================================
    # Asset History
    # =================================================

    def add_asset_history(
        self,
        date,
        close_price: float
    ) -> None:
        """
        資産履歴追加
        """

        self.asset_history.append(

            {

                "Date":
                    str(
                        date.date()
                    ),

                "Cash":
                    self.portfolio.cash,

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


    # =================================================
    # Buy
    # =================================================

    def execute_buy(
        self,
        date,
        price: float,
        average_down: bool = False
    ) -> None:
        """
        買付実行
        """

        shares = (
            Config.INITIAL_SHARES
        )


        if not self.portfolio.can_buy(
            price,
            shares
        ):

            return


        self.portfolio.buy(
            price,
            shares
        )


        action = (
            "AVERAGE_DOWN"
            if average_down
            else "BUY"
        )


        self.add_trade_history(

            date=date,

            action=action,

            price=price,

            shares=shares
        )


    # =================================================
    # Sell
    # =================================================

    def execute_sell(
        self,
        date,
        price: float
    ) -> None:
        """
        全株売却
        """

        shares = (
            self.portfolio.total_shares
        )


        if shares <= 0:

            return


        profit = (
            self.portfolio.sell_all(
                price
            )
        )


        self.add_trade_history(

            date=date,

            action="SELL",

            price=price,

            shares=shares,

            realized_profit=profit
        )


    # =================================================
    # Trading Decision
    # =================================================

    def check_buy_condition(
        self,
        price: float
    ) -> bool:
        """
        初回購入条件
        """

        return (
            not self.portfolio.has_position()
        )


    def check_average_down_condition(
        self,
        price: float
    ) -> bool:
        """
        ナンピン条件

        前回購入価格から6%下落
        """

        return (
            self.portfolio.should_average_down(
                price
            )
        )


    def check_sell_condition(
        self,
        price: float
    ) -> bool:
        """
        利益確定条件

        平均取得単価 +3%
        """

        return (
            self.portfolio.should_take_profit(
                price
            )
        )

    # =================================================
    # Backtest Run
    # =================================================

    def run(self) -> None:
        """
        バックテスト実行
        """

        if self.data is None:

            raise RuntimeError(
                "CSV未読込です"
            )


        for _, row in self.data.iterrows():

            date = row[
                Config.DATE_COLUMN
            ]

            price = float(
                row[
                    Config.PRICE_COLUMN
                ]
            )


            # -----------------------------
            # Sell Check
            # -----------------------------

            if self.check_sell_condition(
                price
            ):

                self.execute_sell(
                    date,
                    price
                )


            # -----------------------------
            # Buy Check
            # -----------------------------

            if self.check_buy_condition(
                price
            ):

                self.execute_buy(
                    date,
                    price
                )


            # -----------------------------
            # Averaging Down
            # -----------------------------

            elif self.check_average_down_condition(
                price
            ):

                self.execute_buy(
                    date,
                    price,
                    average_down=True
                )


            # -----------------------------
            # Asset Record
            # -----------------------------

            self.add_asset_history(
                date,
                price
            )


    # =================================================
    # DataFrame Output
    # =================================================

    def get_trade_history_df(
        self
    ) -> pd.DataFrame:
        """
        売買履歴DataFrame
        """

        if not self.trade_history:

            return pd.DataFrame()


        return pd.DataFrame(

            [
                record.__dict__

                for record

                in self.trade_history

            ]
        )


    def get_asset_history_df(
        self
    ) -> pd.DataFrame:
        """
        資産履歴DataFrame
        """

        return pd.DataFrame(
            self.asset_history
        )


    # =================================================
    # Summary
    # =================================================

    def summary(self) -> dict:
        """
        最終結果
        """

        final_assets = 0


        if self.asset_history:

            final_assets = (
                self.asset_history[-1]
                ["TotalAssets"]
            )


        return {

            "InitialCash":
                Config.INITIAL_CASH,

            "FinalAssets":
                final_assets,

            "Profit":
                final_assets
                -
                Config.INITIAL_CASH,

            "TradeCount":
                len(
                    self.trade_history
                )
        }

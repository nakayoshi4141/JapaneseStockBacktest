"""
Japanese Stock Backtest

Version : 1.0.0 Final

trade_engine.py

バックテスト実行エンジン

"""


from __future__ import annotations


from dataclasses import dataclass


from typing import List, Dict, Any


from pathlib import Path


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
    バックテストエンジン
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

        UTF-8 / UTF-8-SIG / CP932対応
        """

        encodings = [
            "utf-8-sig",
            "utf-8",
            "cp932"
        ]


        last_error = None


        for encoding in encodings:

            try:

                self.data = pd.read_csv(
                    Config.CSV_FILE,
                    encoding=encoding
                )

                break


            except UnicodeDecodeError as e:

                last_error = e

        else:

            raise last_error



        # ---------------------------------------------
        # 必須列確認
        # ---------------------------------------------


        missing = [

            col

            for col in Config.REQUIRED_COLUMNS

            if col not in self.data.columns

        ]


        if missing:

            raise ValueError(
                f"CSV必要列不足 : {missing}"
            )



        # 必要列のみ利用

        self.data = self.data[
            Config.REQUIRED_COLUMNS
        ].copy()



        # ---------------------------------------------
        # 日付変換
        # ---------------------------------------------


        self.data[
            Config.DATE_COLUMN
        ] = pd.to_datetime(

            self.data[
                Config.DATE_COLUMN
            ]

        )



        # ---------------------------------------------
        # 数値変換
        # ---------------------------------------------


        numeric_columns = [

            Config.OPEN_COLUMN,

            Config.CLOSE_COLUMN,

            Config.HIGH_COLUMN,

            Config.LOW_COLUMN

        ]


        for col in numeric_columns:

            self.data[col] = pd.to_numeric(

                self.data[col],

                errors="coerce"

            )



        # 欠損除去

        self.data.dropna(

            inplace=True

        )



        # ---------------------------------------------
        # 日付順へ変更
        # ---------------------------------------------


        self.data.sort_values(

            Config.DATE_COLUMN,

            inplace=True

        )


        self.data.reset_index(

            drop=True,

            inplace=True

        )



    # =================================================
    # Data Validation
    # =================================================


    def validate_data(self) -> None:
        """
        データ検証
        """



        if self.data is None:


            raise ValueError(

                "CSVが読み込まれていません"

            )



        if self.data.empty:


            raise ValueError(

                "CSVデータが空です"

            )



        required = [

            Config.DATE_COLUMN,

            Config.OPEN_COLUMN,

            Config.CLOSE_COLUMN,

            Config.HIGH_COLUMN,

            Config.LOW_COLUMN

        ]



        missing = [

            col

            for col in required

            if col not in self.data.columns

        ]



        if missing:


            raise ValueError(

                f"不足列 : {missing}"

            )

    # =================================================
    # History
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


        self.trade_history.append(

            TradeRecord(

                date=str(date.date()),

                action=action,

                price=float(price),

                shares=int(shares),

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

        )



    def add_asset_history(
        self,
        date,
        close_price: float
    ) -> None:
        """
        資産推移追加
        """


        self.asset_history.append(

            {

                "Date":
                    str(date.date()),

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
    # Trading
    # =================================================


    def execute_buy(
        self,
        date,
        price: float,
        action: str = "BUY"
    ) -> None:
        """
        買付実行
        """


        shares = Config.INITIAL_SHARES



        if not self.portfolio.can_buy(
            price,
            shares
        ):

            return



        self.portfolio.buy(

            price,

            shares

        )



        self.add_trade_history(

            date=date,

            action=action,

            price=price,

            shares=shares

        )




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



        realized_profit = (

            self.portfolio.sell_all(

                price

            )

        )



        self.add_trade_history(

            date=date,

            action="SELL",

            price=price,

            shares=shares,

            realized_profit=realized_profit

        )



    # =================================================
    # Entry Rule
    # =================================================


    def check_initial_entry(
        self,
        row
    ) -> None:
        """
        初回購入判定

        ポジションなしの場合
        始値購入
        """



        if self.portfolio.has_position():

            return



        self.execute_buy(

            date=row[Config.DATE_COLUMN],

            price=row[Config.OPEN_COLUMN],

            action="BUY"

        )



    # =================================================
    # Take Profit Rule
    # =================================================


    def check_take_profit(
        self,
        row
    ) -> bool:
        """
        利確判定

        高値が平均簿価+3%以上
        """


        if not self.portfolio.has_position():

            return False



        target_price = (

            self.portfolio.average_price

            *

            (

                1

                +

                Config.PROFIT_TARGET

            )

        )



        if row[Config.HIGH_COLUMN] >= target_price:


            self.execute_sell(

                date=row[Config.DATE_COLUMN],

                price=target_price

            )


            return True



        return False



    # =================================================
    # Averaging Down Rule
    # =================================================


    def check_average_down(
        self,
        row
    ) -> bool:
        """
        ナンピン判定

        直前購入価格から6%下落
        """


        if not self.portfolio.has_position():

            return False



        if self.portfolio.buy_count >= Config.MAX_BUY_COUNT:

            return False



        target_price = (

            self.portfolio.last_buy_price

            *

            (

                1

                -

                Config.AVERAGING_RATE

            )

        )



        if row[Config.LOW_COLUMN] <= target_price:


            self.execute_buy(

                date=row[Config.DATE_COLUMN],

                price=target_price,

                action="AVERAGE_DOWN"

            )


            return True



        return False

    # =================================================
    # Backtest Run
    # =================================================


    def run(self) -> None:
        """
        バックテスト実行
        """


        if self.data is None:

            raise ValueError(
                "CSVデータがありません"
            )



        for _, row in self.data.iterrows():


            date = row[Config.DATE_COLUMN]


            # -----------------------------------------
            # 保有中
            # -----------------------------------------

            if self.portfolio.has_position():


                # ① 利確確認

                sold = self.check_take_profit(
                    row
                )


                if sold:

                    self.add_asset_history(

                        date,

                        row[Config.CLOSE_COLUMN]

                    )

                    continue



                # ② ナンピン確認

                self.check_average_down(
                    row
                )



            # -----------------------------------------
            # ポジションなし
            # -----------------------------------------

            else:


                self.check_initial_entry(
                    row
                )



            # -----------------------------------------
            # 日次資産記録
            # -----------------------------------------


            self.add_asset_history(

                date,

                row[Config.CLOSE_COLUMN]

            )



    # =================================================
    # DataFrame Convert
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

                for record in self.trade_history

            ]

        )



    def get_asset_history_df(
        self
    ) -> pd.DataFrame:
        """
        資産履歴DataFrame
        """


        if not self.asset_history:

            return pd.DataFrame()



        return pd.DataFrame(

            self.asset_history

        )

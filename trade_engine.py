"""
Japanese Stock Backtest

Version : 1.0.0 Release

trade_engine.py

日産自動車(7201)
バックテストエンジン

売買仕様:

・ポジションなし
    → 始値で100株購入

・ナンピン
    → 直前購入価格から6%下落
    → 安値到達時に条件価格で100株購入

・利益確定
    → 平均取得単価から3%上昇
    → 高値到達時に条件価格で全株売却

・資産評価
    → 終値

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
        ・7201.csv
        ・不要列除外
        """


        self.data = pd.read_csv(

            Config.CSV_FILE,

            encoding="cp932"

        )


        required = [

            Config.DATE_COLUMN,

            Config.OPEN_COLUMN,

            Config.HIGH_COLUMN,

            Config.LOW_COLUMN,

            Config.CLOSE_COLUMN

        ]


        missing = [

            col

            for col in required

            if col not in self.data.columns

        ]


        if missing:

            raise ValueError(

                f"CSV必要列不足 : {missing}"

            )


        self.data = self.data[

            required

        ].copy()



        self.data[

            Config.DATE_COLUMN

        ] = pd.to_datetime(

            self.data[

                Config.DATE_COLUMN

            ]

        )



        self.data.sort_values(

            Config.DATE_COLUMN,

            inplace=True

        )



        self.data.reset_index(

            drop=True,

            inplace=True

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
        売買履歴保存
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

    # =================================================
    # Asset History
    # =================================================


    def add_asset_history(

        self,

        date,

        close_price: float

    ) -> None:
        """
        資産履歴保存

        終値評価
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
    # Initial Buy
    # =================================================


    def execute_initial_buy(

        self,

        date,

        open_price: float

    ) -> None:
        """
        初回購入

        ポジションなしの場合
        始値で100株購入
        """


        shares = Config.INITIAL_SHARES



        if not self.portfolio.can_buy(

            open_price,

            shares

        ):

            return



        self.portfolio.buy(

            open_price,

            shares

        )



        self.add_trade_history(

            date=date,

            action="BUY",

            price=open_price,

            shares=shares

        )



    # =================================================
    # Averaging Down
    # =================================================


    def execute_average_down(

        self,

        date,

        previous_price: float

    ) -> None:
        """
        ナンピン購入

        条件:
        直前購入価格から6%下落

        約定:
        条件価格

        """


        buy_price = (

            previous_price

            *

            (1 - Config.AVERAGE_DOWN_RATE)

        )



        shares = Config.INITIAL_SHARES



        if not self.portfolio.can_buy(

            buy_price,

            shares

        ):

            return



        self.portfolio.buy(

            buy_price,

            shares

        )



        self.add_trade_history(

            date=date,

            action="AVERAGE_DOWN",

            price=buy_price,

            shares=shares

        )



    # =================================================
    # Profit Taking
    # =================================================


    def execute_profit_sell(

        self,

        date,

        average_price: float

    ) -> None:
        """
        利益確定売却

        条件:
        平均取得単価 +3%

        約定:
        条件価格

        """


        sell_price = (

            average_price

            *

            (1 + Config.PROFIT_TARGET)

        )



        shares = (

            self.portfolio.total_shares

        )



        if shares <= 0:

            return



        profit = self.portfolio.sell_all(

            sell_price

        )



        self.add_trade_history(

            date=date,

            action="SELL",

            price=sell_price,

            shares=shares,

            realized_profit=profit

        )



    # =================================================
    # Condition Check
    # =================================================


    def check_average_down(

        self,

        low_price: float

    ) -> bool:
        """
        ナンピン判定

        当日安値で判定
        """


        if not self.portfolio.has_position():

            return False



        last_price = (

            self.portfolio.last_buy_price

        )


        if last_price <= 0:

            return False



        limit_price = (

            last_price

            *

            (1 - Config.AVERAGE_DOWN_RATE)

        )



        return (

            low_price <= limit_price

        )



    def check_profit_target(

        self,

        high_price: float

    ) -> bool:
        """
        利益確定判定

        当日高値で判定
        """


        if not self.portfolio.has_position():

            return False



        target_price = (

            self.portfolio.average_price

            *

            (1 + Config.PROFIT_TARGET)

        )



        return (

            high_price >= target_price

        )  
           # =================================================
    # Backtest Execution
    # =================================================


    def run(self) -> None:
        """
        バックテスト実行

        1日処理順:

        ① 始値購入
        ② ナンピン（安値）
        ③ 利益確定（高値）
        ④ 終値評価

        """


        if self.data is None:

            raise RuntimeError(

                "CSV未読込です"

            )



        for _, row in self.data.iterrows():


            date = row[

                Config.DATE_COLUMN

            ]


            open_price = float(

                row[

                    Config.OPEN_COLUMN

                ]

            )


            high_price = float(

                row[

                    Config.HIGH_COLUMN

                ]

            )


            low_price = float(

                row[

                    Config.LOW_COLUMN

                ]

            )


            close_price = float(

                row[

                    Config.CLOSE_COLUMN

                ]

            )



            # ---------------------------------
            # ① 初回購入
            # ---------------------------------


            if not self.portfolio.has_position():

                self.execute_initial_buy(

                    date,

                    open_price

                )


            else:


                # -----------------------------
                # ② ナンピン判定
                # -----------------------------


                if self.check_average_down(

                    low_price

                ):


                    self.execute_average_down(

                        date,

                        self.portfolio.last_buy_price

                    )



                # -----------------------------
                # ③ 利益確定判定
                # -----------------------------


                if self.check_profit_target(

                    high_price

                ):


                    self.execute_profit_sell(

                        date,

                        self.portfolio.average_price

                    )



            # ---------------------------------
            # ④ 終値評価
            # ---------------------------------


            self.add_asset_history(

                date,

                close_price

            )



    # =================================================
    # Output
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
        資産推移DataFrame
        """


        return pd.DataFrame(

            self.asset_history

        )



    # =================================================
    # Summary
    # =================================================


    def summary(self) -> dict:
        """
        バックテスト結果
        """


        final_assets = Config.INITIAL_CASH



        if self.asset_history:


            final_assets = (

                self.asset_history[-1]

                [

                    "TotalAssets"

                ]

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


            "ReturnRate":

                (

                    final_assets

                    /

                    Config.INITIAL_CASH

                    -

                    1

                ),


            "TradeCount":

                len(

                    self.trade_history

                )

        } 

        )

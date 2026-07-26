"""
Japanese Stock Backtest
Version : 1.0.0

statistics.py

バックテスト結果分析
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestStatistics:
    """
    バックテスト統計計算クラス
    """

    asset_history: pd.DataFrame
    trade_history: pd.DataFrame

    # =====================================================
    # Basic
    # =====================================================

    def initial_assets(self) -> float:
        """
        初期資産
        """

        if self.asset_history.empty:
            return 0.0

        return float(
            self.asset_history.iloc[0]["TotalAssets"]
        )

    def final_assets(self) -> float:
        """
        最終資産
        """

        if self.asset_history.empty:
            return 0.0

        return float(
            self.asset_history.iloc[-1]["TotalAssets"]
        )

    def total_profit(self) -> float:
        """
        総損益
        """

        return (
            self.final_assets()
            -
            self.initial_assets()
        )

    def return_rate(self) -> float:
        """
        総合利益率
        """

        initial = self.initial_assets()

        if initial == 0:
            return 0.0

        return (
            self.total_profit()
            /
            initial
        )
          # =====================================================
    # Trade Statistics
    # =====================================================

    def trade_count(self) -> int:
        """
        売買回数
        """

        if self.trade_history.empty:
            return 0

        return len(
            self.trade_history
        )

    def sell_count(self) -> int:
        """
        売却回数
        """

        if self.trade_history.empty:
            return 0

        return int(
            (
                self.trade_history["取引"]
                == "SELL"
            ).sum()
        )

    def winning_trade_count(self) -> int:
        """
        利益確定回数
        """

        if self.trade_history.empty:
            return 0

        sell_data = self.trade_history[
            self.trade_history["取引"]
            == "SELL"
        ]

        return int(
            (
                sell_data["実現損益"]
                > 0
            ).sum()
        )

    def win_rate(self) -> float:
        """
        勝率
        """

        sells = self.sell_count()

        if sells == 0:
            return 0.0

        return (
            self.winning_trade_count()
            /
            sells
        )

    # =====================================================
    # Drawdown
    # =====================================================

    def max_drawdown(self) -> float:
        """
        最大ドローダウン率
        """

        if self.asset_history.empty:
            return 0.0

        assets = (
            self.asset_history["TotalAssets"]
        )

        peak = assets.cummax()

        drawdown = (
            assets - peak
        ) / peak

        return float(
            drawdown.min()
        )

    # =====================================================
    # CAGR
    # =====================================================

    def cagr(self) -> float:
        """
        年平均成長率
        """

        if self.asset_history.empty:
            return 0.0

        start = (
            pd.to_datetime(
                self.asset_history.iloc[0]["Date"]
            )
        )

        end = (
            pd.to_datetime(
                self.asset_history.iloc[-1]["Date"]
            )
        )

        years = (
            end - start
        ).days / 365.25

        if years <= 0:
            return 0.0

        initial = self.initial_assets()

        final = self.final_assets()

        return (
            (final / initial)
            **
            (1 / years)
            -
            1
        )
          # =====================================================
    # Yearly Performance
    # =====================================================

    def yearly_profit(self) -> pd.DataFrame:
        """
        年別損益
        """

        if self.asset_history.empty:
            return pd.DataFrame()

        df = self.asset_history.copy()

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df["Year"] = (
            df["Date"]
            .dt.year
        )

        yearly = (
            df.groupby("Year")
            ["TotalAssets"]
            .agg(
                [
                    "first",
                    "last"
                ]
            )
            .reset_index()
        )

        yearly["Profit"] = (
            yearly["last"]
            -
            yearly["first"]
        )

        yearly["ReturnRate"] = (
            yearly["Profit"]
            /
            yearly["first"]
        )

        return yearly


    # =====================================================
    # Summary
    # =====================================================

    def summary(self) -> dict:
        """
        全統計結果
        """

        return {
            "Initial Assets":
                self.initial_assets(),

            "Final Assets":
                self.final_assets(),

            "Total Profit":
                self.total_profit(),

            "Return Rate":
                self.return_rate(),

            "Trade Count":
                self.trade_count(),

            "Sell Count":
                self.sell_count(),

            "Win Rate":
                self.win_rate(),

            "Max Drawdown":
                self.max_drawdown(),

            "CAGR":
                self.cagr(),
        }


    # =====================================================
    # DataFrame
    # =====================================================

    def summary_dataframe(
        self
    ) -> pd.DataFrame:
        """
        統計結果DataFrame
        """

        return pd.DataFrame(
            [
                self.summary()
            ]
        )

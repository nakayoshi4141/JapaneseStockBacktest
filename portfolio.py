"""
Japanese Stock Backtest

Version : 1.0.1 Final

portfolio.py

ポートフォリオ管理クラス
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config import Config


@dataclass
class Portfolio:
    """
    ポートフォリオ管理クラス

    管理内容
    --------
    ・現金残高
    ・保有株数
    ・取得総額
    ・平均取得単価
    ・直前購入価格
    ・ナンピン回数
    ・実現損益
    """

    # ==========================================
    # Portfolio Information
    # ==========================================

    cash: float = Config.INITIAL_CASH

    total_shares: int = 0

    total_cost: float = 0.0

    average_price: float = 0.0

    last_buy_price: float = 0.0

    average_down_count: int = 0

    realized_profit: float = 0.0


    # ==========================================
    # Properties
    # ==========================================

    @property
    def has_position(self) -> bool:
        """
        保有株があるか
        """

        return self.total_shares > 0


    @property
    def market_value(self) -> float:
        """
        現在の簿価
        """

        return self.total_cost


    @property
    def next_average_down_price(self) -> Optional[float]:
        """
        次回ナンピン価格

        保有していない場合は None
        """

        if not self.has_position:
            return None

        return (
            self.last_buy_price
            * (1 - Config.AVERAGE_DOWN_RATE)
        )


    @property
    def invested_amount(self) -> float:
        """
        投資元本
        """

        return self.total_cost


    @property
    def available_cash(self) -> float:
        """
        利用可能現金
        """

        return self.cash


    @property
    def total_assets(self) -> float:
        """
        現時点の総資産（簿価ベース）

        評価額は trade_engine.py 側で
        当日価格を使って計算する。
        """

        return (
            self.cash
            + self.total_cost
        )

"""
Japanese Stock Backtest
Version 1.0.0

portfolio.py
ポートフォリオ管理クラス
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class TradeRecord:
    """売買履歴"""

    date: str
    action: str
    price: float
    shares: int
    average_price: float
    total_shares: int
    profit: float = 0.0


class Portfolio:
    """
    保有株管理

    売買判断は trade_engine.py が行う。
    Portfolio は保有状態のみ管理する。
    """

    def __init__(self, config):

        self.config = config

        self.reset()

    def reset(self):
        """初期状態"""

        # 現金
        self.cash = self.config.INITIAL_CASH

        # 保有状態
        self.has_position = False

        self.total_shares = 0

        self.total_cost = 0.0

        self.average_price = 0.0

        self.last_buy_price = 0.0

        self.next_buy_price = 0.0

        self.target_price = 0.0

        self.buy_count = 0

        # 累計利益
        self.total_profit = 0.0

        # 売買履歴
        self.trade_history: List[TradeRecord] = []

    @property
    def market_value(self):

        if not self.has_position:
            return 0.0

        return self.total_shares * self.average_price

    def unrealized_profit(self, current_price):

        if not self.has_position:
            return 0.0

        return (current_price - self.average_price) * self.total_shares

    def current_assets(self, current_price):

        return self.cash + self.total_shares * current_price

    def __str__(self):

        return (
            f"Cash={self.cash:,.0f}, "
            f"Shares={self.total_shares}, "
            f"Avg={self.average_price:.2f}"
        )

"""
Japanese Stock Backtest
Version 1.0.0

portfolio.py

ポートフォリオ管理
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Portfolio:
    """
    保有資産管理クラス
    """

    initial_cash: float

    def __post_init__(self):

        self.cash = float(self.initial_cash)

        self.total_shares = 0

        self.total_cost = 0.0

        self.average_price = 0.0

        self.last_buy_price = None

        self.buy_count = 0

    # =====================================================
    # Position
    # =====================================================

    @property
    def has_position(self) -> bool:
        """
        保有中かどうか
        """
        return self.total_shares > 0

    # =====================================================
    # Buy
    # =====================================================

    def can_buy(
        self,
        price: float,
        shares: int
    ) -> bool:
        """
        購入可能か判定
        """

        required_cash = price * shares

        return self.cash >= required_cash

    def buy(
        self,
        price: float,
        shares: int
    ) -> None:
        """
        株を購入する
        """

        cost = price * shares

        if cost > self.cash:
            raise ValueError("Cash不足")

        self.cash -= cost

        self.total_cost += cost

        self.total_shares += shares

        self.average_price = (
            self.total_cost
            / self.total_shares
        )

        self.last_buy_price = price

        self.buy_count += 1

    # =====================================================
    # Average Down
    # =====================================================

    def should_average_down(
        self,
        current_price: float,
        rate: float
    ) -> bool:
        """
        ナンピン判定
        """

        if not self.has_position:
            return False

        if self.last_buy_price is None:
            return False

        target = self.last_buy_price * (1.0 - rate)

        return current_price <= target
        # =====================================================
    # Take Profit
    # =====================================================

    def should_take_profit(
        self,
        current_price: float,
        profit_rate: float
    ) -> bool:
        """
        利益確定判定

        Parameters
        ----------
        current_price : float
            現在価格

        profit_rate : float
            利益確定率（例：0.03）

        Returns
        -------
        bool
            利確条件を満たせばTrue
        """

        if not self.has_position:
            return False

        target_price = self.average_price * (1.0 + profit_rate)

        return current_price >= target_price

    # =====================================================
    # Market Value
    # =====================================================

    def market_value(
        self,
        current_price: float
    ) -> float:
        """
        保有株の評価額
        """

        return self.total_shares * current_price

    def unrealized_profit(
        self,
        current_price: float
    ) -> float:
        """
        評価損益
        """

        return self.market_value(current_price) - self.total_cost

    def total_assets(
        self,
        current_price: float
    ) -> float:
        """
        総資産
        """

        return self.cash + self.market_value(current_price)

    # =====================================================
    # Sell
    # =====================================================

    def sell_all(
        self,
        price: float
    ) -> float:
        """
        全株売却

        Returns
        -------
        float
            実現損益
        """

        if not self.has_position:
            return 0.0

        proceeds = self.total_shares * price

        realized_profit = proceeds - self.total_cost

        self.cash += proceeds

        self.reset_position()

        return realized_profit
    # =====================================================
    # Reset Position
    # =====================================================

    def reset_position(self) -> None:
        """
        保有ポジションを初期化する
        """

        self.total_shares = 0
        self.total_cost = 0.0
        self.average_price = 0.0
        self.last_buy_price = None
        self.buy_count = 0

    # =====================================================
    # Information
    # =====================================================

    def position_summary(self) -> dict:
        """
        現在のポジション情報を辞書形式で返す
        """

        return {
            "cash": self.cash,
            "shares": self.total_shares,
            "total_cost": self.total_cost,
            "average_price": self.average_price,
            "last_buy_price": self.last_buy_price,
            "buy_count": self.buy_count,
        }

    def __repr__(self) -> str:
        """
        デバッグ表示
        """

        return (
            "Portfolio("
            f"cash={self.cash:.2f}, "
            f"shares={self.total_shares}, "
            f"average_price={self.average_price:.2f}, "
            f"buy_count={self.buy_count})"
        )

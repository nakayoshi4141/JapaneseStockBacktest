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
    # ==========================================
    # Trading Methods
    # ==========================================

    def buy(
        self,
        price: float,
        shares: int = Config.INITIAL_SHARES,
    ) -> None:
        """
        株式購入

        Parameters
        ----------
        price : float
            購入価格

        shares : int
            購入株数
        """

        if price <= 0:
            raise ValueError("Purchase price must be greater than zero.")

        if shares <= 0:
            raise ValueError("Purchase shares must be greater than zero.")

        purchase_amount = price * shares

        if purchase_amount > self.cash:
            raise ValueError("Insufficient cash balance.")

        previous_shares = self.total_shares

        # 現金減少
        self.cash -= purchase_amount

        # 保有情報更新
        self.total_cost += purchase_amount
        self.total_shares += shares

        # 平均取得単価更新
        self.average_price = (
            self.total_cost / self.total_shares
        )

        # 最終購入価格
        self.last_buy_price = price

        # 初回購入以外はナンピン回数を加算
        if previous_shares > 0:
            self.average_down_count += 1


    def can_average_down(self) -> bool:
        """
        ナンピン可能か判定
        """

        if not self.has_position:
            return False

        return (
            self.average_down_count
            < Config.MAX_AVERAGE_DOWN_COUNT
        )


    def sell_all(
        self,
        price: float,
    ) -> float:
        """
        全株売却

        Parameters
        ----------
        price : float
            売却価格

        Returns
        -------
        float
            実現損益
        """

        if not self.has_position:
            return 0.0

        if price <= 0:
            raise ValueError("Sell price must be greater than zero.")

        proceeds = (
            price
            * self.total_shares
        )

        profit = (
            proceeds
            - self.total_cost
        )

        # 現金へ反映
        self.cash += proceeds

        # 実現損益累積
        self.realized_profit += profit

        # 保有情報リセット
        self.total_shares = 0
        self.total_cost = 0.0
        self.average_price = 0.0
        self.last_buy_price = 0.0
        self.average_down_count = 0

        return profit
            # ==========================================
    # Evaluation Methods
    # ==========================================

    def current_market_value(
        self,
        current_price: float,
    ) -> float:
        """
        現在の評価額

        Parameters
        ----------
        current_price : float
            現在株価

        Returns
        -------
        float
            保有株式の評価額
        """

        if not self.has_position:
            return 0.0

        return (
            current_price
            * self.total_shares
        )


    def unrealized_profit(
        self,
        current_price: float,
    ) -> float:
        """
        評価損益
        """

        return (
            self.current_market_value(current_price)
            - self.total_cost
        )


    def total_asset(
        self,
        current_price: float,
    ) -> float:
        """
        総資産

        現金＋株式評価額
        """

        return (
            self.cash
            + self.current_market_value(current_price)
        )


    # ==========================================
    # Utility Methods
    # ==========================================

    def reset(self) -> None:
        """
        ポートフォリオを初期状態へ戻す

        通常のバックテストでは使用しないが、
        単体テスト等で利用する。
        """

        self.cash = Config.INITIAL_CASH

        self.total_shares = 0

        self.total_cost = 0.0

        self.average_price = 0.0

        self.last_buy_price = 0.0

        self.average_down_count = 0

        self.realized_profit = 0.0


    def __str__(self) -> str:
        """
        ポートフォリオ情報
        """

        return (
            "Portfolio("
            f"cash={self.cash:.2f}, "
            f"shares={self.total_shares}, "
            f"average_price={self.average_price:.2f}, "
            f"total_cost={self.total_cost:.2f}, "
            f"realized_profit={self.realized_profit:.2f}"
            ")"
        )

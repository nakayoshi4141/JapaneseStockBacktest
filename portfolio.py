"""Japanese Stock Backtest - Portfolio management."""
from __future__ import annotations

from dataclasses import dataclass

from config import Config


@dataclass
class Portfolio:
    """Holds cash and one-stock position state."""

    cash: float = Config.INITIAL_CASH
    total_shares: int = 0
    total_cost: float = 0.0
    average_price: float = 0.0
    last_buy_price: float = 0.0
    buy_count: int = 0
    realized_profit: float = 0.0

    @property
    def has_position(self) -> bool:
        return self.total_shares > 0

    @property
    def book_value(self) -> float:
        return self.total_cost

    @property
    def next_buy_price(self) -> float | None:
        if not self.has_position:
            return None
        return self.last_buy_price * (1.0 - Config.AVERAGING_RATE)

    @property
    def available_cash(self) -> float:
        return self.cash

    def buy(self, price: float, shares: int = Config.INITIAL_SHARES) -> None:
        if price <= 0:
            raise ValueError("Purchase price must be greater than zero.")
        if shares <= 0:
            raise ValueError("Purchase shares must be greater than zero.")
        amount = float(price) * int(shares)
        if amount > self.cash + 1e-9:
            raise ValueError("Insufficient cash balance.")
        self.cash -= amount
        self.total_cost += amount
        self.total_shares += int(shares)
        self.average_price = self.total_cost / self.total_shares
        self.last_buy_price = float(price)
        self.buy_count += 1

    def can_buy(self, price: float, shares: int = Config.INITIAL_SHARES) -> bool:
        if self.buy_count >= Config.MAX_BUY_COUNT:
            return False
        if price <= 0 or shares <= 0:
            return False
        return price * shares <= self.cash + 1e-9

    def sell_all(self, price: float) -> float:
        if not self.has_position:
            return 0.0
        if price <= 0:
            raise ValueError("Sell price must be greater than zero.")
        shares = self.total_shares
        proceeds = float(price) * shares
        profit = proceeds - self.total_cost
        self.cash += proceeds
        self.realized_profit += profit
        self.total_shares = 0
        self.total_cost = 0.0
        self.average_price = 0.0
        self.last_buy_price = 0.0
        self.buy_count = 0
        return profit

    def market_value(self, current_price: float) -> float:
        if current_price < 0:
            raise ValueError("Current price cannot be negative.")
        return self.total_shares * float(current_price)

    def total_asset(self, current_price: float) -> float:
        return self.cash + self.market_value(current_price)

    def unrealized_profit(self, current_price: float) -> float:
        return self.market_value(current_price) - self.total_cost

    def reset(self) -> None:
        self.cash = Config.INITIAL_CASH
        self.total_shares = 0
        self.total_cost = 0.0
        self.average_price = 0.0
        self.last_buy_price = 0.0
        self.buy_count = 0
        self.realized_profit = 0.0

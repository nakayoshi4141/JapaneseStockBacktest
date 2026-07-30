"""
Japanese Stock Backtest
Version 1.0.1 Final
portfolio.py
"""
from dataclasses import dataclass
from config import Config

@dataclass
class Portfolio:
    cash: float = Config.INITIAL_CASH
    total_shares: int = 0
    total_cost: float = 0.0
    average_price: float = 0.0
    average_down_count: int = 0
    last_buy_price: float = 0.0
    realized_profit: float = 0.0

    @property
    def has_position(self)->bool:
        return self.total_shares>0

    @property
    def next_average_down_price(self):
        if not self.has_position:
            return None
        return self.last_buy_price*(1-Config.AVERAGE_DOWN_RATE)

    def buy(self, price:float, shares:int=Config.INITIAL_SHARES):
        cost=price*shares
        if cost>self.cash:
            raise ValueError("Insufficient cash")
        self.cash-=cost
        self.total_cost+=cost
        self.total_shares+=shares
        self.average_price=self.total_cost/self.total_shares
        self.last_buy_price=price
        if self.total_shares>shares:
            self.average_down_count+=1

    def can_average_down(self)->bool:
        return self.has_position and self.average_down_count<Config.MAX_AVERAGE_DOWN_COUNT

    def sell_all(self, price:float)->float:
        if not self.has_position:
            return 0.0
        proceeds=price*self.total_shares
        profit=proceeds-self.total_cost
        self.cash+=proceeds
        self.realized_profit+=profit
        self.total_shares=0
        self.total_cost=0.0
        self.average_price=0.0
        self.average_down_count=0
        self.last_buy_price=0.0
        return profit

    def market_value(self, price:float)->float:
        return self.total_shares*price

    def unrealized_profit(self, price:float)->float:
        return self.market_value(price)-self.total_cost

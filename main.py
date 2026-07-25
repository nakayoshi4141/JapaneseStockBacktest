"""
Japanese Stock Backtest
Version 1.0

main.py
"""

from config import Config
from portfolio import Portfolio
from trade_engine import TradeEngine


def main():

    config = Config()

    portfolio = Portfolio(config)

    engine = TradeEngine(portfolio)

    engine.load_csv()

    engine.run()


if __name__ == "__main__":
    main()

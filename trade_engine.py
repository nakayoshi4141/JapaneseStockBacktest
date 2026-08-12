"""Japanese Stock Backtest - Version 1.0.1 trade engine."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from config import Config
from portfolio import Portfolio


@dataclass(frozen=True)
class TradeRecord:
    date: str
    action: str
    price: float
    shares: int
    cash: float
    total_shares: int
    average_price: float
    realized_profit: float


class TradeEngine:
    """Loads price data and executes the fixed backtest rules."""

    def __init__(self, portfolio: Portfolio | None = None) -> None:
        Config.validate()
        self.portfolio = portfolio or Portfolio()
        self.trade_history: list[TradeRecord] = []
        self.asset_history: list[dict[str, Any]] = []
        self.data: pd.DataFrame | None = None

    def _debug(self, message: str) -> None:
        if Config.DEBUG:
            print(message)

    def load_csv(self, csv_file: str | Path | None = None) -> pd.DataFrame:
        path = Path(csv_file) if csv_file is not None else Path(Config.CSV_FILE)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        last_error: Exception | None = None
        for encoding in Config.CSV_ENCODINGS:
            try:
                df = pd.read_csv(path, encoding=encoding)
                last_error = None
                break
            except UnicodeDecodeError as exc:
                last_error = exc
        if last_error is not None:
            raise UnicodeError(f"Unable to decode CSV: {path}") from last_error
        missing = [c for c in Config.REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"CSV required columns are missing: {missing}")
        df = df.loc[:, list(Config.REQUIRED_COLUMNS)].copy()
        df[Config.DATE_COLUMN] = pd.to_datetime(df[Config.DATE_COLUMN], errors="coerce")
        for column in (Config.OPEN_COLUMN, Config.HIGH_COLUMN, Config.LOW_COLUMN, Config.CLOSE_COLUMN):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        if df.empty:
            raise ValueError("CSV data is empty.")
        if df.isna().any().any():
            df = df.dropna().copy()
        if df.empty:
            raise ValueError("CSV contains no valid rows after data cleaning.")
        if (df[[Config.OPEN_COLUMN, Config.HIGH_COLUMN, Config.LOW_COLUMN, Config.CLOSE_COLUMN]] <= 0).any().any():
            raise ValueError("Price data must be greater than zero.")
        df = df.sort_values(Config.DATE_COLUMN).drop_duplicates(Config.DATE_COLUMN, keep="last").reset_index(drop=True)
        self.data = df
        return df

    def validate_data(self) -> None:
        if self.data is None:
            raise ValueError("CSV data has not been loaded.")
        if self.data.empty:
            raise ValueError("CSV data is empty.")
        missing = [c for c in Config.REQUIRED_COLUMNS if c not in self.data.columns]
        if missing:
            raise ValueError(f"CSV required columns are missing: {missing}")

    def _record_trade(self, date: pd.Timestamp, action: str, price: float, shares: int, profit: float = 0.0) -> None:
        self.trade_history.append(TradeRecord(
            date=date.strftime("%Y-%m-%d"), action=action, price=float(price), shares=int(shares),
            cash=float(self.portfolio.cash), total_shares=int(self.portfolio.total_shares),
            average_price=float(self.portfolio.average_price), realized_profit=float(profit)
        ))

    def _record_assets(self, date: pd.Timestamp, close_price: float) -> None:
        self.asset_history.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Close": float(close_price),
            "Cash": float(self.portfolio.cash),
            "MarketValue": float(self.portfolio.market_value(close_price)),
            "TotalAssets": float(self.portfolio.total_asset(close_price)),
            "Shares": int(self.portfolio.total_shares),
            "AveragePrice": float(self.portfolio.average_price),
        })

    def execute_buy(self, date: pd.Timestamp, price: float, action: str = "BUY") -> bool:
        shares = Config.INITIAL_SHARES
        if not self.portfolio.can_buy(price, shares):
            self._debug(f"[BUY SKIPPED] {date.date()} price={price:.2f} cash={self.portfolio.cash:.2f}")
            return False
        try:
            self.portfolio.buy(price, shares)
        except ValueError as exc:
            self._debug(f"[BUY SKIPPED] {date.date()} {exc}")
            return False
        self._record_trade(date, action, price, shares)
        self._debug(f"[{action}] {date.date()} price={price:.2f} shares={shares}")
        return True

    def execute_sell(self, date: pd.Timestamp, price: float) -> bool:
        if not self.portfolio.has_position:
            return False
        shares = self.portfolio.total_shares
        try:
            profit = self.portfolio.sell_all(price)
        except ValueError as exc:
            self._debug(f"[SELL SKIPPED] {date.date()} {exc}")
            return False
        self._record_trade(date, "SELL", price, shares, profit)
        self._debug(f"[SELL] {date.date()} price={price:.2f} shares={shares} profit={profit:.2f}")
        return True

    def check_initial_entry(self, row: pd.Series) -> bool:
        if self.portfolio.has_position:
            return False
        return self.execute_buy(row[Config.DATE_COLUMN], float(row[Config.OPEN_COLUMN]), "BUY")

    def check_take_profit(self, row: pd.Series) -> bool:
        if not self.portfolio.has_position:
            return False
        target = self.portfolio.average_price * (1.0 + Config.PROFIT_TARGET)
        if float(row[Config.HIGH_COLUMN]) >= target:
            return self.execute_sell(row[Config.DATE_COLUMN], target)
        return False

    def check_average_down(self, row: pd.Series) -> bool:
        if not self.portfolio.has_position or self.portfolio.buy_count >= Config.MAX_BUY_COUNT:
            return False
        target = self.portfolio.last_buy_price * (1.0 - Config.AVERAGING_RATE)
        if float(row[Config.LOW_COLUMN]) <= target:
            return self.execute_buy(row[Config.DATE_COLUMN], target, "AVERAGE_DOWN")
        return False

    def run(self) -> pd.DataFrame:
        self.validate_data()
       self.portfolio.reset()
        self.trade_history.clear()
        self.asset_history.clear()
        for _, row in self.data.iterrows():
            date = row[Config.DATE_COLUMN]
            if self.portfolio.has_position:
                sold = self.check_take_profit(row)
                if not sold:
                    self.check_average_down(row)
            else:
                self.check_initial_entry(row)
                # The initial purchase occurs at the day's open. Because the
                # strategy defines take-profit using intraday prices, the
                # same day's high must also be evaluated after that purchase.
                if self.portfolio.has_position:
                    self.check_take_profit(row)
            self._record_assets(date, float(row[Config.CLOSE_COLUMN]))
        return self.get_asset_history_df()

    def get_trade_history_df(self) -> pd.DataFrame:
        columns = list(TradeRecord.__annotations__.keys())
        if not self.trade_history:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame([asdict(record) for record in self.trade_history])

    def get_asset_history_df(self) -> pd.DataFrame:
        columns = ["Date", "Close", "Cash", "MarketValue", "TotalAssets", "Shares", "AveragePrice"]
        if not self.asset_history:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(self.asset_history, columns=columns)

"""Japanese Stock Backtest - statistics."""
from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from config import Config


@dataclass
class BacktestStatistics:
    asset_history: pd.DataFrame
    trade_history: pd.DataFrame

    def initial_assets(self) -> float:
        return float(Config.INITIAL_CASH)

    def final_assets(self) -> float:
        if self.asset_history.empty:
            return self.initial_assets()
        return float(self.asset_history.iloc[-1]["TotalAssets"])

    def total_profit(self) -> float:
        return self.final_assets() - self.initial_assets()

    def return_rate(self) -> float:
        initial = self.initial_assets()
        return self.total_profit() / initial if initial else 0.0

    def trade_count(self) -> int:
        return int(len(self.trade_history))

    def sell_count(self) -> int:
        if self.trade_history.empty:
            return 0
        return int((self.trade_history["action"] == "SELL").sum())

    def winning_trade_count(self) -> int:
        if self.trade_history.empty:
            return 0
        sells = self.trade_history[self.trade_history["action"] == "SELL"]
        return int((sells["realized_profit"] > 0).sum()) if not sells.empty else 0

    def win_rate(self) -> float:
        sells = self.sell_count()
        return self.winning_trade_count() / sells if sells else 0.0

    def max_drawdown(self) -> float:
        if self.asset_history.empty:
            return 0.0
        assets = pd.to_numeric(self.asset_history["TotalAssets"], errors="coerce")
        peak = assets.cummax()
        drawdown = (assets - peak) / peak.replace(0, pd.NA)
        return float(drawdown.min()) if not drawdown.dropna().empty else 0.0

    def cagr(self) -> float:
        if self.asset_history.empty:
            return 0.0
        dates = pd.to_datetime(self.asset_history["Date"])
        years = (dates.iloc[-1] - dates.iloc[0]).days / 365.25
        if years <= 0 or self.initial_assets() <= 0 or self.final_assets() <= 0:
            return 0.0
        return (self.final_assets() / self.initial_assets()) ** (1 / years) - 1

    def yearly_profit(self) -> pd.DataFrame:
        if self.asset_history.empty:
            return pd.DataFrame(columns=["Year", "StartAssets", "EndAssets", "Profit", "ReturnRate"])
        df = self.asset_history.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        grouped = df.groupby(df["Date"].dt.year)["TotalAssets"].agg(["first", "last"]).reset_index()
        grouped.columns = ["Year", "StartAssets", "EndAssets"]
        grouped["Profit"] = grouped["EndAssets"] - grouped["StartAssets"]
        grouped["ReturnRate"] = grouped["Profit"] / grouped["StartAssets"].replace(0, pd.NA)
        return grouped

    def summary(self) -> dict[str, float | int]:
        return {
            "Initial Assets": self.initial_assets(),
            "Final Assets": self.final_assets(),
            "Total Profit": self.total_profit(),
            "Return Rate": self.return_rate(),
            "Trade Count": self.trade_count(),
            "Sell Count": self.sell_count(),
            "Winning Trades": self.winning_trade_count(),
            "Win Rate": self.win_rate(),
            "Max Drawdown": self.max_drawdown(),
            "CAGR": self.cagr(),
        }

    def summary_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([self.summary()])

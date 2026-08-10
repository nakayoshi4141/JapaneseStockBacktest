"""Japanese Stock Backtest - equity chart."""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from config import Config


class EquityChart:
    def __init__(self, output_file: Path | None = None) -> None:
        Config.create_output_directory()
        self.output_file = output_file or (Config.OUTPUT_DIR / Config.CHART_FILE)

    def validate(self, asset_history: pd.DataFrame) -> None:
        if asset_history.empty:
            raise ValueError("Asset history is empty.")
        required = {"Date", "TotalAssets"}
        missing = required.difference(asset_history.columns)
        if missing:
            raise ValueError(f"Required chart columns are missing: {sorted(missing)}")

    def create(self, asset_history: pd.DataFrame) -> Path:
        self.validate(asset_history)
        df = asset_history.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df["Date"], df["TotalAssets"], label="Total Assets")
        ax.set_title("Nissan 7201 Backtest Equity Curve")
        ax.set_xlabel("Date")
        ax.set_ylabel("Assets (JPY)")
        ax.grid(True)
        ax.legend()
        fig.tight_layout()
        fig.savefig(self.output_file, dpi=200)
        plt.close(fig)
        if not self.output_file.exists():
            raise RuntimeError("Failed to create equity curve.")
        return self.output_file

    def export(self, asset_history: pd.DataFrame) -> Path:
        return self.create(asset_history)

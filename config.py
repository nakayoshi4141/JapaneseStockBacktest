"""Japanese Stock Backtest - Version 1.0.1"""
from __future__ import annotations

from pathlib import Path


class Config:
    """Project-wide configuration. Trading logic is not implemented here."""

    VERSION: str = "1.0.1 Final"
    DEBUG: bool = True

    # Trading parameters (user-configurable)
    INITIAL_CASH: float = 5_000_000.0
    INITIAL_SHARES: int = 100
    MAX_BUY_COUNT: int = 10  # Total purchases including the initial purchase
    AVERAGING_RATE: float = 0.06
    PROFIT_TARGET: float = 0.03

    # Costs are intentionally not applied in Version 1.0.1.
    COMMISSION: float = 0.0
    TAX_RATE: float = 0.0

    # Input
    CSV_FILE: Path = Path("sample_data") / "7201.csv"
    DATE_COLUMN: str = "日付"
    OPEN_COLUMN: str = "始値"
    HIGH_COLUMN: str = "高値"
    LOW_COLUMN: str = "安値"
    CLOSE_COLUMN: str = "終値"
    REQUIRED_COLUMNS: tuple[str, ...] = (
        DATE_COLUMN, OPEN_COLUMN, HIGH_COLUMN, LOW_COLUMN, CLOSE_COLUMN
    )
    CSV_ENCODINGS: tuple[str, ...] = ("utf-8-sig", "utf-8", "cp932", "shift_jis")

    # Output (fixed names)
    OUTPUT_DIR: Path = Path("output")
    RESULT_FILE: str = "BacktestResult.xlsx"
    TRADE_HISTORY_FILE: str = "trade_history.csv"
    CHART_FILE: str = "equity_curve.png"

    @classmethod
    def create_output_directory(cls) -> Path:
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return cls.OUTPUT_DIR

    @classmethod
    def validate(cls) -> None:
        if cls.INITIAL_CASH <= 0:
            raise ValueError("INITIAL_CASH must be greater than zero.")
        if cls.INITIAL_SHARES <= 0:
            raise ValueError("INITIAL_SHARES must be greater than zero.")
        if cls.MAX_BUY_COUNT <= 0:
            raise ValueError("MAX_BUY_COUNT must be greater than zero.")
        if not 0 < cls.AVERAGING_RATE < 1:
            raise ValueError("AVERAGING_RATE must be between 0 and 1.")
        if not 0 < cls.PROFIT_TARGET < 1:
            raise ValueError("PROFIT_TARGET must be between 0 and 1.")
        if cls.COMMISSION < 0:
            raise ValueError("COMMISSION cannot be negative.")
        if cls.TAX_RATE < 0:
            raise ValueError("TAX_RATE cannot be negative.")

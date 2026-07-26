"""
Japanese Stock Backtest
Version : 1.0.0

main.py

バックテスト実行メイン
"""

from __future__ import annotations

from config import Config
from trade_engine import TradeEngine
from statistics import BacktestStatistics
from excel_writer import ExcelWriter
from chart import EquityChart


def run_backtest() -> None:
    """
    バックテスト実行
    """

    print("=" * 50)
    print("Japanese Stock Backtest")
    print("Version 1.0.0")
    print("=" * 50)


    # --------------------------------------------------
    # Output directory
    # --------------------------------------------------

    Config.create_output_directory()


    # --------------------------------------------------
    # Backtest Engine
    # --------------------------------------------------

    engine = TradeEngine()


    print("Loading CSV...")

    engine.load_csv()

    engine.validate_data()


    print("Running backtest...")

    engine.run()


    # --------------------------------------------------
    # Data
    # --------------------------------------------------

    trade_history = (
        engine.get_trade_history_df()
    )

    asset_history = (
        engine.get_asset_history_df()
    )


    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    statistics = BacktestStatistics(
        asset_history=asset_history,
        trade_history=trade_history
    )


    summary = (
        statistics.summary_dataframe()
    )


    yearly_result = (
        statistics.yearly_profit()
    )


    # --------------------------------------------------
    # Excel
    # --------------------------------------------------

    print("Creating Excel...")

    writer = ExcelWriter()

    excel_file = writer.export(
        trade_history=trade_history,
        asset_history=asset_history,
        statistics=summary,
        yearly_result=yearly_result
    )


    # --------------------------------------------------
    # Chart
    # --------------------------------------------------

    print("Creating chart...")

    chart = EquityChart()

    chart_file = chart.export(
        asset_history
    )


    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    result = (
        statistics.summary()
    )


    print("")
    print("=" * 50)
    print("Backtest Completed")
    print("=" * 50)

    print(
        f"Initial Assets : "
        f"{result['Initial Assets']:,.0f} JPY"
    )

    print(
        f"Final Assets   : "
        f"{result['Final Assets']:,.0f} JPY"
    )

    print(
        f"Profit         : "
        f"{result['Total Profit']:,.0f} JPY"
    )

    print(
        f"Return Rate    : "
        f"{result['Return Rate']:.2%}"
    )

    print(
        f"Trade Count    : "
        f"{result['Trade Count']}"
    )

    print("")
    print("Output Files")
    print(
        excel_file
    )

    print(
        chart_file
    )


if __name__ == "__main__":

    run_backtest()

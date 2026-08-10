"""Japanese Stock Backtest - Version 1.0.1 entry point."""
from __future__ import annotations

from config import Config
from trade_engine import TradeEngine
from statistics import BacktestStatistics
from excel_writer import ExcelWriter
from chart import EquityChart


def run_backtest() -> dict[str, object]:
    Config.validate()
    Config.create_output_directory()
    print("=" * 60)
    print(f"Japanese Stock Backtest Version {Config.VERSION}")
    print("=" * 60)

    engine = TradeEngine()
    print("Loading CSV...")
    engine.load_csv()
    engine.validate_data()
    print(f"Rows: {len(engine.data):,}")
    print("Running backtest...")
    engine.run()

    trade_history = engine.get_trade_history_df()
    asset_history = engine.get_asset_history_df()
    stats = BacktestStatistics(asset_history, trade_history)
    summary = stats.summary_dataframe()
    yearly = stats.yearly_profit()

    writer = ExcelWriter()
    excel_file = writer.export(trade_history, asset_history, summary, yearly)
    trade_csv = writer.export_trade_history_csv(trade_history)
    chart_file = EquityChart().export(asset_history)

    result = stats.summary()
    print("=" * 60)
    print("Backtest Completed")
    print("=" * 60)
    print(f"Initial Assets : {result['Initial Assets']:,.0f} JPY")
    print(f"Final Assets   : {result['Final Assets']:,.0f} JPY")
    print(f"Total Profit   : {result['Total Profit']:,.0f} JPY")
    print(f"Return Rate    : {result['Return Rate']:.2%}")
    print(f"Sell Count     : {result['Sell Count']}")
    print(f"Win Rate       : {result['Win Rate']:.2%}")
    print(f"Max Drawdown   : {result['Max Drawdown']:.2%}")
    print(f"CAGR           : {result['CAGR']:.2%}")
    print("Output Files")
    print(excel_file)
    print(trade_csv)
    print(chart_file)
    return {"summary": result, "excel": excel_file, "trade_csv": trade_csv, "chart": chart_file}


if __name__ == "__main__":
    run_backtest()

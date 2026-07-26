"""
Japanese Stock Backtest

Version : 1.0.0 Final

config.py

バックテスト設定

Target:
日産自動車 (7201)

"""


from pathlib import Path



class Config:
    """
    Backtest Configuration
    """


    # =================================================
    # File Settings
    # =================================================


    CSV_FILE = (
        "sample_data/7201.csv"
    )


    OUTPUT_DIR = (
        "output"
    )



    # =================================================
    # Capital Settings
    # =================================================


    # 初期資金

    INITIAL_CASH = (
        5_000_000
    )



    # =================================================
    # Trading Rules
    # =================================================


    # 初回購入株数

    INITIAL_SHARES = (
        100
    )



    # ナンピン最大回数

    MAX_AVERAGE_DOWN_COUNT = (
        10
    )



    # ナンピン条件

    # 直前購入価格から6%下落

    AVERAGE_DOWN_RATE = (
        0.06
    )



    # 利益確定条件

    # 平均取得単価 +3%

    PROFIT_TARGET = (
        0.03
    )



    # =================================================
    # CSV Column Settings
    # =================================================


    DATE_COLUMN = (
        "日付"
    )


    OPEN_COLUMN = (
        "始値"
    )


    HIGH_COLUMN = (
        "高値"
    )


    LOW_COLUMN = (
        "安値"
    )


    CLOSE_COLUMN = (
        "終値"
    )



    REQUIRED_COLUMNS = [

        DATE_COLUMN,

        OPEN_COLUMN,

        HIGH_COLUMN,

        LOW_COLUMN,

        CLOSE_COLUMN

    ]



    # =================================================
    # Output Files
    # =================================================


    TRADE_HISTORY_FILE = (
        "trade_history.xlsx"
    )


    RESULT_FILE = (
        "BacktestResult.xlsx"
    )


    CHART_FILE = (
        "equity_curve.png"
    )



    # =================================================
    # Debug
    # =================================================


    DEBUG = True



    # =================================================
    # Utility
    # =================================================


    @classmethod
    def create_output_directory(cls):
        """
        出力フォルダ作成
        """

        Path(
            cls.OUTPUT_DIR
        ).mkdir(

            exist_ok=True

        )

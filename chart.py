"""
Japanese Stock Backtest
Version : 1.0.0

chart.py

資産推移グラフ作成
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from config import Config


class EquityChart:
    """
    資産推移グラフ作成クラス
    """

    def __init__(
        self,
        output_file: Path = Config.CHART_FILE
    ):

        self.output_file = output_file


    # =====================================================
    # Create
    # =====================================================

    def create(
        self,
        asset_history: pd.DataFrame
    ) -> None:
        """
        資産推移グラフ作成
        """

        if asset_history.empty:
            raise ValueError(
                "資産履歴がありません"
            )


        Config.create_output_directory()


        df = asset_history.copy()


        df["Date"] = pd.to_datetime(
            df["Date"]
        )


        plt.figure(
            figsize=(12, 6)
        )


        plt.plot(
            df["Date"],
            df["TotalAssets"],
            label="Total Assets"
        )


        plt.title(
            "Nissan 7201 Backtest Equity Curve"
        )


        plt.xlabel(
            "Date"
        )


        plt.ylabel(
            "Assets (JPY)"
        )


        plt.grid(
            True
        )


        plt.legend()


        plt.tight_layout()


        plt.savefig(
            self.output_file,
            dpi=300
        )


        plt.close()

    # =====================================================
    # Validation
    # =====================================================

    def validate(
        self,
        asset_history: pd.DataFrame
    ) -> None:
        """
        資産データ検証
        """

        required_columns = [
            "Date",
            "TotalAssets"
        ]

        missing = [
            col
            for col in required_columns
            if col not in asset_history.columns
        ]

        if missing:

            raise ValueError(
                f"必要列がありません: {missing}"
            )


    # =====================================================
    # Export
    # =====================================================

    def export(
        self,
        asset_history: pd.DataFrame
    ) -> Path:
        """
        グラフ出力
        """

        self.validate(
            asset_history
        )

        self.create(
            asset_history
        )

        if not self.output_file.exists():

            raise RuntimeError(
                "グラフファイル作成に失敗しました"
            )

        return self.output_file

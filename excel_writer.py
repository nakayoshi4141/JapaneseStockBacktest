"""
Japanese Stock Backtest
Version : 1.0.0

excel_writer.py

Excel出力処理
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import Config


class ExcelWriter:
    """
    バックテスト結果Excel出力クラス
    """

    def __init__(
        self,
        output_file: Path = Config.EXCEL_FILE
    ):

        self.output_file = output_file


    # =====================================================
    # Save
    # =====================================================

    def save(
        self,
        trade_history: pd.DataFrame,
        asset_history: pd.DataFrame,
        statistics: pd.DataFrame,
        yearly_result: pd.DataFrame
    ) -> None:
        """
        Excel保存
        """

        Config.create_output_directory()

        with pd.ExcelWriter(
            self.output_file,
            engine="openpyxl"
        ) as writer:

            self.write_sheet(
                writer,
                trade_history,
                "TradeHistory"
            )

            self.write_sheet(
                writer,
                asset_history,
                "AssetHistory"
            )

            self.write_sheet(
                writer,
                statistics,
                "Statistics"
            )

            self.write_sheet(
                writer,
                yearly_result,
                "YearlyResult"
            )


    # =====================================================
    # Sheet
    # =====================================================

    def write_sheet(
        self,
        writer,
        dataframe: pd.DataFrame,
        sheet_name: str
    ) -> None:
        """
        DataFrame書込
        """

        dataframe.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False
        )
    # =====================================================
    # Format
    # =====================================================

    def format_excel(
        self
    ) -> None:
        """
        Excel書式調整

        pandas出力後のExcelを
        openpyxlで整形する
        """

        from openpyxl import load_workbook
        from openpyxl.styles import Font
        from openpyxl.utils import get_column_letter


        workbook = load_workbook(
            self.output_file
        )


        for worksheet in workbook.worksheets:

            # -----------------------------
            # Header
            # -----------------------------

            for cell in worksheet[1]:

                cell.font = Font(
                    bold=True
                )


            # -----------------------------
            # Column Width
            # -----------------------------

            for column_cells in worksheet.columns:

                max_length = 0

                column_letter = (
                    get_column_letter(
                        column_cells[0].column
                    )
                )

                for cell in column_cells:

                    if cell.value is not None:

                        length = len(
                            str(cell.value)
                        )

                        if length > max_length:
                            max_length = length


                worksheet.column_dimensions[
                    column_letter
                ].width = (
                    max_length + 3
                )


        workbook.save(
            self.output_file
        )


    # =====================================================
    # Export
    # =====================================================

    def export(
        self,
        trade_history: pd.DataFrame,
        asset_history: pd.DataFrame,
        statistics: pd.DataFrame,
        yearly_result: pd.DataFrame
    ) -> Path:
        """
        Excel出力実行
        """

        self.save(
            trade_history,
            asset_history,
            statistics,
            yearly_result
        )

        self.format_excel()

        return self.output_file      

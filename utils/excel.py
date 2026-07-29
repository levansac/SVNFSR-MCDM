from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


def load_pipeline_excel(
    excel_file,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load a complete SVNFSR workbook.

    Required sheets:
        Matrix
        Criteria
    """
    workbook = pd.ExcelFile(
        excel_file,
        engine="openpyxl",
    )

    normalized_names = {
        name.strip().lower(): name
        for name in workbook.sheet_names
    }

    matrix_sheet = normalized_names.get("matrix")
    criteria_sheet = normalized_names.get("criteria")

    if matrix_sheet is None:
        raise ValueError(
            "The workbook does not contain a sheet named 'Matrix'."
        )

    if criteria_sheet is None:
        raise ValueError(
            "The workbook does not contain a sheet named 'Criteria'."
        )

    matrix = pd.read_excel(
        workbook,
        sheet_name=matrix_sheet,
    )

    criterion_data = pd.read_excel(
        workbook,
        sheet_name=criteria_sheet,
    )

    return matrix, criterion_data


def export_pipeline_to_excel(
    *,
    input_matrix: pd.DataFrame,
    criterion_input: pd.DataFrame,
    weights: pd.DataFrame,
    weighted_matrix: pd.DataFrame,
    relation_matrix: pd.DataFrame,
    detail: pd.DataFrame,
    ranking: pd.DataFrame,
) -> bytes:
    """
    Export all pipeline stages into one Excel workbook.
    """
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        input_matrix.to_excel(
            writer,
            sheet_name="Input Matrix",
            index=False,
        )

        criterion_input.to_excel(
            writer,
            sheet_name="Criterion Input",
            index=False,
        )

        weights.to_excel(
            writer,
            sheet_name="Criterion Weights",
            index=False,
        )

        weighted_matrix.to_excel(
            writer,
            sheet_name="Weighted Matrix",
            index=False,
        )

        relation_matrix.to_excel(
            writer,
            sheet_name="Relation R",
            index=False,
        )

        detail.to_excel(
            writer,
            sheet_name="Score and Dominance",
            index=False,
        )

        ranking.to_excel(
            writer,
            sheet_name="Final Ranking",
            index=False,
        )

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = (
                worksheet.dimensions
            )

            for column_cells in worksheet.columns:
                maximum_length = 0

                for cell in column_cells:
                    value = (
                        ""
                        if cell.value is None
                        else str(cell.value)
                    )
                    maximum_length = max(
                        maximum_length,
                        len(value),
                    )

                column_letter = (
                    column_cells[0].column_letter
                )

                worksheet.column_dimensions[
                    column_letter
                ].width = min(
                    maximum_length + 2,
                    40,
                )

    output.seek(0)
    return output.getvalue()


def dataframe_to_excel(
    data: pd.DataFrame,
    sheet_name: str = "Results",
) -> bytes:
    """
    Backward-compatible single-table exporter.
    """
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        data.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
        )

    output.seek(0)
    return output.getvalue()

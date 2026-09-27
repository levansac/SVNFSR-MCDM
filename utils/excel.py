from __future__ import annotations

from io import BytesIO
import pandas as pd


def load_pipeline_excel(excel_file) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """
    Đọc workbook đầu vào SVNFSR.

    Bắt buộc:
      - Matrix: Alternative, C1, C2, ...; mỗi ô (T, I, F, μ).

    Tùy chọn:
      - Weights: Criterion, Weight.

    Nếu có Weights, pipeline sẽ dùng trực tiếp các trọng số được cung cấp.
    Nếu không có Weights, E(cj), C(cj), wj được tính tự động từ Matrix.
    """
    workbook = pd.ExcelFile(excel_file, engine="openpyxl")
    names = {name.strip().lower(): name for name in workbook.sheet_names}

    matrix_sheet = names.get("matrix")
    if matrix_sheet is None:
        raise ValueError("Tệp Excel không có trang tính tên 'Matrix'.")

    matrix = pd.read_excel(workbook, sheet_name=matrix_sheet)
    weights = None

    weights_sheet = names.get("weights")
    if weights_sheet is not None:
        weights = pd.read_excel(workbook, sheet_name=weights_sheet)
        weights.columns = [str(c).strip() for c in weights.columns]

        # Chấp nhận cả tên cột tiếng Anh và tiếng Việt để thuận tiện sử dụng.
        rename_map = {}
        for col in weights.columns:
            key = col.strip().lower()
            if key in {"criterion", "tiêu chí", "tieu chi"}:
                rename_map[col] = "Criterion"
            elif key in {"weight", "trọng số", "trong so"}:
                rename_map[col] = "Weight"
        weights = weights.rename(columns=rename_map)

        required = {"Criterion", "Weight"}
        missing = required.difference(weights.columns)
        if missing:
            raise ValueError(
                "Trang tính 'Weights' phải có hai cột: Criterion và Weight."
            )

        weights = weights[["Criterion", "Weight"]].copy()
        weights["Criterion"] = weights["Criterion"].astype(str).str.strip()
        weights["Weight"] = pd.to_numeric(weights["Weight"], errors="raise")

        if weights["Criterion"].eq("").any():
            raise ValueError("Tên tiêu chí trong trang 'Weights' không được để trống.")
        if weights["Criterion"].duplicated().any():
            raise ValueError("Trang 'Weights' có tiêu chí bị trùng.")
        if (weights["Weight"] <= 0).any():
            raise ValueError("Mọi trọng số trong trang 'Weights' phải lớn hơn 0.")
        if abs(float(weights["Weight"].sum()) - 1.0) > 1e-6:
            raise ValueError(
                "Tổng trọng số trong trang 'Weights' phải bằng 1. "
                f"Hiện tại = {weights['Weight'].sum():.8f}."
            )

    return matrix, weights


def export_pipeline_to_excel(
    *, input_matrix: pd.DataFrame, weights: pd.DataFrame,
    weighted_matrix: pd.DataFrame, relation_matrix: pd.DataFrame,
    detail: pd.DataFrame, ranking: pd.DataFrame,
) -> bytes:
    """Xuất toàn bộ các bước tính toán ra một workbook Excel."""
    output = BytesIO()
    input_export = input_matrix.rename(columns={"Alternative": "Phương án"})
    weights_export = weights.rename(columns={
        "Criterion": "Tiêu chí", "Weight Numerator": "Tử số trọng số",
        "Weight": "Trọng số", "Weight Source": "Nguồn trọng số",
    })
    weighted_export = weighted_matrix.rename(columns={"Alternative": "Phương án", "Criterion": "Tiêu chí"})
    relation_export = relation_matrix.rename(columns={
        "Alternative": "Phương án", "Criterion": "Tiêu chí",
        "Criterion 1": "Tiêu chí 1", "Criterion 2": "Tiêu chí 2", "Relation": "Quan hệ",
    })
    detail_export = detail.rename(columns={
        "Alternative": "Phương án", "Criterion": "Tiêu chí", "Relation": "Quan hệ",
        "Normalized μ": "μ chuẩn hóa", "Dominant Score": "Điểm chi phối",
    })
    ranking_export = ranking.rename(columns={
        "Alternative": "Phương án", "Overall Score": "Điểm tổng thể", "Rank": "Xếp hạng",
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        input_export.to_excel(writer, sheet_name="Du lieu dau vao", index=False)
        weights_export.to_excel(writer, sheet_name="Trong so tieu chi", index=False)
        weighted_export.to_excel(writer, sheet_name="Ma tran co trong so", index=False)
        relation_export.to_excel(writer, sheet_name="Quan he R", index=False)
        detail_export.to_excel(writer, sheet_name="Diem va chi phoi", index=False)
        ranking_export.to_excel(writer, sheet_name="Xep hang cuoi", index=False)
        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for cells in worksheet.columns:
                max_len = max(len("" if c.value is None else str(c.value)) for c in cells)
                worksheet.column_dimensions[cells[0].column_letter].width = min(max_len + 2, 40)
    output.seek(0)
    return output.getvalue()


def dataframe_to_excel(data: pd.DataFrame, sheet_name: str = "Ket qua") -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output.getvalue()

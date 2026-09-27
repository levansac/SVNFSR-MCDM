from __future__ import annotations
import pandas as pd


def validate_input_data(data: pd.DataFrame) -> list[str]:
    errors = []
    required = {"Alternative", "Criterion", "T", "I", "F", "μ"}
    missing = required.difference(data.columns)
    if missing:
        return ["Thiếu các cột bắt buộc: " + ", ".join(sorted(missing))]
    if data.empty:
        return ["Dữ liệu đầu vào không được để trống."]

    alternatives = data["Alternative"].astype(str).str.strip()
    criteria = data["Criterion"].astype(str).str.strip()

    if alternatives.eq("").any():
        errors.append("Tên phương án không được để trống.")
    if criteria.eq("").any():
        errors.append("Tên tiêu chí không được để trống.")

    pairs = pd.DataFrame({"Alternative": alternatives, "Criterion": criteria})
    if pairs.duplicated().any():
        errors.append("Mỗi cặp (phương án, tiêu chí) phải là duy nhất.")

    for column in ["T", "I", "F", "μ"]:
        values = pd.to_numeric(data[column], errors="coerce")
        if values.isna().any() or ((values < 0) | (values > 1)).any():
            errors.append(f"Giá trị {column} phải là số và thuộc khoảng [0, 1].")

    criterion_sets = pairs.groupby("Alternative")["Criterion"].apply(frozenset)
    if len(criterion_sets) > 1:
        reference = criterion_sets.iloc[0]
        if not criterion_sets.apply(lambda value: value == reference).all():
            errors.append("Tất cả phương án phải sử dụng cùng một tập tiêu chí.")
    return errors


def validate_parameters(alpha: float, beta: float, gamma: float) -> list[str]:
    errors = []
    if alpha <= 0 or beta <= 0 or gamma <= 0:
        errors.append("α, β và γ phải lớn hơn 0.")
    if abs(alpha + beta + gamma - 1.0) > 1e-9:
        errors.append(f"α + β + γ phải bằng 1 (hiện tại: {alpha+beta+gamma:.4f}).")
    return errors

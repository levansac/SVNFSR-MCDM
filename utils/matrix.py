from __future__ import annotations

import re
import pandas as pd


CELL_PATTERN = re.compile(
    r"^\s*[\(\[]?\s*"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*,\s*"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*,\s*"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*,\s*"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*"
    r"[\)\]]?\s*$"
)


def format_cell(T: float, I: float, F: float, mu: float) -> str:
    """Return the canonical SVNFSR input representation."""
    return f"({T:.2f}, {I:.2f}, {F:.2f}, {mu:.2f})"


def parse_svnfsr_cell(value) -> tuple[float, float, float, float]:
    """
    Parse one matrix cell in the NEW format:
        (T, I, F, μ)

    Example:
        (0.7, 0.4, 0.6, 0.94)
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise ValueError("Ô dữ liệu đang trống. Định dạng yêu cầu: (T, I, F, μ).")

    text = str(value).strip()
    match = CELL_PATTERN.fullmatch(text)
    if not match:
        raise ValueError(
            f"Giá trị '{text}' không hợp lệ. Định dạng yêu cầu: (T, I, F, μ), "
            "ví dụ (0.70, 0.40, 0.60, 0.94)."
        )

    T, I, F, mu = (float(x) for x in match.groups())

    for name, number in (("T", T), ("I", I), ("F", F), ("μ", mu)):
        if not 0.0 <= number <= 1.0:
            raise ValueError(
                f"{name}={number} nằm ngoài khoảng [0, 1] trong ô '{text}'."
            )

    return T, I, F, mu


def create_default_matrix(
    number_of_alternatives: int,
    number_of_criteria: int,
) -> pd.DataFrame:
    """Create an editable matrix using the new 4-tuple cell format."""
    columns = ["Alternative"] + [
        f"C{j}" for j in range(1, number_of_criteria + 1)
    ]

    rows = []
    for i in range(1, number_of_alternatives + 1):
        row = {"Alternative": f"u{i}"}
        for j in range(1, number_of_criteria + 1):
            row[f"C{j}"] = "(0.50, 0.50, 0.50, 1.00)"
        rows.append(row)

    return pd.DataFrame(rows, columns=columns)


def matrix_to_long(matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Convert:
        Alternative | C1 | C2 | ...
        u1          | (T,I,F,μ) | ...

    to:
        Alternative | Criterion | T | I | F | μ
    """
    if matrix is None or matrix.empty:
        raise ValueError("Ma trận SVNFS đang trống.")

    if "Alternative" not in matrix.columns:
        raise ValueError("Trang tính Matrix phải có cột 'Alternative'.")

    criterion_columns = [
        str(col) for col in matrix.columns if str(col) != "Alternative"
    ]
    if not criterion_columns:
        raise ValueError("Ma trận SVNFS phải có ít nhất một tiêu chí.")

    alternatives = matrix["Alternative"].astype(str).str.strip()

    if alternatives.eq("").any():
        raise ValueError("Tên phương án không được để trống.")

    duplicated = alternatives[alternatives.duplicated()].unique().tolist()
    if duplicated:
        raise ValueError(
            "Tên phương án phải là duy nhất. Bị trùng: "
            + ", ".join(duplicated)
        )

    records: list[dict] = []

    for row_index, row in matrix.iterrows():
        alternative = str(row["Alternative"]).strip()

        for criterion in criterion_columns:
            try:
                T, I, F, mu = parse_svnfsr_cell(row[criterion])
            except ValueError as error:
                raise ValueError(
                    f"{alternative} / {criterion}: {error}"
                ) from error

            records.append(
                {
                    "Alternative": alternative,
                    "Criterion": criterion,
                    "T": T,
                    "I": I,
                    "F": F,
                    "μ": mu,
                }
            )

    return pd.DataFrame(
        records,
        columns=["Alternative", "Criterion", "T", "I", "F", "μ"],
    )

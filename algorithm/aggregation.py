import pandas as pd


def prepare_numeric_data(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert T, I, F and μ columns to numeric values.

    This function will later contain the SVNFSR
    relation aggregation process.
    """
    prepared_data = data.copy()

    numeric_columns = ["T", "I", "F", "μ"]

    for column in numeric_columns:
        prepared_data[column] = pd.to_numeric(
            prepared_data[column],
            errors="coerce",
        )

    return prepared_data


def aggregate_svnfsr_values(
    first_value: tuple[float, float, float],
    second_value: tuple[float, float, float],
) -> tuple[float, float, float]:
    """
    Aggregate two SVNFSR values using:

        T = min(T1, T2)
        I = max(I1, I2)
        F = max(F1, F2)
    """
    truth_1, indeterminacy_1, falsity_1 = first_value
    truth_2, indeterminacy_2, falsity_2 = second_value

    aggregated_truth = min(truth_1, truth_2)
    aggregated_indeterminacy = max(
        indeterminacy_1,
        indeterminacy_2,
    )
    aggregated_falsity = max(
        falsity_1,
        falsity_2,
    )

    return (
        aggregated_truth,
        aggregated_indeterminacy,
        aggregated_falsity,
    )
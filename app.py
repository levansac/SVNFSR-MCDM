from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from algorithm import run_svnfsr
from components import (
    render_footer,
    render_header,
    render_parameter_intro,
    render_parameter_status,
    render_result_banner,
    render_section_header,
)
from styles import get_custom_css
from utils.excel import (
    export_pipeline_to_excel,
    load_pipeline_excel,
)
from utils.matrix import create_default_matrix, matrix_to_long
from utils.validator import (
    validate_criterion_data,
    validate_input_data,
    validate_parameters,
)


PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_FILE = PROJECT_ROOT / "sample" / "sample_pipeline.xlsx"

st.set_page_config(
    page_title="SVNFSR-MCDM Online Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(get_custom_css(), unsafe_allow_html=True)


def clear_result() -> None:
    st.session_state.pop("algorithm_result", None)


def set_project_data(
    matrix: pd.DataFrame,
    criterion_data: pd.DataFrame,
) -> None:
    st.session_state["input_matrix"] = matrix.copy()
    st.session_state["criterion_data"] = criterion_data.copy()
    st.session_state["editor_version"] = (
        st.session_state.get("editor_version", 0) + 1
    )
    clear_result()


def create_default_criterion_data(
    number_of_criteria: int,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Criterion": [
                f"C{index + 1}"
                for index in range(number_of_criteria)
            ],
            "E": [0.0] * number_of_criteria,
            "C": [0.0] * number_of_criteria,
        }
    )


def reset_project(
    number_of_alternatives: int,
    number_of_criteria: int,
) -> None:
    set_project_data(
        matrix=create_default_matrix(
            number_of_alternatives,
            number_of_criteria,
        ),
        criterion_data=create_default_criterion_data(
            number_of_criteria
        ),
    )


def display_error_list(errors: list[str]) -> None:
    st.error(
        "Input data is invalid:\n\n"
        + "\n".join(
            f"• {error}"
            for error in errors
        )
    )


render_header()

# =========================================================
# 1. IMPORT AND PROBLEM CONFIGURATION
# =========================================================
with st.container(border=True):
    render_section_header(
        1,
        "Import Input Data",
        (
            "Upload one Excel workbook containing the SVNFS matrix "
            "and criterion information, or load the built-in sample."
        ),
    )

    upload_column, sample_column = st.columns(
        2,
        gap="large",
    )

    with upload_column:
        uploaded_file = st.file_uploader(
            "Upload pipeline input (.xlsx)",
            type=["xlsx"],
            help=(
                "The workbook should contain sheets named Matrix and Criteria."
            ),
        )

        st.info(
            "Required workbook structure:\n\n"
            "- **Matrix**: Alternative, C1, C2, …\n"
            "- **Criteria**: Criterion, E, C\n\n"
            "Each matrix cell uses `(T, I, F) / μ`."
        )

    with sample_column:
        st.markdown(
            """
            <div class="sample-card">
                <div class="sample-card-title">
                    📘 Built-in sample workbook
                </div>
                <div class="sample-card-text">
                    Load a complete 5 × 6 SVNFS example with
                    criterion information.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        load_sample_clicked = st.button(
            "Load Sample Workbook",
            use_container_width=True,
        )

    configuration_column_1, configuration_column_2 = st.columns(
        2,
        gap="large",
    )

    with configuration_column_1:
        number_of_alternatives = st.number_input(
            "Number of alternatives",
            min_value=2,
            max_value=50,
            value=5,
            step=1,
        )

    with configuration_column_2:
        number_of_criteria = st.number_input(
            "Number of criteria",
            min_value=2,
            max_value=20,
            value=6,
            step=1,
        )


if "input_matrix" not in st.session_state:
    reset_project(
        int(number_of_alternatives),
        int(number_of_criteria),
    )


if uploaded_file is not None:
    uploaded_signature = (
        f"{uploaded_file.name}:{uploaded_file.size}"
    )

    if (
        st.session_state.get("uploaded_signature")
        != uploaded_signature
    ):
        try:
            imported_matrix, imported_criteria = (
                load_pipeline_excel(uploaded_file)
            )

            set_project_data(
                imported_matrix,
                imported_criteria,
            )

            st.session_state[
                "uploaded_signature"
            ] = uploaded_signature

            st.success(
                "The input workbook was imported successfully."
            )
        except Exception as error:
            st.error(
                f"Unable to import the workbook: {error}"
            )


if load_sample_clicked:
    try:
        sample_matrix, sample_criteria = (
            load_pipeline_excel(SAMPLE_FILE)
        )

        set_project_data(
            sample_matrix,
            sample_criteria,
        )

        st.success(
            "The sample workbook was loaded successfully."
        )
    except Exception as error:
        st.error(
            f"Unable to load the sample workbook: {error}"
        )


expected_shape = (
    int(number_of_alternatives),
    int(number_of_criteria) + 1,
)

if (
    uploaded_file is None
    and not load_sample_clicked
    and st.session_state["input_matrix"].shape
    != expected_shape
):
    reset_project(
        int(number_of_alternatives),
        int(number_of_criteria),
    )


# =========================================================
# 2. CRITERION WEIGHTS
# =========================================================
with st.container(border=True):
    render_section_header(
        2,
        "Step 1 — Criterion Weights",
        (
            "Enter E(cj) and C(cj). The system calculates criterion "
            "weights and applies them to the input SVNFS matrix."
        ),
    )

    st.latex(
        r"""
        w_j=
        \frac{1-E(c_j)+C(c_j)}
        {\sum_{q=1}^{m}[1-E(c_q)+C(c_q)]}
        """
    )

    criterion_editor_key = (
        "criterion_editor_"
        f"{st.session_state.get('editor_version', 0)}"
    )

    criterion_data = st.data_editor(
        st.session_state["criterion_data"],
        key=criterion_editor_key,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Criterion": st.column_config.TextColumn(
                "Criterion",
                disabled=True,
            ),
            "E": st.column_config.NumberColumn(
                "E(cj)",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                format="%.4f",
                required=True,
            ),
            "C": st.column_config.NumberColumn(
                "C(cj)",
                min_value=0.0,
                step=0.01,
                format="%.4f",
                required=True,
            ),
        },
    )

    st.session_state["criterion_data"] = criterion_data

    st.caption(
        "When all E and C values are zero, all criteria receive equal weights."
    )


# =========================================================
# 3. SCORING PARAMETERS
# =========================================================
with st.container(border=True):
    render_section_header(
        3,
        "Scoring Parameters",
        "Set α, β and γ subject to α + β + γ = 1.",
    )

    alpha_column, beta_column, gamma_column = st.columns(3)

    with alpha_column:
        render_parameter_intro(
            "Alpha",
            "α",
            "Influence of truth-membership T.",
        )
        alpha = st.number_input(
            "Alpha",
            min_value=0.01,
            max_value=0.98,
            value=0.20,
            step=0.01,
            format="%.2f",
            label_visibility="collapsed",
        )

    with beta_column:
        render_parameter_intro(
            "Beta",
            "β",
            "Influence of benefit value 1 − I.",
        )
        beta = st.number_input(
            "Beta",
            min_value=0.01,
            max_value=0.98,
            value=0.40,
            step=0.01,
            format="%.2f",
            label_visibility="collapsed",
        )

    with gamma_column:
        render_parameter_intro(
            "Gamma",
            "γ",
            "Influence of benefit value 1 − F.",
        )
        gamma = st.number_input(
            "Gamma",
            min_value=0.01,
            max_value=0.98,
            value=0.40,
            step=0.01,
            format="%.2f",
            label_visibility="collapsed",
        )

    render_parameter_status(
        alpha,
        beta,
        gamma,
    )


# =========================================================
# 4. SVNFS MATRIX
# =========================================================
with st.container(border=True):
    render_section_header(
        4,
        "SVNFS Evaluation Matrix",
        (
            "Rows represent alternatives, columns represent criteria, "
            "and every cell has the form (T, I, F) / μ."
        ),
    )

    st.latex(
        r"""
        x_{ij}
        =
        \frac{(T_{ij},I_{ij},F_{ij})}
        {\mu_{ij}}
        """
    )

    matrix_editor_key = (
        "matrix_editor_"
        f"{st.session_state.get('editor_version', 0)}"
    )

    matrix = st.data_editor(
        st.session_state["input_matrix"],
        key=matrix_editor_key,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
    )

    st.session_state["input_matrix"] = matrix

    show_parsed_data = st.checkbox(
        "Show parsed T, I, F and μ values",
        value=False,
    )

    if show_parsed_data:
        try:
            parsed_preview = matrix_to_long(matrix)
            st.dataframe(
                parsed_preview,
                use_container_width=True,
                hide_index=True,
            )
        except Exception as error:
            st.warning(str(error))

    run_column, reset_column = st.columns(
        [3, 1]
    )

    with run_column:
        run_clicked = st.button(
            "▶ Run Full SVNFSR-MCDM Pipeline",
            type="primary",
            use_container_width=True,
        )

    with reset_column:
        reset_clicked = st.button(
            "↻ Reset Project",
            use_container_width=True,
        )

    if reset_clicked:
        reset_project(
            int(number_of_alternatives),
            int(number_of_criteria),
        )
        st.rerun()


# =========================================================
# EXECUTE PIPELINE
# =========================================================
if run_clicked:
    validation_errors: list[str] = []

    try:
        long_data = matrix_to_long(matrix)
    except Exception as error:
        long_data = pd.DataFrame()
        validation_errors.append(str(error))

    if not long_data.empty:
        validation_errors.extend(
            validate_input_data(long_data)
        )

        expected_criteria = (
            long_data["Criterion"]
            .drop_duplicates()
            .astype(str)
            .tolist()
        )

        validation_errors.extend(
            validate_criterion_data(
                criterion_data,
                expected_criteria,
            )
        )

    validation_errors.extend(
        validate_parameters(
            alpha,
            beta,
            gamma,
        )
    )

    if validation_errors:
        display_error_list(validation_errors)
    else:
        try:
            result = run_svnfsr(
                data=long_data,
                criterion_data=criterion_data,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
            )

            result["input_matrix"] = matrix.copy()
            result["criterion_input"] = (
                criterion_data.copy()
            )

            st.session_state[
                "algorithm_result"
            ] = result

            st.success(
                "The full SVNFSR-MCDM pipeline was executed successfully."
            )
        except Exception as error:
            st.error(
                f"Unable to execute the pipeline: {error}"
            )


# =========================================================
# 5. VISUAL RESULTS
# =========================================================
if "algorithm_result" in st.session_state:
    result = st.session_state["algorithm_result"]
    ranking = result["ranking"]
    weights = result["weights"]
    detail = result["detail"]
    relation_matrix = result["relation_matrix"]

    best_names = ", ".join(
        result["best_alternatives"]
    )

    with st.container(border=True):
        render_section_header(
            5,
            "Visual Results",
            (
                "Explore criterion weights, relation performance, "
                "dominance patterns and the final ranking."
            ),
        )

        metric_1, metric_2, metric_3, metric_4 = st.columns(4)

        metric_1.metric(
            "Best alternative",
            best_names,
        )
        metric_2.metric(
            "Best overall score",
            f'{result["best_score"]:.6f}',
        )
        metric_3.metric(
            "Criterion relations",
            relation_matrix["Relation"].nunique(),
        )
        metric_4.metric(
            "Dominant selections",
            int(detail["δ"].sum()),
        )

        render_result_banner(
            best_names,
            result["best_score"],
        )

        overview_tab, weight_tab, relation_tab, dominance_tab, data_tab = (
            st.tabs(
                [
                    "Overview",
                    "Criterion Weights",
                    "Relation Analysis",
                    "Dominance Analysis",
                    "Detailed Data",
                ]
            )
        )

        with overview_tab:
            overview_left, overview_right = st.columns(
                2,
                gap="large",
            )

            with overview_left:
                st.subheader("Final Ranking")

                st.dataframe(
                    ranking.round(
                        {
                            "Overall Score": 6,
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            with overview_right:
                st.subheader("Overall Score Comparison")

                ranking_chart = (
                    ranking[
                        ["Alternative", "Overall Score"]
                    ]
                    .set_index("Alternative")
                )

                st.bar_chart(
                    ranking_chart,
                    use_container_width=True,
                )

            st.subheader("Dominant Relations by Alternative")

            dominance_count = (
                detail.groupby(
                    "Alternative",
                    as_index=False,
                )["δ"]
                .sum()
                .rename(
                    columns={
                        "δ": "Dominant Relations",
                    }
                )
                .set_index("Alternative")
            )

            st.bar_chart(
                dominance_count,
                use_container_width=True,
            )

        with weight_tab:
            weight_left, weight_right = st.columns(
                [1.2, 1],
                gap="large",
            )

            with weight_left:
                st.subheader("Calculated Criterion Weights")

                st.dataframe(
                    weights.round(
                        {
                            "E": 4,
                            "C": 4,
                            "Weight Numerator": 6,
                            "Weight": 6,
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            with weight_right:
                st.subheader("Weight Distribution")

                weight_chart = (
                    weights[
                        ["Criterion", "Weight"]
                    ]
                    .set_index("Criterion")
                )

                st.bar_chart(
                    weight_chart,
                    use_container_width=True,
                )

            st.metric(
                "Weight sum",
                f'{weights["Weight"].sum():.6f}',
            )

        with relation_tab:
            st.subheader(
                "Mean Evaluation Score by Criterion Relation"
            )

            relation_summary = (
                detail.groupby(
                    "Relation",
                    as_index=False,
                )
                .agg(
                    Mean_V=("V", "mean"),
                    Maximum_V=("V", "max"),
                    Dominance_Count=("δ", "sum"),
                )
                .sort_values(
                    "Mean_V",
                    ascending=False,
                )
            )

            relation_chart = (
                relation_summary[
                    ["Relation", "Mean_V"]
                ]
                .set_index("Relation")
            )

            st.bar_chart(
                relation_chart,
                use_container_width=True,
            )

            st.dataframe(
                relation_summary.round(
                    {
                        "Mean_V": 6,
                        "Maximum_V": 6,
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        with dominance_tab:
            st.subheader(
                "Dominance Matrix"
            )

            dominance_matrix = (
                detail.pivot_table(
                    index="Alternative",
                    columns="Relation",
                    values="δ",
                    aggfunc="max",
                    fill_value=0,
                )
            )

            st.dataframe(
                dominance_matrix.astype(int),
                use_container_width=True,
            )

            st.subheader(
                "Dominant Score Contribution"
            )

            contribution_matrix = (
                detail.pivot_table(
                    index="Alternative",
                    columns="Relation",
                    values="Dominant Score",
                    aggfunc="sum",
                    fill_value=0.0,
                )
            )

            st.dataframe(
                contribution_matrix.round(6),
                use_container_width=True,
            )

        with data_tab:
            weighted_matrix_tab, relation_matrix_tab, score_tab = (
                st.tabs(
                    [
                        "Weighted Matrix",
                        "Relation R",
                        "Score and Dominance",
                    ]
                )
            )

            with weighted_matrix_tab:
                st.dataframe(
                    result["weighted_matrix"].round(6),
                    use_container_width=True,
                    hide_index=True,
                )

            with relation_matrix_tab:
                st.dataframe(
                    relation_matrix.round(
                        {
                            "T": 6,
                            "I": 6,
                            "F": 6,
                            "μ": 6,
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            with score_tab:
                st.dataframe(
                    detail.round(
                        {
                            "T": 6,
                            "I": 6,
                            "F": 6,
                            "μ": 6,
                            "Normalized μ": 6,
                            "V": 6,
                            "Dominant Score": 6,
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

        st.divider()
        st.subheader("Export Complete Results")

        export_file = export_pipeline_to_excel(
            input_matrix=result["input_matrix"],
            criterion_input=result["criterion_input"],
            weights=result["weights"],
            weighted_matrix=result["weighted_matrix"],
            relation_matrix=result["relation_matrix"],
            detail=result["detail"],
            ranking=result["ranking"],
        )

        export_column_1, export_column_2 = st.columns(
            2
        )

        with export_column_1:
            st.download_button(
                "Download Complete Pipeline (Excel)",
                data=export_file,
                file_name=(
                    "svnfsr_full_pipeline_results.xlsx"
                ),
                mime=(
                    "application/vnd."
                    "openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
            )

        with export_column_2:
            ranking_csv = ranking.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "Download Final Ranking (CSV)",
                data=ranking_csv,
                file_name="svnfsr_final_ranking.csv",
                mime="text/csv",
                use_container_width=True,
            )

render_footer()

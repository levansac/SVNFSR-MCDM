"""
===============================================================================
SVNFSR-MCDM - GHI CHÚ BẢO TRÌ FILE app.py
===============================================================================

Vai trò:
- app.py quản lý giao diện Streamlit và điều phối luồng xử lý.
- Công thức/thuật toán chính nên nằm trong algorithm/.
- Đọc và xuất Excel nên nằm trong utils/.

Luồng website:
1) Cấu hình trang.
2) Upload Excel.
3) Parse + kiểm tra dữ liệu.
4) Nhập alpha, beta, gamma.
5) Hiển thị ma trận SVNFS.
6) Chạy pipeline SVNFSR-MCDM.
7) Hiển thị xếp hạng và các bảng tính trung gian.
8) Xuất kết quả Excel.

QUY TẮC QUAN TRỌNG:
- Không đổi tên cột DataFrame nội bộ:
  Alternative, Criterion, Overall Score, Rank, ...
- Chỉ Việt hóa trên bản sao dùng để HIỂN THỊ hoặc XUẤT FILE.
- Giữ nguyên các ký hiệu T, I, F, μ, E(cj), C(cj), wj, α, β, γ.
- Streamlit rerun script sau mỗi tương tác, vì vậy st.session_state được dùng
  để giữ ma trận và kết quả giữa các lần chạy.

===============================================================================
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from algorithm import run_svnfsr
from components import (
    render_footer,
    render_header,
    render_section_header,
)
from styles import get_custom_css
from utils.excel import (
    export_pipeline_to_excel,
    load_pipeline_excel,
)
from utils.matrix import create_default_matrix, matrix_to_long
from utils.validator import (
    validate_input_data,
    validate_parameters,
)



# =============================================================================
# 1. CẤU HÌNH TRANG
# Thiết lập title/icon/layout. Không ảnh hưởng đến phép tính của thuật toán.
# =============================================================================
st.set_page_config(
    page_title="SVNFSR-MCDM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(get_custom_css(), unsafe_allow_html=True)


def clear_result() -> None:
    st.session_state.pop("algorithm_result", None)


def set_project_data(matrix: pd.DataFrame, provided_weights: pd.DataFrame | None = None) -> None:
    st.session_state["input_matrix"] = matrix.copy()
    st.session_state["provided_weights"] = None if provided_weights is None else provided_weights.copy()
    st.session_state["editor_version"] = (
        st.session_state.get("editor_version", 0) + 1
    )
    clear_result()


def reset_project(
    number_of_alternatives: int,
    number_of_criteria: int,
) -> None:
    set_project_data(
        create_default_matrix(
            number_of_alternatives,
            number_of_criteria,
        )
    )


def display_error_list(errors: list[str]) -> None:
    st.error(
        "Dữ liệu đầu vào không hợp lệ:\n\n"
        + "\n".join(
            f"• {error}"
            for error in errors
        )
    )


# =============================================================================
# 2. PHẦN ĐẦU TRANG
# Header/mô tả được render từ components.py để app.py gọn hơn.
# =============================================================================
render_header()

# =========================================================
# 1. IMPORT AND PROBLEM CONFIGURATION
# =========================================================
with st.container(border=True):
    render_section_header(
        1,
        "Nhập dữ liệu đầu vào",
        (
            "Tải lên tệp Excel chứa ma trận SVNFS và thực hiện thuật toán."
        ),
    )

    # =============================================================================
    # 3. UPLOAD DỮ LIỆU EXCEL
    # Workbook chứa sheet Matrix.
    # Cột đầu: Alternative; các cột sau: C1...Cm.
    # Mỗi ô đánh giá có dạng (T, I, F, μ).
    # =============================================================================
    uploaded_file = st.file_uploader(
        "Tải lên ma trận SVNFS (.xlsx)",
        type=["xlsx"],
        help="Tệp Excel cần có trang tính tên Matrix.",
    )

    st.info(
        "Cấu trúc tệp Excel yêu cầu:\n\n"
        "- **Matrix** *(bắt buộc)*: Alternative, C1, C2, …\n\n"
        "- **Weights** *(tùy chọn)*: Criterion, Weight\n\n"
        "Mỗi ô Matrix có dạng `(T, I, F, μ)`.\n\n"
        "Nếu có sheet **Weights**, hệ thống dùng trọng số trong file. "
        "Nếu không có, trọng số được tính tự động từ E(cj) và C(cj)."
    )
# =============================================================================
# 4. SESSION STATE
# Streamlit rerun toàn bộ file sau mỗi thao tác. session_state giúp giữ dữ liệu
# đầu vào và kết quả để chúng không bị mất sau mỗi lần rerun.
# =============================================================================
if "input_matrix" not in st.session_state:
    reset_project(5, 6)


# =============================================================================
# 5. ĐỌC + KIỂM TRA FILE
# Parse file Excel và kiểm tra cấu trúc/giá trị trước khi cho phép chạy mô hình.
# Lỗi định dạng sẽ được báo cho người dùng thay vì truyền dữ liệu sai vào pipeline.
# =============================================================================
if uploaded_file is not None:
    uploaded_signature = (
        f"{uploaded_file.name}:{uploaded_file.size}"
    )

    if (
        st.session_state.get("uploaded_signature")
        != uploaded_signature
    ):
        try:
            imported_matrix, imported_weights = load_pipeline_excel(uploaded_file)
            set_project_data(imported_matrix, imported_weights)

            st.session_state["uploaded_signature"] = uploaded_signature

            st.success(
                "Đã nhập tệp dữ liệu thành công."
            )
        except Exception as error:
            st.error(
                f"Không thể nhập tệp dữ liệu: {error}"
            )




# 2. CRITERION WEIGHTS
# =========================================================
provided_weights = st.session_state.get("provided_weights")
if provided_weights is not None:
    st.success("Đã phát hiện sheet Weights: thuật toán sẽ dùng trọng số được cung cấp trong file Excel.")
else:
    st.caption("Không có sheet Weights: trọng số sẽ được tính tự động từ E(cj) và C(cj).")

with st.expander("Cách tính trọng số tiêu chí"):
    st.caption(
        "Nếu workbook có sheet Weights, hệ thống dùng trực tiếp trọng số đó. "
        "Nếu không có, trọng số được tính tự động từ ma trận SVNFS bằng s1, e1 và c1."
    )
    st.latex(
        r"""
        w_j=
        \frac{1-E(c_j)+C(c_j)}
        {\sum_{q=1}^{m}[1-E(c_q)+C(c_q)]}
        """
    )


# =========================================================
# 3. SCORING PARAMETERS
# =========================================================
with st.container(border=True):
    render_section_header(
        2,
        "Tham số hàm điểm",
        "Thiết lập α, β và γ sao cho α + β + γ = 1.",
    )

    alpha_column, beta_column, gamma_column = st.columns(3)

    with alpha_column:
        alpha = st.number_input(
            "Alpha (α) – độ đúng T",
            min_value=0.01,
            max_value=0.98,
            value=0.40,
            step=0.01,
            format="%.2f",
        )

    with beta_column:
        beta = st.number_input(
            "Beta (β) – thành phần 1 − I",
            min_value=0.01,
            max_value=0.98,
            value=0.40,
            step=0.01,
            format="%.2f",
        )

    with gamma_column:
        gamma = st.number_input(
            "Gamma (γ) – thành phần 1 − F",
            min_value=0.01,
            max_value=0.98,
            value=0.20,
            step=0.01,
            format="%.2f",
        )

    # Kiểm tra điều kiện tổng α + β + γ = 1 trước khi chạy pipeline.
    parameter_sum = alpha + beta + gamma
    if abs(parameter_sum - 1.0) > 1e-9:
        st.warning(f"α + β + γ = {parameter_sum:.2f}. Tổng ba tham số phải bằng 1.")


# =========================================================
# 4. SVNFS MATRIX
# =========================================================
with st.container(border=True):
    render_section_header(
        3,
        "Ma trận đánh giá SVNFS",
        (
            "Mỗi hàng là một phương án, mỗi cột là một tiêu chí, "
            "và mỗi ô có dạng (T, I, F, μ)."
        ),
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
    run_clicked = st.button(
        "▶ Thực hiện thuật toán SVNFSR-MCDM",
        type="primary",
        use_container_width=True,
    )


# =========================================================
# EXECUTE PIPELINE
# =========================================================
# =============================================================================
# 9. THỰC HIỆN PIPELINE
# Khi bấm nút chạy:
# - validate dữ liệu;
# - kiểm tra tham số;
# - gọi run_svnfsr(...);
# - lưu result vào session_state.
#
# Khi sửa CÔNG THỨC, ưu tiên sửa module trong algorithm/, không nhét công thức
# trực tiếp vào phần giao diện này.
# =============================================================================
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
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                provided_weights=st.session_state.get("provided_weights"),
            )

            result["input_matrix"] = matrix.copy()

            st.session_state[
                "algorithm_result"
            ] = result

            st.success(
                "Thuật toán SVNFSR-MCDM đã thực hiện thành công."
            )
        except Exception as error:
            st.error(
                f"Không thể thực hiện thuật toán: {error}"
            )


# =========================================================
# 5. RESULTS
# =========================================================
if "algorithm_result" in st.session_state:
    result = st.session_state["algorithm_result"]
    # =============================================================================
    # 11. XẾP HẠNG CUỐI
    # ranking dùng tên cột nội bộ:
    #   Alternative | Overall Score | Rank
    #
    # KHÔNG rename trực tiếp ranking. Tạo ranking_display nếu muốn hiển thị tiếng Việt.
    # =============================================================================
    ranking = result["ranking"]
    weights = result["weights"]
    detail = result["detail"]
    relation_matrix = result["relation_matrix"]

    best_names = ", ".join(result["best_alternatives"])

    with st.container(border=True):
        render_section_header(
            4,
            "Kết quả",
            "Kết quả xếp hạng các phương án.",
        )

        metric_1, metric_2 = st.columns(2)
        metric_1.metric("Phương án tốt nhất", best_names)
        metric_2.metric(
            "Điểm tổng thể cao nhất",
            f'{result["best_score"]:.6f}',
        )

        result_left, result_right = st.columns(2, gap="large")

        with result_left:
            st.subheader("Xếp hạng cuối cùng")
            st.dataframe(
                ranking.round({"Overall Score": 6}),
                use_container_width=True,
                hide_index=True,
            )

        with result_right:
            st.subheader("Điểm tổng thể")
            # -----------------------------------------------------------------------------
            # 12. BIỂU ĐỒ ĐIỂM
            # Phải chọn cột nội bộ 'Overall Score' TRƯỚC, sau đó mới đổi nhãn hiển thị.
            # Nếu truy cập ranking['Điểm tổng thể'] sẽ phát sinh KeyError.
            # -----------------------------------------------------------------------------
            ranking_chart = (
                ranking[["Alternative", "Overall Score"]]
                .set_index("Alternative")
            )
            st.bar_chart(
                ranking_chart,
                use_container_width=True,
            )

        # =============================================================================
        # 13. CHI TIẾT TÍNH TOÁN
        # Các bảng trung gian được đặt trong expander để giao diện public gọn hơn.
        # Người cần kiểm tra thuật toán vẫn có thể mở phần này.
        # =============================================================================
        with st.expander("Chi tiết tính toán"):
            st.markdown("**Trọng số tiêu chí**")
            # 13.1 Trọng số tiêu chí: hiển thị E(cj), C(cj), wj.
            weight_columns = ["Criterion", "E", "C", "Weight"]
            if "Weight Source" in weights.columns:
                weight_columns.append("Weight Source")
            weights_display = weights[weight_columns].copy().rename(
                columns={
                    "Criterion": "Tiêu chí",
                    "Weight": "Trọng số",
                    "Weight Source": "Nguồn trọng số",
                }
            )

            st.dataframe(
                weights_display.round(
                    {
                        "E": 4,
                        "C": 4,
                        "Trọng số": 4,
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("**Ma trận sau khi áp dụng trọng số**")
            # 13.2 Ma trận sau khi áp dụng trọng số.
            weighted_display = result["weighted_matrix"].rename(
                columns={"Alternative": "Phương án", "Criterion": "Tiêu chí"}
            )
            st.dataframe(
                weighted_display.round(6),
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("**Quan hệ R**")
            # 13.3 Quan hệ R giữa các cặp tiêu chí.
            relation_display = relation_matrix.rename(
                columns={
                    "Alternative": "Phương án",
                    "Criterion 1": "Tiêu chí 1",
                    "Criterion 2": "Tiêu chí 2",
                    "Relation": "Quan hệ",
                }
            )
            st.dataframe(
                relation_display.round({"T": 6, "I": 6, "F": 6, "μ": 6}),
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("**Điểm và chỉ số chi phối**")
            # 13.4 μ chuẩn hóa, V_ij, chỉ số chi phối và điểm đóng góp.
            detail_display = detail.rename(
                columns={
                    "Alternative": "Phương án",
                    "Criterion": "Tiêu chí",
                    "Relation": "Quan hệ",
                    "Normalized μ": "μ chuẩn hóa",
                    "Dominant Score": "Điểm chi phối",
                }
            )
            st.dataframe(
                detail_display.round(
                    {
                        "T": 6, "I": 6, "F": 6, "μ": 6,
                        "μ chuẩn hóa": 6, "V": 6, "Điểm chi phối": 6,
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        export_file = export_pipeline_to_excel(
            input_matrix=result["input_matrix"],
            weights=result["weights"],
            weighted_matrix=result["weighted_matrix"],
            relation_matrix=result["relation_matrix"],
            detail=result["detail"],
            ranking=result["ranking"],
        )

        export_spacer, export_column = st.columns([5, 1])

        with export_column:
            st.download_button(
                "↓ Xuất Excel",
                data=export_file,
                file_name="ket_qua_svnfsr_mcdm.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
            )


# =============================================================================
# 15. FOOTER
# =============================================================================
render_footer()

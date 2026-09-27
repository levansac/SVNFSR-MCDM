"""
===============================================================================
components.py - Các thành phần giao diện dùng chung cho SVNFSR-MCDM
===============================================================================

File này chỉ phụ trách giao diện:
- CSS bổ sung để các khối rõ nét hơn.
- Header của website.
- Tiêu đề từng bước.
- Footer.

Không đặt công thức hoặc logic thuật toán trong file này.
===============================================================================
"""

from __future__ import annotations

import html
import streamlit as st


def _inject_component_css() -> None:
    """Nạp CSS bổ sung cho giao diện.

    CSS này được đặt trong components.py để app.py không phải phụ thuộc vào
    việc sửa styles.py. Nó chủ yếu tăng độ tương phản của card, tiêu đề,
    uploader, input và bảng.
    """
    st.markdown(
        """
        <style>
        :root {
            --sv-primary: #2563eb;
            --sv-primary-dark: #1d4ed8;
            --sv-navy: #172554;
            --sv-border: #b9cbe3;
            --sv-soft: #eff6ff;
            --sv-text: #1e293b;
            --sv-muted: #64748b;
        }

        /* Nền trang */
        .stApp {
            background: linear-gradient(180deg, #f7fbff 0px, #ffffff 320px);
            color: var(--sv-text);
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.35rem;
            padding-bottom: 3rem;
        }

        /* Header */
        .svnfsr-header {
            background: linear-gradient(135deg, #eaf3ff 0%, #ffffff 55%, #eef6ff 100%);
            border: 1px solid #a9c8ef;
            border-left: 5px solid var(--sv-primary);
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 14px;
            box-shadow: 0 6px 22px rgba(37, 99, 235, 0.08);
        }

        .svnfsr-title {
            margin: 0;
            color: var(--sv-navy);
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .svnfsr-title span {
            color: var(--sv-primary);
        }

        .svnfsr-subtitle {
            margin-top: 8px;
            color: #475569;
            font-size: 1rem;
            line-height: 1.6;
        }

        .svnfsr-intro {
            background: #eef6ff;
            border: 1px solid #b9d5f7;
            border-left: 4px solid #3b82f6;
            border-radius: 11px;
            padding: 13px 18px;
            margin: 0 0 18px 0;
            color: #1d4ed8;
            text-align: center;
        }

        /* Card Streamlit có border */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid var(--sv-border) !important;
            border-left: 4px solid #3b82f6 !important;
            border-radius: 12px !important;
            background: #ffffff !important;
            box-shadow: 0 5px 18px rgba(30, 64, 175, 0.055);
        }

        /* Tiêu đề section */
        .svnfsr-section-head {
            display: flex;
            align-items: center;
            gap: 13px;
            margin-bottom: 4px;
        }

        .svnfsr-section-number {
            width: 38px;
            height: 38px;
            flex: 0 0 38px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            font-weight: 800;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        }

        .svnfsr-section-title {
            color: var(--sv-navy);
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            line-height: 1.25;
        }

        .svnfsr-section-description {
            color: #5b6b82;
            margin: 7px 0 18px 51px;
            font-size: 0.98rem;
            line-height: 1.6;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            background: #f7fbff;
            border: 1.5px dashed #4f8df7;
            border-radius: 11px;
            padding: 8px 10px;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: #edf5ff !important;
            border: 1px dashed #76a7f7 !important;
            border-radius: 9px !important;
        }

        /* Input */
        [data-testid="stNumberInput"] input {
            background: #ffffff !important;
            border: 1px solid #b9cbe3 !important;
            color: #172554 !important;
            font-weight: 600;
        }

        [data-testid="stNumberInput"] input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.12) !important;
        }

        [data-testid="stWidgetLabel"] p {
            color: #334155;
            font-weight: 600;
        }

        /* Button */
        .stButton > button {
            min-height: 44px;
            border-radius: 9px;
            border: 1px solid #9fb7d5;
            font-weight: 600;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
            border-color: #2563eb !important;
            color: white !important;
            box-shadow: 0 5px 14px rgba(37, 99, 235, 0.20);
        }

        .stButton > button[kind="primary"]:hover {
            background: #1d4ed8 !important;
            border-color: #1d4ed8 !important;
        }

        /* Expander */
        [data-testid="stExpander"] {
            border: 1px solid #b9cbe3 !important;
            border-radius: 10px !important;
            overflow: hidden;
            background: white;
        }

        [data-testid="stExpander"] summary {
            background: #f7fbff;
            color: #1e3a8a;
            font-weight: 600;
        }

        /* DataFrame */
        [data-testid="stDataFrame"] {
            border: 1px solid #c3d1e3;
            border-radius: 10px;
            overflow: hidden;
        }

        /* Download Excel nhỏ gọn */
        .stDownloadButton > button {
            min-height: 38px;
            border: 1px solid #2563eb;
            border-radius: 8px;
            color: #1d4ed8;
            background: white;
            font-weight: 600;
        }

        .stDownloadButton > button:hover {
            background: #eff6ff;
        }

        /* Footer */
        .svnfsr-footer {
            margin-top: 30px;
            padding-top: 16px;
            border-top: 1px solid #d6e1ee;
            color: #7c8ba1;
            text-align: center;
            font-size: 0.86rem;
        }

        @media (max-width: 900px) {
            .svnfsr-title { font-size: 1.55rem; }
            .svnfsr-section-title { font-size: 1.4rem; }
            .svnfsr-section-description { margin-left: 0; margin-top: 10px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Hiển thị phần đầu trang và đồng thời nạp CSS bổ sung."""
    _inject_component_css()

    st.markdown(
        """
        <div class="svnfsr-header">
            <h1 class="svnfsr-title">
                <span>SVNFSR-MCDM</span>
            </h1>
            <div class="svnfsr-subtitle">
                Mô hình quan hệ mềm mờ neutrosophic đơn trị có xét độ tin cậy
                cho bài toán ra quyết định đa tiêu chí
            </div>
        </div>

        <div class="svnfsr-intro">
            ⓘ Tải dữ liệu đánh giá SVNFSR, thiết lập tham số mô hình
            và thực hiện xếp hạng các phương án.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(
    number: int | str,
    title: str,
    description: str | None = None,
) -> None:
    """Hiển thị tiêu đề một bước.

    Hàm này render trực tiếp bằng st.markdown, đúng với cách app.py đang gọi:
        render_section_header(1, "Nhập dữ liệu đầu vào", "...")
    """
    safe_number = html.escape(str(number))
    safe_title = html.escape(str(title))

    description_html = ""
    if description:
        description_html = (
            '<div class="svnfsr-section-description">'
            f'{html.escape(str(description))}'
            '</div>'
        )

    st.markdown(
        f"""
        <div class="svnfsr-section-head">
            <div class="svnfsr-section-number">{safe_number}</div>
            <div class="svnfsr-section-title">{safe_title}</div>
        </div>
        {description_html}
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Hiển thị footer cuối trang."""
    st.markdown(
        """
        <div class="svnfsr-footer">
            SVNFSR-MCDM · Công cụ hỗ trợ ra quyết định đa tiêu chí
            có xét độ tin cậy
        </div>
        """,
        unsafe_allow_html=True,
    )

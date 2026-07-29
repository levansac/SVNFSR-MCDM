from __future__ import annotations

import html
import streamlit as st


def render_header() -> None:
    st.markdown(
        """
        <div class="app-header">
            <h1 class="app-title">▣ <span>SVNFSR-MCDM</span> Online Demo</h1>
            <div class="app-subtitle">
                A Reliability-aware Single-Valued Neutrosophic Fuzzy Soft Relation Model
                for Multi-criteria Decision-making
            </div>
        </div>
        <div class="top-note">
            ⓘ Enter SVNFSR evaluation data, configure the model parameters,
            and calculate the ranking of alternatives.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(
    number: int,
    title: str,
    description: str,
) -> None:
    st.markdown(
        f"""
        <div class="section-heading">
            <div class="section-number">{number}</div>
            <h2 class="section-title">{html.escape(title)}</h2>
        </div>
        <div class="section-description">{html.escape(description)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_help(text: str) -> None:
    st.markdown(
        f'<div class="mini-help">💡 {html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def render_sample_card() -> None:
    st.markdown(
        """
        <div class="sample-card">
            <div class="sample-card-title">▣ Load Sample Excel</div>
            <div class="sample-card-text">
                Load the built-in sample dataset and try the demo immediately.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_parameter_intro(
    name: str,
    symbol: str,
    description: str,
) -> None:
    st.markdown(
        f"""
        <div class="parameter-name">{html.escape(name)} ({html.escape(symbol)})</div>
        <div class="parameter-description">{html.escape(description)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_parameter_status(
    alpha: float,
    beta: float,
    gamma: float,
) -> None:
    total = alpha + beta + gamma
    if abs(total - 1.0) < 1e-9:
        st.markdown(
            f"""
            <div class="valid-box">
                ✓ α + β + γ = {total:.2f}<br>
                <span style="font-weight:500">Parameter combination is valid.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="invalid-box">
                ⚠ α + β + γ = {total:.2f}<br>
                <span style="font-weight:500">
                    The current implementation allows this combination,
                    but a sum of 1.00 is recommended for interpretation.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_result_banner(
    alternative: str,
    score: float,
) -> None:
    st.markdown(
        f"""
        <div class="result-banner">
            ✓ Recommended alternative:
            {html.escape(str(alternative))}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            Final score: {score:.6f}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="footer">
            SVNFSR-MCDM Online Demo · Reliability-aware decision support
        </div>
        """,
        unsafe_allow_html=True,
    )

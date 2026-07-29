def get_custom_css() -> str:
    return """
    <style>
    :root {
        --blue-50: #eff6ff;
        --blue-100: #dbeafe;
        --blue-200: #bfdbfe;
        --blue-500: #3b82f6;
        --blue-600: #2563eb;
        --blue-700: #1d4ed8;
        --slate-50: #f8fafc;
        --slate-100: #f1f5f9;
        --slate-200: #e2e8f0;
        --slate-500: #64748b;
        --slate-700: #334155;
        --slate-900: #0f172a;
        --green-50: #ecfdf5;
        --green-600: #059669;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.08), transparent 26rem),
            #ffffff;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, p, label, .stMarkdown {
        font-family: "Segoe UI", Arial, sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    .app-header {
        text-align: center;
        padding: 0.5rem 0 1.2rem;
    }

    .app-title {
        color: var(--slate-900);
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
    }

    .app-title span {
        color: var(--blue-600);
    }

    .app-subtitle {
        color: var(--slate-500);
        font-size: 1rem;
        margin-top: 0.4rem;
    }

    .top-note {
        background: linear-gradient(90deg, var(--blue-50), #f8fbff);
        border: 1px solid var(--blue-100);
        border-radius: 14px;
        color: var(--blue-700);
        padding: 0.9rem 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }

    .section-heading {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.2rem;
    }

    .section-number {
        width: 2rem;
        height: 2rem;
        border-radius: 9px;
        background: linear-gradient(135deg, var(--blue-500), var(--blue-700));
        color: white;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        box-shadow: 0 5px 12px rgba(37, 99, 235, 0.22);
    }

    .section-title {
        color: var(--slate-900);
        font-size: 1.45rem;
        font-weight: 800;
        margin: 0;
    }

    .section-description {
        color: var(--slate-500);
        margin: 0.15rem 0 1rem 2.7rem;
        font-size: 0.95rem;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--slate-200);
        border-left: 4px solid var(--blue-500);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.96);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }

    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding-top: 0.15rem;
    }

    [data-testid="stFileUploader"] {
        background: var(--blue-50);
        border: 1px dashed var(--blue-500);
        border-radius: 14px;
        padding: 0.5rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: transparent;
        border: none;
    }

    .mini-help {
        color: var(--slate-500);
        background: var(--slate-50);
        border: 1px solid var(--slate-200);
        border-radius: 10px;
        padding: 0.65rem 0.8rem;
        font-size: 0.9rem;
        margin-top: 0.35rem;
    }

    .sample-card {
        border: 1px solid #a7f3d0;
        background: var(--green-50);
        border-radius: 14px;
        padding: 1rem;
        min-height: 132px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .sample-card-title {
        color: var(--green-600);
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .sample-card-text {
        color: var(--slate-500);
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }

    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input {
        border-radius: 10px;
    }

    [data-testid="stNumberInput"] button {
        background: var(--slate-50);
        border-color: var(--slate-200);
    }

    .parameter-card {
        border: 1px solid var(--blue-100);
        background: linear-gradient(180deg, #ffffff, var(--blue-50));
        border-radius: 14px;
        padding: 0.9rem 1rem 0.3rem;
        min-height: 175px;
    }

    .parameter-name {
        color: var(--blue-700);
        font-weight: 800;
        margin-bottom: 0.15rem;
    }

    .parameter-description {
        color: var(--slate-500);
        min-height: 2.6rem;
        font-size: 0.88rem;
    }

    [data-testid="stCheckbox"] {
        padding: 0.75rem 0.9rem;
        background: var(--blue-50);
        border: 1px solid var(--blue-100);
        border-radius: 12px;
    }

    .valid-box {
        background: var(--green-50);
        border: 1px solid #a7f3d0;
        color: var(--green-600);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    .invalid-box {
        background: #fff7ed;
        border: 1px solid #fdba74;
        color: #c2410c;
        border-radius: 12px;
        padding: 0.85rem 1rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    [data-testid="stDataEditor"] {
        border: 1px solid var(--slate-200);
        border-radius: 14px;
        overflow: hidden;
    }

    .stButton > button {
        border-radius: 10px;
        min-height: 2.7rem;
        font-weight: 700;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, var(--blue-600), var(--blue-500));
        border: 0;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.2);
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff, var(--blue-50));
        border: 1px solid var(--blue-100);
        border-radius: 14px;
        padding: 0.85rem 1rem;
    }

    [data-testid="stMetricLabel"] {
        color: var(--slate-500);
    }

    [data-testid="stMetricValue"] {
        color: var(--blue-700);
        font-weight: 800;
    }

    .result-banner {
        background: linear-gradient(90deg, var(--green-50), #f6fffb);
        border: 1px solid #a7f3d0;
        color: var(--green-600);
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
        font-size: 1.05rem;
        font-weight: 800;
        margin: 0.8rem 0 1rem;
    }

    [data-testid="stDownloadButton"] button {
        border-radius: 10px;
        min-height: 2.7rem;
        font-weight: 700;
        border-color: var(--blue-500);
        color: var(--blue-700);
    }

    hr {
        border-color: var(--slate-200);
    }

    .footer {
        text-align: center;
        color: var(--slate-500);
        font-size: 0.85rem;
        padding-top: 1rem;
    }

    @media (max-width: 768px) {
        .app-title {
            font-size: 1.65rem;
        }

        .section-description {
            margin-left: 0;
        }
    }
    </style>
    """

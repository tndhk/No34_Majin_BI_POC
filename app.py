import json
import os
import traceback
from io import StringIO

import google.generativeai as genai
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

import prompts

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Majin式 GemBI Generator",
    page_icon="🧞‍♂️",
    layout="wide"
)

# Custom CSS - Mystical Oracle Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=Fira+Code:wght@400;500&display=swap');

    /* ═══════════════════════════════════════════════════════════
       MAJIN ORACLE - Mystical Data Sorcery Theme
       A dark, luxurious interface for summoning data insights
    ═══════════════════════════════════════════════════════════ */

    :root {
        --void-deep: #06060a;
        --void-surface: #0d0d14;
        --void-elevated: #14141f;
        --void-border: #1e1e2e;
        --oracle-cyan: #00e5ff;
        --oracle-cyan-dim: #00b8cc;
        --oracle-gold: #fbbf24;
        --oracle-gold-dim: #d97706;
        --oracle-purple: #a855f7;
        --text-primary: #f0f0f5;
        --text-secondary: #9090a0;
        --text-muted: #606070;
        --glow-cyan: 0 0 30px rgba(0, 229, 255, 0.3);
        --glow-gold: 0 0 20px rgba(251, 191, 36, 0.25);
    }

    /* Global dark theme override */
    .stApp {
        background: linear-gradient(145deg, var(--void-deep) 0%, #0a0a12 50%, var(--void-deep) 100%) !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(ellipse at 20% 20%, rgba(0, 229, 255, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(168, 85, 247, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(251, 191, 36, 0.02) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stSidebar"] {
        background: var(--void-surface) !important;
        border-right: 1px solid var(--void-border) !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-secondary) !important;
    }

    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        color: var(--text-primary) !important;
    }

    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    /* Typography */
    .main-header {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 3.2rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        background: linear-gradient(135deg, var(--oracle-cyan) 0%, var(--oracle-gold) 50%, var(--oracle-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
        text-shadow: var(--glow-cyan);
        position: relative;
        display: inline-block;
    }

    .main-header::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 0;
        width: 60%;
        height: 2px;
        background: linear-gradient(90deg, var(--oracle-cyan), transparent);
    }

    .sub-header {
        font-family: 'DM Sans', system-ui, sans-serif;
        font-size: 1.05rem;
        color: var(--text-secondary);
        margin-bottom: 2.5rem;
        font-weight: 400;
        letter-spacing: 0.01em;
        line-height: 1.6;
    }

    /* Section headers with mystical styling */
    .stMarkdown h3 {
        font-family: 'Cormorant Garamond', Georgia, serif !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-top: 2rem !important;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--void-border);
        position: relative;
    }

    .stMarkdown h3::before {
        content: '◆';
        color: var(--oracle-cyan);
        margin-right: 0.75rem;
        font-size: 0.8rem;
        opacity: 0.8;
    }

    /* Cards and containers */
    .step-card {
        background: var(--void-elevated);
        padding: 1.75rem;
        border-radius: 1rem;
        border: 1px solid var(--void-border);
        box-shadow:
            0 4px 24px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.03);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .step-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--oracle-cyan-dim), transparent);
        opacity: 0.5;
    }

    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: var(--void-elevated) !important;
        border: 2px dashed var(--void-border) !important;
        border-radius: 1rem !important;
        padding: 2rem !important;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--oracle-cyan-dim) !important;
        box-shadow: inset 0 0 30px rgba(0, 229, 255, 0.05);
    }

    [data-testid="stFileUploader"] * {
        color: var(--text-secondary) !important;
    }

    /* Buttons - Mystical glow effect */
    .stButton > button {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 0.5rem !important;
        border: none !important;
        background: linear-gradient(135deg, var(--oracle-cyan-dim) 0%, var(--oracle-cyan) 100%) !important;
        color: var(--void-deep) !important;
        box-shadow: var(--glow-cyan) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 40px rgba(0, 229, 255, 0.5) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--oracle-gold-dim) 0%, var(--oracle-gold) 100%) !important;
        box-shadow: var(--glow-gold) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 40px rgba(251, 191, 36, 0.5) !important;
    }

    /* DataFrame styling */
    [data-testid="stDataFrame"] {
        background: var(--void-elevated) !important;
        border-radius: 0.75rem !important;
        border: 1px solid var(--void-border) !important;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] * {
        font-family: 'Fira Code', monospace !important;
        font-size: 0.85rem !important;
    }

    /* Alert boxes */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
        border-left: 3px solid #10b981 !important;
        color: #6ee7b7 !important;
    }

    .stInfo {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.1) 0%, rgba(0, 229, 255, 0.05) 100%) !important;
        border-left: 3px solid var(--oracle-cyan) !important;
        color: var(--oracle-cyan) !important;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(251, 191, 36, 0.05) 100%) !important;
        border-left: 3px solid var(--oracle-gold) !important;
        color: var(--oracle-gold) !important;
    }

    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
        border-left: 3px solid #ef4444 !important;
        color: #fca5a5 !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: var(--oracle-cyan) transparent transparent transparent !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--void-surface) !important;
        border-radius: 0.75rem !important;
        padding: 0.25rem !important;
        gap: 0.25rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 1.5rem !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--void-elevated) !important;
        color: var(--oracle-cyan) !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        background: var(--void-elevated) !important;
        border-radius: 0.5rem !important;
    }

    /* Code blocks */
    .stCodeBlock {
        background: var(--void-deep) !important;
        border: 1px solid var(--void-border) !important;
        border-radius: 0.75rem !important;
    }

    .stCodeBlock code {
        font-family: 'Fira Code', monospace !important;
    }

    /* Horizontal rule */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--void-border), transparent) !important;
        margin: 2rem 0 !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        color: var(--text-primary) !important;
        box-shadow: none !important;
    }

    .stDownloadButton > button:hover {
        border-color: var(--oracle-cyan-dim) !important;
        color: var(--oracle-cyan) !important;
        box-shadow: var(--glow-cyan) !important;
    }

    /* Markdown text */
    .stMarkdown p, .stMarkdown li {
        color: var(--text-secondary) !important;
        font-family: 'DM Sans', system-ui, sans-serif !important;
        line-height: 1.7 !important;
    }

    .stMarkdown strong {
        color: var(--text-primary) !important;
    }

    .stMarkdown code {
        background: var(--void-elevated) !important;
        color: var(--oracle-cyan) !important;
        padding: 0.2em 0.4em !important;
        border-radius: 0.25rem !important;
        font-family: 'Fira Code', monospace !important;
    }

    /* Blueprint display box */
    .blueprint-box {
        background: var(--void-surface);
        border: 1px solid var(--void-border);
        border-radius: 1rem;
        padding: 1.5rem;
        max-height: 500px;
        overflow-y: auto;
    }

    .blueprint-box::-webkit-scrollbar {
        width: 6px;
    }

    .blueprint-box::-webkit-scrollbar-track {
        background: var(--void-deep);
    }

    .blueprint-box::-webkit-scrollbar-thumb {
        background: var(--void-border);
        border-radius: 3px;
    }

    .blueprint-box::-webkit-scrollbar-thumb:hover {
        background: var(--oracle-cyan-dim);
    }

    /* Floating orb decoration */
    .oracle-orb {
        width: 120px;
        height: 120px;
        background: radial-gradient(circle at 30% 30%, var(--oracle-cyan), transparent 70%);
        border-radius: 50%;
        position: fixed;
        top: 100px;
        right: 50px;
        opacity: 0.1;
        filter: blur(40px);
        pointer-events: none;
        animation: float 8s ease-in-out infinite;
        z-index: -1;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-20px) scale(1.1); }
    }

    /* Column gap adjustment */
    [data-testid="column"] {
        padding: 0 1rem;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
</style>

<!-- Decorative orb -->
<div class="oracle-orb"></div>
""", unsafe_allow_html=True)

# Main Title with mystical styling
st.markdown('''
<div class="main-header">
    <span style="font-size: 2.8rem; margin-right: 0.5rem;">🧞‍♂️</span>
    Majin式 GemBI Generator
</div>
''', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Summon the power of AI to transform your data into illuminating visualizations.<br/>Upload your CSV, review the oracle\'s blueprint, and manifest a fully functional BI dashboard.</div>', unsafe_allow_html=True)

# Sidebar: Configuration
with st.sidebar:
    st.header("Configuration")
    api_key_env = os.getenv("GOOGLE_API_KEY")
    api_key = st.text_input("Google API Key", value=api_key_env if api_key_env else "", type="password")

    model_name = st.selectbox(
        "Generator Model",
        ["gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-latest", "gemini-2.0-flash-exp"],
        index=0
    )

    st.info("Note: The generated dashboard will use `gemini-2.5-flash-preview-09-2025` internally as per specification.")

    if not api_key:
        st.warning("Please enter your Google API Key to proceed.")
        st.stop()

# Configure GenAI
genai.configure(api_key=api_key)

# Session State Initialization
if "blueprint" not in st.session_state:
    st.session_state.blueprint = None
if "csv_summary" not in st.session_state:
    st.session_state.csv_summary = None
if "generated_html" not in st.session_state:
    st.session_state.generated_html = None
if "full_csv_text" not in st.session_state:
    st.session_state.full_csv_text = None

# --- Step 1: Upload Data ---
st.markdown("### Step 1: Upload Data")
uploaded_file = st.file_uploader("Upload your CSV file (e.g. sales data)", type=["csv"])

if uploaded_file:
    try:
        # Read full CSV for injection later
        uploaded_file.seek(0)
        try:
            full_text = uploaded_file.read().decode('shift_jis')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            full_text = uploaded_file.read().decode('utf-8')

        st.session_state.full_csv_text = full_text

        # Read a subset for analysis (Pandas)
        uploaded_file.seek(0)
        try:
            df = pd.read_csv(uploaded_file, nrows=50, encoding='shift_jis')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, nrows=50, encoding='utf-8')

        st.success(f"Loaded successfully! Columns: {len(df.columns)}, Sample Rows: {len(df)}")
        st.dataframe(df.head())

        # Prepare summary for AI (using the small dataframe)
        buffer = StringIO()
        df.head(5).to_csv(buffer, index=False)
        sample_csv = buffer.getvalue()
        columns_str = ", ".join(df.columns.tolist())

        st.session_state.csv_summary = {
            "columns": columns_str,
            "sample": sample_csv
        }

    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()
else:
    st.session_state.blueprint = None
    st.session_state.generated_html = None
    st.session_state.full_csv_text = None


# --- Step 2: Analyze & Blueprint ---
if st.session_state.csv_summary:
    st.markdown("---")
    st.markdown("### Step 2: Analyze & Blueprint")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("""
        **Phase 1 Analysis:**
        The AI will analyze your data structure and propose 20+ charts.
        """)
        if st.button("🚀 Generate Blueprint", type="primary"):
            with st.spinner("Analyzing data structure..."):
                try:
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=prompts.SYSTEM_PROMPT)

                    prompt = prompts.PHASE1_PROMPT_TEMPLATE.format(
                        columns=st.session_state.csv_summary["columns"],
                        sample_data=st.session_state.csv_summary["sample"]
                    )

                    response = model.generate_content(prompt)
                    st.session_state.blueprint = response.text
                    st.session_state.generated_html = None # Reset downstream
                except Exception as e:
                    st.error(f"AI Error: {e}")

    with col2:
        if st.session_state.blueprint:
            st.markdown("#### Proposed Blueprint")
            st.markdown(st.session_state.blueprint)
            st.info("Review the plan above. You can regenerate if needed.")


# --- Step 3: Implement & Visualize ---
if st.session_state.blueprint:
    st.markdown("---")
    st.markdown("### Step 3: Dashboard Visualization")

    st.markdown("Generate the application and visualize it directly below.")

    if st.button("✨ Generate & Visualize", type="primary"):
        if not st.session_state.full_csv_text:
            st.error("Please upload a CSV file first.")
        else:
            with st.spinner("Analyzing data and performing Python-side aggregation..."):
                try:
                    # 1. Generate Codes
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=prompts.SYSTEM_PROMPT)
                    prompt = prompts.PHASE2_PROMPT_TEMPLATE.replace("{{BLUEPRINT}}", st.session_state.blueprint)

                    response = model.generate_content(prompt, generation_config={"max_output_tokens": 8192})
                    content = response.text

                    # 2. Extract Python and HTML Blocks
                    py_code = ""
                    html_code = ""
                    if "```python" in content:
                        py_code = content.split("```python")[1].split("```")[0].strip()
                    if "```html" in content:
                        html_code = content.split("```html")[1].split("```")[0].strip()

                    if not py_code or not html_code:
                        st.error("Failed to generate code blocks. Please try again.")
                        st.expander("AI Response").write(content)
                        st.stop()

                    # 3. Execute Python Aggregation
                    # Load data into DataFrame
                    try:
                        uploaded_file.seek(0)
                        # We try to detect the encoding again or use the one from state if we stored it
                        # Since we have full_csv_text, let's just use StringIO
                        df_full = pd.read_csv(StringIO(st.session_state.full_csv_text))

                        # Prepare local scope for execution
                        local_scope = {"pd": pd, "df": df_full}
                        exec(py_code, {}, local_scope)

                        if "aggregate_all_data" not in local_scope:
                            st.error("AI failed to define 'aggregate_all_data' function.")
                            st.stop()

                        aggregated_data = local_scope["aggregate_all_data"](df_full)
                        json_data = json.dumps(aggregated_data, ensure_ascii=False)

                    except Exception as e:
                        st.error(f"Execution Error (Python): {e}")
                        st.code(py_code, language="python")
                        st.stop()

                    # 4. Inject JSON and Shims into HTML
                    final_html = html_code.replace("{{JSON_DATA}}", json_data)

                    # Add Direct View Auto-load Shim
                    injection_script = """
                    <script>
                        // Overwrite window.onload to skip splash and init with data
                        const originalOnLoad = window.onload;
                        window.onload = function() {
                            if (originalOnLoad) originalOnLoad();
                            console.log("Direct View: Dashboard data injected.");
                            document.getElementById('initialSplash').classList.add('hidden');
                            if (typeof renderCharts === 'function') renderCharts();
                            // If there are other initialization functions, call them here
                        };
                    </script>
                    """
                    final_html = final_html.replace("</body>", f"{injection_script}</body>")

                    st.session_state.generated_html = final_html
                    st.balloons()

                except Exception as e:
                    st.error(f"Generation Error: {e}")
                    st.write(traceback.format_exc())

    if st.session_state.generated_html:
        st.success("Dashboard Generated with Python Optimization!")

        # Tabs for View vs Download
        tab1, tab2 = st.tabs(["👁️ Direct View", "📥 Download HTML"])

        with tab1:
            st.caption("The dashboard is running in an isolated container below. You can interact with it full-screen.")
            # Render HTML iframe
            components.html(st.session_state.generated_html, height=1200, scrolling=True)

        with tab2:
            st.download_button(
                label="Download HTML Dashboard (Standalone)",
                data=st.session_state.generated_html,
                file_name="majin_analytics_dashboard.html",
                mime="text/html"
            )
            with st.expander("View Source Code"):
                st.code(st.session_state.generated_html, language='html')

import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
from io import StringIO
import prompts
import streamlit.components.v1 as components
import json
import traceback

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Majin式 GemBI Generator",
    page_icon="🧞‍♂️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<div class="main-header">🧞‍♂️ Majin式 GemBI Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your CSV, review the blueprint, and generate a fully functional AI-powered BI dashboard.</div>', unsafe_allow_html=True)

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
        except:
             uploaded_file.seek(0)
             full_text = uploaded_file.read().decode('utf-8')
        
        st.session_state.full_csv_text = full_text

        # Read a subset for analysis (Pandas)
        uploaded_file.seek(0)
        try:
            df = pd.read_csv(uploaded_file, nrows=50, encoding='shift_jis')
        except:
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

    # Custom Analysis Focus (Optional)
    st.markdown("#### 📋 カスタム分析パラメータ (オプション)")
    custom_analysis_focus = st.text_area(
        "重視したいKPIや分析の切り口を入力してください (Optional)",
        placeholder="例:\n- 売上高と利益率の関係性を重点的に分析\n- 地域別・時系列での傾向把握\n- 顧客セグメント別のパフォーマンス比較",
        height=100,
        help="ここに入力した内容がAIプロンプトに追加され、分析の観点がカスタマイズされます"
    )

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

                    # Prepare custom focus section
                    custom_focus_section = ""
                    if custom_analysis_focus and custom_analysis_focus.strip():
                        custom_focus_section = f"""
## ユーザー指定の分析重視事項
以下の観点を特に重視して分析設計を行ってください:
{custom_analysis_focus.strip()}
"""

                    prompt = prompts.PHASE1_PROMPT_TEMPLATE.format(
                        columns=st.session_state.csv_summary["columns"],
                        sample_data=st.session_state.csv_summary["sample"],
                        custom_focus=custom_focus_section
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
                    injection_script = f"""
                    <script>
                        // Overwrite window.onload to skip splash and init with data
                        const originalOnLoad = window.onload;
                        window.onload = function() {{
                            if (originalOnLoad) originalOnLoad();
                            console.log("Direct View: Dashboard data injected.");
                            document.getElementById('initialSplash').classList.add('hidden');
                            if (typeof renderCharts === 'function') renderCharts();
                            // If there are other initialization functions, call them here
                        }};
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

"""
Data BI Analytics App v2

ワンショット生成 + 対話型分析
"""
import os

import google.generativeai as genai
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from src.services.ai_generator import AIGenerator
from src.services.chat_handler import ChatHandler
from src.services.data_processor import DataProcessor

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Majin Analytics - AI Data Oracle",
    page_icon="🧞‍♂️",
    layout="wide"
)

# Custom CSS - Majin Oracle Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=Fira+Code:wght@400;500&display=swap');

    /* ═══════════════════════════════════════════════════════════
       MAJIN ORACLE - Mystical Data Sorcery Theme
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

    /* Global dark theme */
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

    .main .block-container {
        padding-top: 2rem;
        max-width: 1600px;
    }

    /* Typography */
    .main-header {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        background: linear-gradient(135deg, var(--oracle-cyan) 0%, var(--oracle-gold) 50%, var(--oracle-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
        display: inline-block;
    }

    .sub-header {
        font-family: 'DM Sans', system-ui, sans-serif;
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-weight: 400;
        line-height: 1.6;
    }

    /* Section headers */
    .stMarkdown h3 {
        font-family: 'Cormorant Garamond', Georgia, serif !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--void-border);
    }

    .stMarkdown h3::before {
        content: '◆';
        color: var(--oracle-cyan);
        margin-right: 0.6rem;
        font-size: 0.75rem;
        opacity: 0.8;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--oracle-cyan-dim), var(--oracle-cyan)) !important;
        box-shadow: var(--glow-cyan);
    }

    /* Chat container */
    .chat-container {
        background: var(--void-elevated);
        border: 1px solid var(--void-border);
        border-radius: 1rem;
        padding: 1.25rem;
        height: 500px;
        overflow-y: auto;
    }

    .chat-container::-webkit-scrollbar {
        width: 6px;
    }

    .chat-container::-webkit-scrollbar-track {
        background: var(--void-deep);
    }

    .chat-container::-webkit-scrollbar-thumb {
        background: var(--void-border);
        border-radius: 3px;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        border-radius: 0.75rem !important;
        margin-bottom: 0.75rem;
    }

    [data-testid="stChatMessage"] * {
        color: var(--text-secondary) !important;
    }

    [data-testid="stChatMessageContent"] p {
        font-family: 'DM Sans', system-ui, sans-serif !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        border-radius: 0.75rem !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', system-ui, sans-serif !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: var(--void-elevated) !important;
        border: 2px dashed var(--void-border) !important;
        border-radius: 1rem !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--oracle-cyan-dim) !important;
        box-shadow: inset 0 0 30px rgba(0, 229, 255, 0.05);
    }

    [data-testid="stFileUploader"] * {
        color: var(--text-secondary) !important;
    }

    /* Buttons */
    .stButton > button {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
        padding: 0.7rem 1.5rem !important;
        border-radius: 0.5rem !important;
        border: none !important;
        background: linear-gradient(135deg, var(--oracle-cyan-dim) 0%, var(--oracle-cyan) 100%) !important;
        color: var(--void-deep) !important;
        box-shadow: var(--glow-cyan) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 40px rgba(0, 229, 255, 0.5) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--oracle-gold-dim) 0%, var(--oracle-gold) 100%) !important;
        box-shadow: var(--glow-gold) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 40px rgba(251, 191, 36, 0.5) !important;
    }

    /* DataFrame */
    [data-testid="stDataFrame"] {
        background: var(--void-elevated) !important;
        border-radius: 0.75rem !important;
        border: 1px solid var(--void-border) !important;
    }

    [data-testid="stDataFrame"] * {
        font-family: 'Fira Code', monospace !important;
        font-size: 0.85rem !important;
    }

    /* Alerts */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
        border-left: 3px solid #10b981 !important;
        color: #6ee7b7 !important;
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

    /* Tabs */
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
    }

    .stTabs [aria-selected="true"] {
        background: var(--void-elevated) !important;
        color: var(--oracle-cyan) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        background: var(--void-elevated) !important;
        border-radius: 0.5rem !important;
    }

    /* Markdown text */
    .stMarkdown p, .stMarkdown li {
        color: var(--text-secondary) !important;
        font-family: 'DM Sans', system-ui, sans-serif !important;
        line-height: 1.6 !important;
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

    /* Spinner */
    .stSpinner > div {
        border-color: var(--oracle-cyan) transparent transparent transparent !important;
    }

    /* Horizontal rule */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--void-border), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """セッション状態の初期化"""
    defaults = {
        "csv_data": None,
        "df_full": None,
        "dashboard_html": None,
        "aggregated_data": None,
        "blueprint": None,
        "chat_history": [],
        "generation_status": "idle",  # idle | generating | complete
        "current_step": 0,
        "total_steps": 4,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_progress():
    """生成進捗を表示"""
    steps = [
        ("📊", "データ分析"),
        ("🏗️", "構造設計"),
        ("📈", "グラフ生成"),
        ("✅", "完了")
    ]

    if st.session_state.generation_status == "generating":
        current = st.session_state.current_step
        progress = current / st.session_state.total_steps
        st.progress(progress)

        cols = st.columns(4)
        for i, (icon, label) in enumerate(steps):
            with cols[i]:
                if i < current:
                    st.markdown(f"~~{icon} {label}~~")
                elif i == current:
                    st.markdown(f"**{icon} {label}...**")
                else:
                    st.markdown(f"{icon} {label}")


def generate_dashboard(df: pd.DataFrame, model) -> bool:
    """ダッシュボードをワンショットで生成"""
    generator = AIGenerator(model=model)

    def progress_callback(step: int, message: str):
        st.session_state.current_step = step
        st.session_state.progress_message = message

    try:
        st.session_state.generation_status = "generating"
        result = generator.generate_oneshot(df, progress_callback=progress_callback)

        st.session_state.dashboard_html = result.html
        st.session_state.aggregated_data = result.data
        st.session_state.blueprint = result.blueprint
        st.session_state.generation_status = "complete"

        # 初期チャットメッセージを追加
        if not st.session_state.chat_history:
            summary = f"""
📊 **ダッシュボードを生成しました！**

**データ概要:**
- 行数: {len(df)}
- カラム: {', '.join(df.columns.tolist())}

何か質問があれば聞いてください。例えば:
- 「売上が最も高いのは？」
- 「地域別の比較グラフを追加して」
- 「このデータを分析して」
"""
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": summary
            })

        return True
    except Exception as e:
        st.error(f"生成エラー: {e}")
        st.session_state.generation_status = "idle"
        return False


def render_chat_interface(model):
    """チャットインターフェースを描画"""
    st.markdown("### 💬 AI アシスタント")

    # メッセージ履歴表示
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("chart_html"):
                components.html(message["chart_html"], height=300)

    # サジェスト（履歴が少ない場合のみ）
    if len(st.session_state.chat_history) <= 2:
        st.markdown("**💡 こんな質問ができます:**")
        suggestions = [
            "📊 売上トップ5を教えて",
            "📈 トレンドを分析して",
            "🔍 データの特徴を教えて"
        ]
        cols = st.columns(3)
        for i, sug in enumerate(suggestions):
            with cols[i]:
                if st.button(sug, key=f"sug_{i}"):
                    handle_chat_input(sug, model)
                    st.rerun()

    # チャット入力
    if prompt := st.chat_input("質問や分析リクエストを入力..."):
        handle_chat_input(prompt, model)
        st.rerun()


def handle_chat_input(user_message: str, model):
    """チャット入力を処理"""
    # ユーザーメッセージを追加
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_message
    })

    # ChatHandlerで処理
    handler = ChatHandler(model=model)
    context = {
        "df": st.session_state.df_full,
        "summary": st.session_state.aggregated_data
    }

    response = handler.handle_message(user_message, context)

    # 応答を追加
    assistant_message = {
        "role": "assistant",
        "content": response.content
    }

    # グラフが生成された場合
    if response.type == "chart" and response.chart_spec:
        spec = response.chart_spec
        data = handler.generate_chart_data(spec, st.session_state.df_full)
        chart_html = handler.generate_chart_html(spec, data)
        assistant_message["chart_html"] = chart_html

    st.session_state.chat_history.append(assistant_message)


def main():
    """メイン関数"""
    init_session_state()

    # Header with mystical styling
    st.markdown('''
    <div class="main-header">
        <span style="font-size: 2.4rem; margin-right: 0.5rem;">🧞‍♂️</span>
        Majin Analytics
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">CSVをアップロードして、AIオラクルがダッシュボードを召喚。<br/>その後、対話で深層分析を探求。</div>', unsafe_allow_html=True)

    # Sidebar: Configuration
    with st.sidebar:
        st.header("⚙️ 設定")
        api_key_env = os.getenv("GOOGLE_API_KEY")
        api_key = st.text_input(
            "Google API Key",
            value=api_key_env if api_key_env else "",
            type="password"
        )

        model_name = st.selectbox(
            "モデル",
            ["gemini-2.5-flash-preview-05-20", "gemini-2.0-flash-exp"],
            index=0
        )

        if not api_key:
            st.warning("APIキーを入力してください")
            st.stop()

    # Configure GenAI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name)

    # ダッシュボード未生成の場合
    if st.session_state.generation_status != "complete":
        # File Upload
        st.markdown("### 📁 データをアップロード")
        uploaded_file = st.file_uploader(
            "CSVファイルを選択",
            type=["csv"],
            help="日本語のCSV（Shift_JIS / UTF-8）に対応"
        )

        if uploaded_file:
            processor = DataProcessor()
            try:
                # CSVを読み込み
                uploaded_file.seek(0)
                csv_bytes = uploaded_file.read()
                df = processor.load_csv(csv_bytes)

                st.session_state.df_full = df
                st.session_state.csv_data = csv_bytes

                st.success(f"✅ 読み込み完了: {len(df)}行 × {len(df.columns)}列")

                # プレビュー
                with st.expander("📋 データプレビュー", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)

                # 生成ボタン
                st.markdown("---")
                if st.button("🚀 ダッシュボードを生成", type="primary", use_container_width=True):
                    with st.spinner("生成中..."):
                        render_progress()
                        success = generate_dashboard(df, model)
                        if success:
                            st.rerun()

            except Exception as e:
                st.error(f"読み込みエラー: {e}")

        # 生成中の進捗表示
        if st.session_state.generation_status == "generating":
            render_progress()

    # ダッシュボード生成済みの場合
    else:
        # 2カラムレイアウト
        col_dashboard, col_chat = st.columns([2, 1])

        with col_dashboard:
            st.markdown("### 📊 ダッシュボード")

            # タブ: 表示 / ダウンロード
            tab1, tab2 = st.tabs(["👁️ 表示", "📥 ダウンロード"])

            with tab1:
                components.html(
                    st.session_state.dashboard_html,
                    height=800,
                    scrolling=True
                )

            with tab2:
                st.download_button(
                    label="HTMLをダウンロード",
                    data=st.session_state.dashboard_html,
                    file_name="dashboard.html",
                    mime="text/html",
                    use_container_width=True
                )

            # リセットボタン
            if st.button("🔄 新しいデータで始める"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        with col_chat:
            render_chat_interface(model)


if __name__ == "__main__":
    main()

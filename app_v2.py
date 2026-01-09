"""
Data BI Analytics App v2

ワンショット生成 + 対話型分析
"""

import os
import traceback

from google import genai
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from src.services.ai_generator import AIGenerator
from src.services.chat_handler import ChatHandler
from src.services.data_processor import DataProcessor
from src.services.genai_adapter import GenAIModelAdapter

load_dotenv()

# =============================================================================
# 定数
# =============================================================================

AVAILABLE_MODELS = [
    "gemini-2.5-flash",  # 最新安定版（推奨）
    "gemini-3-flash-preview",  # 次世代モデル（実験版）
    "gemini-2.5-flash-lite",  # 軽量版（高速・低コスト）
    "gemini-2.0-flash-exp",  # 旧世代実験版
]

SESSION_DEFAULTS = {
    "csv_data": None,
    "df_full": None,
    "dashboard_html": None,
    "aggregated_data": None,
    "blueprint": None,
    "chat_history": [],
    "generation_status": "idle",
    "current_step": 0,
    "total_steps": 4,
    "last_generation_error": None,
}

PROGRESS_STEPS = [
    ("data_analysis", "データ分析"),
    ("structure_design", "構造設計"),
    ("chart_generation", "グラフ生成"),
    ("completion", "完了"),
]

CHAT_SUGGESTIONS = [
    "売上トップ5を教えて",
    "トレンドを分析して",
    "データの特徴を教えて",
]

MAJIN_ORACLE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=Fira+Code:wght@400;500&display=swap');

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

    .stApp {
        background: linear-gradient(145deg, var(--void-deep) 0%, #0a0a12 50%, var(--void-deep) 100%) !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
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
    [data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        color: var(--text-primary) !important;
    }

    .main .block-container { padding-top: 2rem; max-width: 1600px; }

    .main-header {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 2.8rem; font-weight: 700; letter-spacing: 0.02em;
        background: linear-gradient(135deg, var(--oracle-cyan) 0%, var(--oracle-gold) 50%, var(--oracle-purple) 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 0.25rem; display: inline-block;
    }

    .sub-header {
        font-family: 'DM Sans', system-ui, sans-serif;
        font-size: 1rem; color: var(--text-secondary);
        margin-bottom: 2rem; font-weight: 400; line-height: 1.6;
    }

    .stMarkdown h3 {
        font-family: 'Cormorant Garamond', Georgia, serif !important;
        font-size: 1.4rem !important; font-weight: 600 !important;
        color: var(--text-primary) !important;
        padding-bottom: 0.5rem; border-bottom: 1px solid var(--void-border);
    }
    .stMarkdown h3::before {
        content: '\u25c6'; color: var(--oracle-cyan);
        margin-right: 0.6rem; font-size: 0.75rem; opacity: 0.8;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--oracle-cyan-dim), var(--oracle-cyan)) !important;
        box-shadow: var(--glow-cyan);
    }

    .chat-container {
        background: var(--void-elevated); border: 1px solid var(--void-border);
        border-radius: 1rem; padding: 1.25rem; height: 500px; overflow-y: auto;
    }
    .chat-container::-webkit-scrollbar { width: 6px; }
    .chat-container::-webkit-scrollbar-track { background: var(--void-deep); }
    .chat-container::-webkit-scrollbar-thumb { background: var(--void-border); border-radius: 3px; }

    [data-testid="stChatMessage"] {
        background: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        border-radius: 0.75rem !important; margin-bottom: 0.75rem;
    }
    [data-testid="stChatMessage"] * { color: var(--text-secondary) !important; }
    [data-testid="stChatMessageContent"] p { font-family: 'DM Sans', system-ui, sans-serif !important; }

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

    [data-testid="stFileUploader"] {
        background: var(--void-elevated) !important;
        border: 2px dashed var(--void-border) !important;
        border-radius: 1rem !important; padding: 1.5rem !important;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--oracle-cyan-dim) !important;
        box-shadow: inset 0 0 30px rgba(0, 229, 255, 0.05);
    }
    [data-testid="stFileUploader"] * { color: var(--text-secondary) !important; }

    .stButton > button {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 600 !important; letter-spacing: 0.03em !important;
        text-transform: uppercase !important; font-size: 0.8rem !important;
        padding: 0.7rem 1.5rem !important; border-radius: 0.5rem !important;
        border: none !important;
        background: linear-gradient(135deg, var(--oracle-cyan-dim) 0%, var(--oracle-cyan) 100%) !important;
        color: var(--void-deep) !important; box-shadow: var(--glow-cyan) !important;
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

    [data-testid="stDataFrame"] {
        background: var(--void-elevated) !important;
        border-radius: 0.75rem !important;
        border: 1px solid var(--void-border) !important;
    }
    [data-testid="stDataFrame"] * {
        font-family: 'Fira Code', monospace !important;
        font-size: 0.85rem !important;
    }

    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
        border-left: 3px solid #10b981 !important; color: #6ee7b7 !important;
    }
    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(251, 191, 36, 0.05) 100%) !important;
        border-left: 3px solid var(--oracle-gold) !important; color: var(--oracle-gold) !important;
    }
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
        border-left: 3px solid #ef4444 !important; color: #fca5a5 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--void-surface) !important;
        border-radius: 0.75rem !important; padding: 0.25rem !important; gap: 0.25rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 500 !important; color: var(--text-secondary) !important;
        border-radius: 0.5rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--void-elevated) !important;
        color: var(--oracle-cyan) !important;
    }

    .streamlit-expanderHeader {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 500 !important; color: var(--text-secondary) !important;
        background: var(--void-elevated) !important; border-radius: 0.5rem !important;
    }

    .stMarkdown p, .stMarkdown li {
        color: var(--text-secondary) !important;
        font-family: 'DM Sans', system-ui, sans-serif !important;
        line-height: 1.6 !important;
    }
    .stMarkdown strong { color: var(--text-primary) !important; }
    .stMarkdown code {
        background: var(--void-elevated) !important;
        color: var(--oracle-cyan) !important;
        padding: 0.2em 0.4em !important; border-radius: 0.25rem !important;
        font-family: 'Fira Code', monospace !important;
    }

    .stDownloadButton > button {
        background: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        color: var(--text-primary) !important; box-shadow: none !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--oracle-cyan-dim) !important;
        color: var(--oracle-cyan) !important; box-shadow: var(--glow-cyan) !important;
    }

    .stSpinner > div { border-color: var(--oracle-cyan) transparent transparent transparent !important; }

    hr {
        border: none !important; height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--void-border), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>
"""

# =============================================================================
# セッション管理
# =============================================================================


def init_session_state() -> None:
    """セッション状態の初期化"""
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session_state() -> None:
    """セッション状態のリセット"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_dashboard_complete() -> bool:
    """ダッシュボード生成が完了しているか"""
    return st.session_state.generation_status == "complete"


# =============================================================================
# UI コンポーネント
# =============================================================================


def render_header() -> None:
    """ヘッダーを描画"""
    st.markdown(
        '<div class="main-header">'
        '<span style="font-size: 2.4rem; margin-right: 0.5rem;">&#x1F9DE;</span>'
        "Majin Analytics</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">CSVをアップロードして、AIオラクルがダッシュボードを召喚。'
        "<br/>その後、対話で深層分析を探求。</div>",
        unsafe_allow_html=True,
    )


def render_progress() -> None:
    """生成進捗を表示"""
    if st.session_state.generation_status != "generating":
        return

    current = st.session_state.current_step  # AIGeneratorから1～4の値を受け取る
    progress = min(current / st.session_state.total_steps, 1.0)
    st.progress(progress)

    cols = st.columns(4)
    for i, (_, label) in enumerate(PROGRESS_STEPS):
        with cols[i]:
            if i < current - 1:  # current=1のとき、i=0で比較すると0<0は偽
                st.markdown(f"~~{label}~~")
            elif i == current - 1:  # current=1のとき、i=0で表示
                st.markdown(f"[{label}...]")
            else:
                st.markdown(label)


def render_sidebar() -> str:
    """サイドバーを描画し、選択されたモデル名を返す"""
    with st.sidebar:
        st.header("設定")

        model_name = st.selectbox(
            "モデル",
            AVAILABLE_MODELS,
            index=0,
            help="gemini-2.5-flashが推奨（2026年1月時点の最新安定版）",
        )

        st.markdown("---")
        st.markdown("### Status")

        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            st.success("API Key: Configured")
        else:
            st.error("API Key: Missing")
            st.info("Please set GOOGLE_API_KEY in .env file")
            st.stop()

    return model_name


# =============================================================================
# ダッシュボード生成
# =============================================================================


def generate_dashboard(df: pd.DataFrame, model) -> bool:
    """ダッシュボードをワンショットで生成"""
    generator = AIGenerator(model=model)

    def progress_callback(step: int, message: str) -> None:
        st.session_state.current_step = step
        st.session_state.progress_message = message

    try:
        st.session_state.generation_status = "generating"
        result = generator.generate_oneshot(df, progress_callback=progress_callback)

        st.session_state.dashboard_html = result.html
        st.session_state.aggregated_data = result.data
        st.session_state.blueprint = result.blueprint
        st.session_state.generation_status = "complete"

        _add_initial_chat_message(df)
        return True
    except Exception as e:
        st.error(f"生成エラー: {e}")
        st.session_state.last_generation_error = traceback.format_exc()
        with st.expander("詳細ログ", expanded=True):
            st.code(st.session_state.last_generation_error)
        st.session_state.generation_status = "idle"
        return False


def _add_initial_chat_message(df: pd.DataFrame) -> None:
    """初期チャットメッセージを追加"""
    if st.session_state.chat_history:
        return

    columns_str = ", ".join(df.columns.tolist())
    summary = f"""ダッシュボードを生成しました。

データ概要:
- 行数: {len(df)}
- カラム: {columns_str}

何か質問があれば聞いてください。例えば:
- 「売上が最も高いのは?」
- 「地域別の比較グラフを追加して」
- 「このデータを分析して」
"""
    st.session_state.chat_history.append({"role": "assistant", "content": summary})


# =============================================================================
# ファイルアップロード画面
# =============================================================================


def render_upload_view(model) -> None:
    """ファイルアップロード画面を描画"""
    st.markdown("### データをアップロード")
    uploaded_file = st.file_uploader(
        "CSVファイルを選択",
        type=["csv"],
        help="日本語のCSV（Shift_JIS / UTF-8）に対応",
    )

    if not uploaded_file:
        if st.session_state.generation_status == "generating":
            render_progress()
        return

    processor = DataProcessor()
    try:
        uploaded_file.seek(0)
        csv_bytes = uploaded_file.read()
        df = processor.load_csv(csv_bytes)

        st.session_state.df_full = df
        st.session_state.csv_data = csv_bytes

        st.success(f"読み込み完了: {len(df)}行 x {len(df.columns)}列")

        with st.expander("データプレビュー", expanded=True):
            st.dataframe(df.head(10), width="stretch")

        st.markdown("---")
        if st.button("ダッシュボードを生成", type="primary", width="stretch"):
            with st.spinner("生成中..."):
                render_progress()
                if generate_dashboard(df, model):
                    st.rerun()

    except Exception as e:
        st.error(f"読み込みエラー: {e}")

    if st.session_state.generation_status == "generating":
        render_progress()


# =============================================================================
# ダッシュボード表示画面
# =============================================================================


def render_dashboard_view(model) -> None:
    """ダッシュボード表示画面を描画"""
    col_dashboard, col_chat = st.columns([2, 1])

    with col_dashboard:
        _render_dashboard_panel()

    with col_chat:
        _render_chat_panel(model)


def _render_dashboard_panel() -> None:
    """ダッシュボードパネルを描画"""
    st.markdown("### ダッシュボード")

    tab_view, tab_download = st.tabs(["表示", "ダウンロード"])

    with tab_view:
        components.html(
            st.session_state.dashboard_html,
            height=800,
            scrolling=True,
        )

    with tab_download:
        st.download_button(
            label="HTMLをダウンロード",
            data=st.session_state.dashboard_html,
            file_name="dashboard.html",
            mime="text/html",
            width="stretch",
        )

    if st.button("新しいデータで始める"):
        reset_session_state()
        st.rerun()


def _render_chat_panel(model) -> None:
    """チャットパネルを描画"""
    st.markdown("### AI アシスタント")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("chart_html"):
                components.html(message["chart_html"], height=300)

    _render_chat_suggestions(model)

    if prompt := st.chat_input("質問や分析リクエストを入力..."):
        _handle_chat_input(prompt, model)
        st.rerun()


def _render_chat_suggestions(model) -> None:
    """チャットサジェストを描画"""
    if len(st.session_state.chat_history) > 2:
        return

    st.markdown("こんな質問ができます:")
    cols = st.columns(3)
    for i, suggestion in enumerate(CHAT_SUGGESTIONS):
        with cols[i]:
            if st.button(suggestion, key=f"sug_{i}"):
                _handle_chat_input(suggestion, model)
                st.rerun()


def _handle_chat_input(user_message: str, model) -> None:
    """チャット入力を処理"""
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    handler = ChatHandler(model=model)
    context = {
        "df": st.session_state.df_full,
        "summary": st.session_state.aggregated_data,
    }

    response = handler.handle_message(user_message, context)

    assistant_message = {"role": "assistant", "content": response.content}

    if response.type == "chart" and response.chart_spec:
        spec = response.chart_spec
        data = handler.generate_chart_data(spec, st.session_state.df_full)
        chart_html = handler.generate_chart_html(spec, data)
        assistant_message["chart_html"] = chart_html

    st.session_state.chat_history.append(assistant_message)


# =============================================================================
# メイン
# =============================================================================


def main() -> None:
    """メイン関数"""
    st.set_page_config(
        page_title="Majin Analytics - AI Data Oracle",
        page_icon="&#x1F9DE;",
        layout="wide",
    )
    st.markdown(MAJIN_ORACLE_CSS, unsafe_allow_html=True)

    init_session_state()
    render_header()

    model_name = render_sidebar()
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    model = GenAIModelAdapter(client, model_name=model_name)

    if is_dashboard_complete():
        render_dashboard_view(model)
    else:
        render_upload_view(model)


if __name__ == "__main__":
    main()

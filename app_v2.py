"""
Data BI Analytics App v2

ワンショット生成 + 対話型分析
"""
import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

from src.services.data_processor import DataProcessor
from src.services.ai_generator import AIGenerator
from src.services.chat_handler import ChatHandler, Intent

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Data BI Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1e3a8a;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    .chat-container {
        background: #f8fafc;
        border-radius: 0.5rem;
        padding: 1rem;
        height: 500px;
        overflow-y: auto;
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

    # Header
    st.markdown('<div class="main-header">📊 Data BI Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">CSVをアップロードして、AIがダッシュボードを自動生成。その後、対話で深掘り分析。</div>', unsafe_allow_html=True)

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

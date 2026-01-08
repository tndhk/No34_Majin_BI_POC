# Data BI Analytics App 実装計画書

## 1. 実装フェーズ概要

```
Phase 1: ワンショット生成機能
    ↓
Phase 2: チャットUI基盤
    ↓
Phase 3: 対話型分析機能
    ↓
Phase 4: UI/UX改善・最適化
```

---

## 2. Phase 1: ワンショット生成機能

### 2.1 目的
現行の3ステップ（Upload → Blueprint確認 → Generate）を1ステップに統合

### 2.2 タスク一覧

#### Task 1.1: アプリ構造のリファクタリング
**ファイル構成変更:**
```
app.py                    # 現行（リファクタリング）
  ↓
app_new.py               # 新規メインアプリ
├── components/
│   ├── __init__.py
│   ├── file_uploader.py  # CSVアップロードコンポーネント
│   ├── dashboard.py      # ダッシュボード表示
│   ├── chat.py           # チャットUI
│   └── progress.py       # 進捗表示
├── services/
│   ├── __init__.py
│   ├── data_processor.py # データ処理
│   ├── ai_generator.py   # AI生成ロジック
│   └── chat_handler.py   # チャット処理
├── prompts/
│   ├── __init__.py
│   ├── blueprint.py      # Phase1プロンプト
│   ├── dashboard.py      # Phase2プロンプト
│   └── chat.py           # チャット用プロンプト
└── utils/
    ├── __init__.py
    └── helpers.py        # ユーティリティ関数
```

#### Task 1.2: ワンショット生成ロジック実装
```python
# services/ai_generator.py

class DashboardGenerator:
    def __init__(self, api_key: str, model_name: str):
        self.model = genai.GenerativeModel(model_name)

    async def generate_oneshot(
        self,
        df: pd.DataFrame,
        progress_callback: Callable
    ) -> GenerationResult:
        """
        ワンショットでダッシュボードを生成

        Steps:
        1. データ分析 & Blueprint生成
        2. Python集計コード生成
        3. HTMLダッシュボード生成
        4. 実行 & 組み立て
        """
        # Step 1: Blueprint
        progress_callback(step=1, message="データ構造を分析中...")
        blueprint = await self._generate_blueprint(df)

        # Step 2-3: Code Generation
        progress_callback(step=2, message="ダッシュボードを設計中...")
        py_code, html_code = await self._generate_code(blueprint)

        # Step 4: Execute & Assemble
        progress_callback(step=3, message="グラフを生成中...")
        result = self._execute_and_assemble(df, py_code, html_code)

        progress_callback(step=4, message="完了!")
        return result
```

#### Task 1.3: 進捗表示コンポーネント
```python
# components/progress.py

def render_progress(current_step: int, total_steps: int = 4):
    """
    生成進捗を視覚的に表示

    ステップ:
    1. データ分析
    2. 構造設計
    3. グラフ生成
    4. 完了
    """
    steps = [
        ("データ分析", "📊"),
        ("構造設計", "🏗️"),
        ("グラフ生成", "📈"),
        ("完了", "✅")
    ]

    progress_percent = (current_step / total_steps) * 100
    st.progress(progress_percent / 100)

    cols = st.columns(total_steps)
    for i, (label, icon) in enumerate(steps):
        with cols[i]:
            if i < current_step:
                st.markdown(f"~~{icon} {label}~~")
            elif i == current_step:
                st.markdown(f"**{icon} {label}**")
            else:
                st.markdown(f"{icon} {label}")
```

#### Task 1.4: セッション状態管理
```python
# utils/session.py

def init_session_state():
    """セッション状態の初期化"""
    defaults = {
        "csv_data": None,
        "df_full": None,
        "df_summary": None,
        "blueprint": None,
        "aggregated_data": None,
        "dashboard_html": None,
        "chat_history": [],
        "generation_status": "idle",  # idle | generating | complete
        "current_step": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
```

### 2.3 成果物
- [x] ワンクリックでダッシュボード生成
- [x] 進捗表示UI
- [x] リファクタリングされたコード構造

---

## 3. Phase 2: チャットUI基盤

### 3.1 目的
Streamlitのチャット機能を活用した対話インターフェース構築

### 3.2 タスク一覧

#### Task 2.1: チャットUIコンポーネント
```python
# components/chat.py

def render_chat_interface():
    """チャットUIを描画"""

    # 初期メッセージ（データサマリー）
    if not st.session_state.chat_history:
        initial_message = generate_data_summary(st.session_state.df_full)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": initial_message,
            "type": "summary"
        })

    # メッセージ履歴表示
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message.get("type") == "chart":
                # グラフの場合は特別表示
                st.components.v1.html(message["chart_html"], height=400)
            else:
                st.markdown(message["content"])

    # 入力欄
    if prompt := st.chat_input("質問や分析リクエストを入力..."):
        handle_user_input(prompt)
```

#### Task 2.2: サジェスト機能
```python
# components/chat.py

def render_suggestions():
    """分析サジェストを表示"""
    suggestions = [
        "📊 売上トップ10を見せて",
        "📈 月別のトレンドを分析して",
        "🔍 異常値を検出して",
        "📋 このデータをまとめて"
    ]

    st.markdown("**💡 こんな質問ができます:**")
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(suggestion, key=f"sug_{i}"):
                handle_user_input(suggestion)
```

#### Task 2.3: 2カラムレイアウト
```python
# app_new.py (メイン)

def render_main_view():
    """ダッシュボード生成後のメインビュー"""

    col_dashboard, col_chat = st.columns([2, 1])

    with col_dashboard:
        st.markdown("### 📊 ダッシュボード")
        components.html(
            st.session_state.dashboard_html,
            height=800,
            scrolling=True
        )

    with col_chat:
        st.markdown("### 💬 AI アシスタント")
        render_chat_interface()
```

### 3.3 成果物
- [x] チャットUI（メッセージ表示 + 入力）
- [x] 2カラムレイアウト
- [x] サジェスト機能

---

## 4. Phase 3: 対話型分析機能

### 4.1 目的
AIとの対話で追加分析・グラフ生成を実現

### 4.2 タスク一覧

#### Task 3.1: チャットハンドラー
```python
# services/chat_handler.py

class ChatHandler:
    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
        self.system_prompt = CHAT_SYSTEM_PROMPT

    def handle_message(self, user_message: str, context: dict) -> ChatResponse:
        """
        ユーザーメッセージを処理

        1. 意図を分類
        2. 適切な処理を実行
        3. 応答を生成
        """
        # 意図分類
        intent = self._classify_intent(user_message)

        if intent == "question":
            return self._handle_question(user_message, context)
        elif intent == "add_chart":
            return self._handle_chart_request(user_message, context)
        elif intent == "analyze":
            return self._handle_analysis(user_message, context)
        elif intent == "summarize":
            return self._handle_summary(user_message, context)
        else:
            return self._handle_general(user_message, context)
```

#### Task 3.2: 意図分類プロンプト
```python
# prompts/chat.py

INTENT_CLASSIFICATION_PROMPT = """
ユーザーのメッセージを以下のカテゴリに分類してください。

カテゴリ:
- question: データに関する質問（「〜は何？」「なぜ〜？」）
- add_chart: グラフ追加リクエスト（「〜を見せて」「グラフを追加」）
- analyze: 分析リクエスト（「分析して」「比較して」「相関を見て」）
- summarize: まとめリクエスト（「まとめて」「レポートにして」）
- general: その他

ユーザーメッセージ: {message}

JSONで回答: {{"intent": "カテゴリ名", "entities": ["抽出されたエンティティ"]}}
"""
```

#### Task 3.3: 追加グラフ生成
```python
# services/chart_generator.py

class AdditionalChartGenerator:
    def generate_chart(
        self,
        request: str,
        df: pd.DataFrame,
        existing_charts: list
    ) -> ChartResult:
        """
        リクエストに基づいて追加グラフを生成

        1. リクエストを解析
        2. 必要なデータを集計
        3. グラフHTMLを生成
        """
        # AIにグラフ仕様を生成させる
        chart_spec = self._generate_chart_spec(request, df.columns.tolist())

        # データを集計
        chart_data = self._aggregate_for_chart(df, chart_spec)

        # HTMLを生成
        chart_html = self._generate_chart_html(chart_spec, chart_data)

        return ChartResult(
            chart_id=f"additional_{len(existing_charts)}",
            title=chart_spec["title"],
            html=chart_html,
            data=chart_data
        )
```

#### Task 3.4: データ質問応答
```python
# services/chat_handler.py

def _handle_question(self, question: str, context: dict) -> ChatResponse:
    """
    データに関する質問に回答

    例:
    - 「売上が一番高いのは？」→ データを検索して回答
    - 「なぜ3月に下がった？」→ 分析して考察
    """
    prompt = f"""
    以下のデータに関する質問に答えてください。

    ## データサマリー
    {context['data_summary']}

    ## 統計情報
    {context['statistics']}

    ## 質問
    {question}

    ## 回答ガイドライン
    - 具体的な数値を含める
    - データの根拠を示す
    - 簡潔に回答する（3-5文程度）
    """

    response = self.model.generate_content(prompt)
    return ChatResponse(type="text", content=response.text)
```

#### Task 3.5: コンテキスト管理
```python
# services/context_manager.py

class ContextManager:
    def build_context(self) -> dict:
        """AIに渡すコンテキストを構築"""
        df = st.session_state.df_full

        return {
            "data_summary": self._generate_data_summary(df),
            "statistics": self._calculate_statistics(df),
            "column_info": self._get_column_info(df),
            "current_charts": st.session_state.get("chart_list", []),
            "chat_history": st.session_state.chat_history[-10:],  # 直近10件
        }

    def _generate_data_summary(self, df: pd.DataFrame) -> str:
        """データサマリーを生成"""
        return f"""
        行数: {len(df)}
        列数: {len(df.columns)}
        カラム: {', '.join(df.columns.tolist())}
        数値列: {', '.join(df.select_dtypes(include=['number']).columns.tolist())}
        カテゴリ列: {', '.join(df.select_dtypes(include=['object']).columns.tolist())}
        """
```

### 4.3 成果物
- [x] 意図分類機能
- [x] 質問応答機能
- [x] 追加グラフ生成機能
- [x] コンテキスト管理

---

## 5. Phase 4: UI/UX改善・最適化

### 5.1 目的
ユーザー体験の向上とパフォーマンス最適化

### 5.2 タスク一覧

#### Task 4.1: ローディングUX改善
- スケルトンローダー
- アニメーション付き進捗
- 予想待ち時間表示

#### Task 4.2: エラーハンドリング
- ユーザーフレンドリーなエラーメッセージ
- リトライ機能
- フォールバック処理

#### Task 4.3: レスポンシブ対応
- モバイル表示最適化
- タブレット対応

#### Task 4.4: パフォーマンス最適化
- キャッシュ活用（@st.cache_data）
- 遅延読み込み
- 大規模データ対応

---

## 6. 実装スケジュール

```
Phase 1: ワンショット生成
├── Task 1.1: アプリ構造リファクタリング
├── Task 1.2: ワンショット生成ロジック
├── Task 1.3: 進捗表示
└── Task 1.4: セッション状態管理

Phase 2: チャットUI基盤
├── Task 2.1: チャットUIコンポーネント
├── Task 2.2: サジェスト機能
└── Task 2.3: 2カラムレイアウト

Phase 3: 対話型分析
├── Task 3.1: チャットハンドラー
├── Task 3.2: 意図分類
├── Task 3.3: 追加グラフ生成
├── Task 3.4: 質問応答
└── Task 3.5: コンテキスト管理

Phase 4: UI/UX改善
├── Task 4.1: ローディングUX
├── Task 4.2: エラーハンドリング
├── Task 4.3: レスポンシブ対応
└── Task 4.4: パフォーマンス最適化
```

---

## 7. 技術的考慮事項

### 7.1 Streamlitの制約と対策

| 制約 | 対策 |
|------|------|
| 全体再実行 | session_stateで状態保持 |
| 同期処理 | spinner + 進捗表示でUX改善 |
| カスタムCSS制限 | st.markdown(unsafe_allow_html=True) |

### 7.2 AI API利用

| 項目 | 方針 |
|------|------|
| レート制限 | リトライ + 指数バックオフ |
| コスト管理 | トークン数監視、キャッシュ活用 |
| 応答品質 | プロンプトエンジニアリング、Few-shot |

### 7.3 テスト方針

| レイヤー | テスト方法 |
|----------|------------|
| データ処理 | pytest + pandas testing |
| AI生成 | モック + スナップショット |
| UI | 手動テスト + スクリーンショット |

---

## 8. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| AI生成失敗 | ダッシュボード生成不可 | リトライ + フォールバックテンプレート |
| 大規模データ | メモリ不足、遅延 | サンプリング + 分割処理 |
| API障害 | サービス停止 | エラーハンドリング + 通知 |

---

## 9. 成功指標

| 指標 | 目標値 |
|------|--------|
| ダッシュボード生成成功率 | 95%以上 |
| 生成時間 | 60秒以内 |
| チャット応答時間 | 5秒以内 |
| ユーザー満足度 | 調査で80%以上が「満足」 |

---

## 10. 次のアクション

### 実装開始時の最初のステップ
1. ブランチ作成（feature/oneshot-generation）
2. 新規ディレクトリ構造作成
3. Task 1.1 から着手

### 確認事項
- [ ] Gemini API のレート制限確認
- [ ] Streamlitのバージョン確認（チャット機能対応）
- [ ] テストデータの準備

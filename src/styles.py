MAJIN_ORACLE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        /* Base Colors - Deep Executive Navy */
        --void-deep: #0b1120;       /* Dark Midnight Blue (背景最下層) */
        --void-surface: #151e32;    /* Deep Slate (メイン背景) */
        --void-elevated: #1e293b;   /* Slate 800 (カード背景) */
        --void-border: #334155;     /* Slate 700 (明確な境界線) */

        /* Accent Colors - Professional Trust */
        --oracle-primary: #38bdf8;   /* Sky 400 (プライマリアクセント) */
        --oracle-primary-dim: #0284c7; /* Sky 600 */
        --oracle-gold: #fbbf24;      /* Amber 400 (ハイライト) */
        --oracle-gold-dim: #d97706;  /* Amber 600 */
        --oracle-accent: #818cf8;    /* Indigo 400 */

        /* Text Colors - High Contrast */
        --text-primary: #f8fafc;     /* Slate 50 (ほぼ白) */
        --text-secondary: #cbd5e1;   /* Slate 300 (高可読性グレー) */
        --text-muted: #94a3b8;       /* Slate 400 */

        /* Effects */
        --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.15);
        --glow-primary: 0 0 20px rgba(56, 189, 248, 0.2);
    }

    .stApp {
        background-color: var(--void-deep) !important;
        background-image: none !important; /* フラットな背景推奨 */
    }

    /* 背景の装飾を最小限に - プロフェッショナルな静寂 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; height: 300px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, transparent 100%);
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stSidebar"] {
        background-color: var(--void-surface) !important;
        border-right: 1px solid var(--void-border) !important;
    }
    [data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        color: var(--text-primary) !important;
        border-radius: 0.5rem !important;
    }

    .main .block-container { padding-top: 2rem; max-width: 1600px; }

    .main-header {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.8rem; font-weight: 700; letter-spacing: 0.02em;
        /* 知性を感じるグラデーション */
        background: linear-gradient(135deg, var(--oracle-primary) 0%, #60a5fa 50%, var(--oracle-accent) 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 0.25rem; display: inline-block;
        text-shadow: 0 2px 10px rgba(56, 189, 248, 0.1);
    }

    .sub-header {
        font-family: 'DM Sans', sans-serif;
        font-size: 1rem; color: var(--text-secondary);
        margin-bottom: 2rem; font-weight: 400; line-height: 1.6;
    }

    .stMarkdown h3 {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.5rem !important; font-weight: 600 !important;
        color: var(--text-primary) !important;
        padding-bottom: 0.5rem; border-bottom: 1px solid var(--void-border);
        margin-top: 1.5rem !important;
    }
    .stMarkdown h3::before {
        content: '◈'; color: var(--oracle-primary);
        margin-right: 0.6rem; font-size: 0.9rem; opacity: 0.9;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--oracle-primary-dim), var(--oracle-primary)) !important;
    }

    /* Chat Container - Explicit Borders */
    .chat-container {
        background-color: var(--void-elevated);
        border: 1px solid var(--void-border);
        border-radius: 0.75rem;
        padding: 1.25rem; height: 500px; overflow-y: auto;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }
    .chat-container::-webkit-scrollbar { width: 8px; }
    .chat-container::-webkit-scrollbar-track { background: var(--void-surface); }
    .chat-container::-webkit-scrollbar-thumb { background: var(--void-border); border-radius: 4px; }

    [data-testid="stChatMessage"] {
        background-color: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        border-radius: 0.75rem !important; margin-bottom: 0.75rem;
    }
    [data-testid="stChatMessage"] * { color: var(--text-secondary) !important; }
    [data-testid="stChatMessageContent"] p { font-family: 'DM Sans', sans-serif !important; }

    [data-testid="stChatInput"] {
        background-color: var(--void-elevated) !important;
        border: 1px solid var(--void-border) !important;
        border-radius: 0.75rem !important;
    }
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    [data-testid="stFileUploader"] {
        background-color: var(--void-elevated) !important;
        border: 2px dashed var(--void-border) !important;
        border-radius: 0.75rem !important; padding: 2rem !important;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--oracle-primary) !important;
        background-color: rgba(56, 189, 248, 0.05) !important;
    }
    [data-testid="stFileUploader"] * { color: var(--text-secondary) !important; }

    /* Buttons - Sharp & Professional */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important; letter-spacing: 0.02em !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 1.25rem !important; border-radius: 0.5rem !important;
        border: 1px solid var(--void-border) !important;
        background: var(--void-elevated) !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-card) !important;
    }
    .stButton > button:hover {
        border-color: var(--oracle-primary) !important;
        color: var(--oracle-primary) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--oracle-primary-dim) 0%, var(--oracle-primary) 100%) !important;
        border: none !important;
        color: #fff !important; /* Always white on primary */
        box-shadow: 0 4px 6px rgba(2, 132, 199, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 12px rgba(2, 132, 199, 0.4) !important;
    }

    [data-testid="stDataFrame"] {
        background-color: var(--void-elevated) !important;
        border-radius: 0.75rem !important;
        border: 1px solid var(--void-border) !important;
    }
    [data-testid="stDataFrame"] * {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        color: var(--text-secondary) !important;
    }

    .stSuccess {
        background-color: rgba(52, 211, 153, 0.1) !important;
        border-left: 3px solid #34d399 !important; color: #34d399 !important;
    }
    .stWarning {
        background-color: rgba(251, 191, 36, 0.1) !important;
        border-left: 3px solid var(--oracle-gold) !important; color: var(--oracle-gold) !important;
    }
    .stError {
        background-color: rgba(248, 113, 113, 0.1) !important;
        border-left: 3px solid #f87171 !important; color: #f87171 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--void-surface) !important;
        border-radius: 0.5rem !important; padding: 0.25rem !important; gap: 0.5rem !important;
        border: 1px solid var(--void-border) !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important; color: var(--text-secondary) !important;
        border-radius: 0.3rem !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--void-elevated) !important;
        color: var(--oracle-primary) !important;
        font-weight: 600 !important;
    }

    .streamlit-expanderHeader {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important; color: var(--text-primary) !important;
        background-color: var(--void-elevated) !important;
        border-radius: 0.5rem !important;
        border: 1px solid var(--void-border) !important;
    }

    .stMarkdown p, .stMarkdown li {
        color: var(--text-secondary) !important;
        font-family: 'DM Sans', sans-serif !important;
        line-height: 1.7 !important;
    }
    .stMarkdown strong { color: var(--text-primary) !important; font-weight: 600 !important; }
    .stMarkdown code {
        background-color: var(--void-surface) !important;
        color: var(--oracle-primary) !important;
        padding: 0.2em 0.4em !important; border-radius: 0.25rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        border: 1px solid var(--void-border) !important;
    }

    .stSpinner > div { border-color: var(--oracle-primary) transparent transparent transparent !important; }

    hr {
        border: none !important; height: 1px !important;
        background-color: var(--void-border) !important;
        margin: 2rem 0 !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>
"""

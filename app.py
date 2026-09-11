import streamlit as st

from utils.common import render_sidebar_settings

st.set_page_config(page_title="AIライティングツール", page_icon="🖋️", layout="wide")

render_sidebar_settings()

st.title("🖋️ AIライティングツール")
st.write(
    "Gemini APIを使った、個人用オールインワン・ライティング支援ツールです。"
    "左のメニューから使いたい機能を選んでください。"
)

st.subheader("できること")

features = [
    ("📝 ブログ記事作成", "トピックとキーワードから記事の下書きを生成します。"),
    ("📧 メール返信文作成", "受信メールと返信の要点から返信文を作成します。"),
    ("📄 文章要約", "長文を指定の長さ・形式で要約します。"),
    ("✍️ 校正・リライト", "誤字脱字や敬語、読みやすさをチェックして修正します。"),
    ("🔄 文体変換", "です・ます調やビジネス調など、文体をワンクリックで変換します。"),
    ("💡 タイトル生成", "記事の概要から複数のタイトル案を生成します。"),
    ("🐦 SNS投稿文作成", "X / Instagram など媒体別の投稿文を作成します。"),
    ("🌐 翻訳", "自然な文章として多言語に翻訳します。"),
]

cols = st.columns(2)
for i, (name, desc) in enumerate(features):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.caption(desc)

st.divider()
st.subheader("はじめに")
st.markdown(
    """
1. サイドバーに [Google AI Studio](https://aistudio.google.com/apikey) で取得したGemini APIキーを入力します。
2. 左メニューから使いたい機能を選択します。
3. 必要事項を入力して生成ボタンを押すだけです。

`.env` ファイルを作成し `GEMINI_API_KEY=あなたのキー` と記載しておくと、次回以降の入力を省略できます
（`.env.example` をコピーして使ってください）。
"""
)

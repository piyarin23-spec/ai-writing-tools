import streamlit as st

from utils.common import get_settings, render_sidebar_settings, require_api_key
from utils.gemini_client import GeminiError, generate_stream

st.set_page_config(page_title="ブログ記事作成 | AIライティングツール", page_icon="📝")
render_sidebar_settings()

st.title("📝 ブログ記事作成")
st.caption("トピックとキーワードを入力すると、ブログ記事の下書きを生成します。")

with st.form("blog_form"):
    topic = st.text_input("記事のトピック・タイトル案 *", placeholder="例：在宅ワークの生産性を上げる方法")
    keywords = st.text_input("含めたいキーワード（カンマ区切り・任意）", placeholder="例：時間管理, 集中力, ツール")
    audience = st.text_input("想定読者（任意）", placeholder="例：在宅勤務を始めたばかりの会社員")

    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("トーン", ["フレンドリー", "専門的・信頼感", "カジュアル", "フォーマル"])
    with col2:
        length = st.selectbox("文字数の目安", ["600字程度", "1000字程度", "1500字程度", "2000字以上"])

    outline_request = st.text_area(
        "構成の希望（任意）",
        placeholder="例：導入 → 3つの方法（見出し付き）→ まとめ、の構成にしてください",
        height=100,
    )
    submitted = st.form_submit_button("記事を生成する", type="primary")

if submitted:
    if not topic.strip():
        st.error("記事のトピックを入力してください。")
    elif not require_api_key():
        pass
    else:
        api_key, model = get_settings()
        prompt = f"""あなたはプロのブログライターです。以下の条件に沿って、日本語のブログ記事を作成してください。

# トピック
{topic}

# 含めたいキーワード
{keywords or "指定なし"}

# 想定読者
{audience or "指定なし"}

# トーン
{tone}

# 文字数の目安
{length}

# 構成の希望
{outline_request or "Markdownの見出し（##）を使い、導入・本文（複数の見出しに分ける）・まとめの構成にしてください。"}

読みやすい段落分けと適切な見出しを使い、実用的で読者の役に立つ内容にしてください。
"""
        st.divider()
        try:
            with st.spinner("記事を生成中..."):
                result = st.write_stream(generate_stream(api_key, model, prompt, temperature=0.8))
            st.session_state["blog_result"] = result
        except GeminiError as e:
            st.error(str(e))

if st.session_state.get("blog_result"):
    st.download_button(
        "テキストとしてダウンロード",
        st.session_state["blog_result"],
        file_name="blog_article.md",
    )

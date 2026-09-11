import streamlit as st

from utils.common import get_settings, render_sidebar_settings, require_api_key
from utils.gemini_client import GeminiError, generate_stream

st.set_page_config(page_title="タイトル生成 | AIライティングツール", page_icon="💡")
render_sidebar_settings()

st.title("💡 タイトル生成")
st.caption("記事やコンテンツの概要を入力すると、複数のタイトル案を生成します。")

STYLES = [
    "SEOを意識した検索されやすいタイトル",
    "思わずクリックしたくなるキャッチーなタイトル",
    "誠実で信頼感のあるタイトル",
    "疑問形で興味を引くタイトル",
    "数字を使った具体的なタイトル",
]

with st.form("title_form"):
    content = st.text_area(
        "記事・コンテンツの概要 *",
        height=180,
        placeholder="例：在宅ワークで集中力を保つための3つの習慣について書いた記事",
    )
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("タイトルの雰囲気", STYLES)
    with col2:
        num_titles = st.number_input("生成する案の数", min_value=1, max_value=10, value=5, step=1)

    max_length = st.text_input("文字数の目安（任意）", placeholder="例：32字以内")
    submitted = st.form_submit_button("タイトルを生成する", type="primary")

if submitted:
    if not content.strip():
        st.error("記事・コンテンツの概要を入力してください。")
    elif not require_api_key():
        pass
    else:
        api_key, model = get_settings()
        prompt = f"""以下のコンテンツ概要をもとに、タイトル案を{num_titles}個考えてください。

# コンテンツの概要
{content}

# タイトルの雰囲気
{style}

# 文字数の目安
{max_length or "指定なし"}

番号付きリストの形式で、タイトル案のみを出力してください。説明や前置きは不要です。
"""
        st.divider()
        try:
            with st.spinner("タイトルを生成中..."):
                result = st.write_stream(generate_stream(api_key, model, prompt, temperature=0.9))
            st.session_state["titles_result"] = result
        except GeminiError as e:
            st.error(str(e))

if st.session_state.get("titles_result"):
    st.download_button(
        "テキストとしてダウンロード",
        st.session_state["titles_result"],
        file_name="titles.txt",
    )

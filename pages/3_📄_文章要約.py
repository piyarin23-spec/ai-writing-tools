import streamlit as st

from utils.common import get_settings, render_sidebar_settings, require_api_key
from utils.gemini_client import GeminiError, generate_stream

st.set_page_config(page_title="文章要約 | AIライティングツール", page_icon="📄")
render_sidebar_settings()

st.title("📄 文章要約")
st.caption("長文を貼り付けると、指定した長さ・形式で要約します。")

uploaded = st.file_uploader("テキストファイルを読み込む（任意・.txt / .md）", type=["txt", "md"])
default_text = ""
if uploaded is not None:
    default_text = uploaded.read().decode("utf-8", errors="ignore")

with st.form("summary_form"):
    text = st.text_area("要約したい文章 *", value=default_text, height=280)

    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("要約の長さ", ["1文で", "3行程度で", "100字程度", "300字程度", "500字程度"])
    with col2:
        output_format = st.selectbox("出力形式", ["文章形式", "箇条書き形式"])

    keep_info = st.text_input("特に残したい情報（任意）", placeholder="例：数値データ、固有名詞、結論")
    submitted = st.form_submit_button("要約する", type="primary")

if submitted:
    if not text.strip():
        st.error("要約したい文章を入力してください。")
    elif not require_api_key():
        pass
    else:
        api_key, model = get_settings()
        prompt = f"""以下の文章を要約してください。

# 要約対象の文章
{text}

# 要約の長さ
{length}

# 出力形式
{output_format}

# 特に残したい情報
{keep_info or "指定なし（重要なポイントを優先してください）"}

余計な前置き（「以下に要約します」等）は不要です。要約結果のみを出力してください。
"""
        st.divider()
        try:
            with st.spinner("要約中..."):
                result = st.write_stream(generate_stream(api_key, model, prompt, temperature=0.3))
            st.session_state["summary_result"] = result
        except GeminiError as e:
            st.error(str(e))

if st.session_state.get("summary_result"):
    st.download_button(
        "テキストとしてダウンロード",
        st.session_state["summary_result"],
        file_name="summary.txt",
    )

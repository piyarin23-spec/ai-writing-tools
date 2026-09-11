import streamlit as st

from utils.common import get_settings, render_sidebar_settings, require_api_key
from utils.gemini_client import GeminiError, generate_stream

st.set_page_config(page_title="文体変換 | AIライティングツール", page_icon="🔄")
render_sidebar_settings()

st.title("🔄 文体変換")
st.caption("文章を貼り付けると、指定したスタイルの文体に変換します。内容は変えません。")

STYLES = [
    "です・ます調（丁寧）",
    "である調（論文・レポート風）",
    "ビジネスメール調（丁寧語・敬語）",
    "カジュアル・フレンドリー",
    "SNS向け（絵文字・くだけた表現あり）",
    "やさしい言葉（子供や初心者向け）",
]

with st.form("style_form"):
    text = st.text_area("変換したい文章 *", height=280)
    style = st.selectbox("変換先のスタイル", STYLES)
    extra_instruction = st.text_input("追加の指示（任意）", placeholder="例：一人称は「私」にしてください")
    submitted = st.form_submit_button("変換する", type="primary")

if submitted:
    if not text.strip():
        st.error("変換したい文章を入力してください。")
    elif not require_api_key():
        pass
    else:
        api_key, model = get_settings()
        prompt = f"""以下の文章の文体を、指定したスタイルに変換してください。内容や意味は変えないでください。

# 元の文章
{text}

# 変換先のスタイル
{style}

# 追加の指示
{extra_instruction or "指定なし"}

変換後の文章のみを出力してください。前置きや説明は不要です。
"""
        st.divider()
        try:
            with st.spinner("変換中..."):
                result = st.write_stream(generate_stream(api_key, model, prompt, temperature=0.5))
            st.session_state["style_result"] = result
        except GeminiError as e:
            st.error(str(e))

if st.session_state.get("style_result"):
    st.download_button(
        "テキストとしてダウンロード",
        st.session_state["style_result"],
        file_name="style_converted.txt",
    )

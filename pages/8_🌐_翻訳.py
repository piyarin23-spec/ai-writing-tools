import streamlit as st

from utils.common import get_settings, render_sidebar_settings, require_api_key
from utils.gemini_client import GeminiError, generate_stream

st.set_page_config(page_title="翻訳 | AIライティングツール", page_icon="🌐")
render_sidebar_settings()

st.title("🌐 翻訳")
st.caption("文章を貼り付けると、自然な文章として翻訳します。")

LANGUAGES = ["英語", "日本語", "中国語（簡体字）", "中国語（繁体字）", "韓国語", "フランス語", "スペイン語", "ドイツ語", "その他（自由入力）"]

with st.form("translate_form"):
    text = st.text_area("翻訳したい文章 *", height=280)

    col1, col2 = st.columns(2)
    with col1:
        target_lang = st.selectbox("翻訳先の言語", LANGUAGES)
        custom_lang = ""
        if target_lang == "その他（自由入力）":
            custom_lang = st.text_input("言語名を入力", placeholder="例：タイ語")
    with col2:
        tone = st.selectbox("文体", ["自然な文章", "ビジネス調・フォーマル", "カジュアル"])

    submitted = st.form_submit_button("翻訳する", type="primary")

if submitted:
    final_lang = custom_lang.strip() if target_lang == "その他（自由入力）" else target_lang
    if not text.strip():
        st.error("翻訳したい文章を入力してください。")
    elif not final_lang:
        st.error("翻訳先の言語を入力してください。")
    elif not require_api_key():
        pass
    else:
        api_key, model = get_settings()
        prompt = f"""以下の文章を{final_lang}に翻訳してください。

# 原文
{text}

# 文体
{tone}

直訳ではなく、{final_lang}として自然に読める翻訳にしてください。
翻訳結果のみを出力し、前置きや説明は不要です。
"""
        st.divider()
        try:
            with st.spinner("翻訳中..."):
                result = st.write_stream(generate_stream(api_key, model, prompt, temperature=0.3))
            st.session_state["translation_result"] = result
        except GeminiError as e:
            st.error(str(e))

if st.session_state.get("translation_result"):
    st.download_button(
        "テキストとしてダウンロード",
        st.session_state["translation_result"],
        file_name="translation.txt",
    )

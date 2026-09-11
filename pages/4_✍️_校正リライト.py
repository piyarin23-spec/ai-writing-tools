import streamlit as st

from utils.common import get_settings, render_sidebar_settings, require_api_key
from utils.gemini_client import GeminiError, generate_stream

st.set_page_config(page_title="校正・リライト | AIライティングツール", page_icon="✍️")
render_sidebar_settings()

st.title("✍️ 校正・リライト")
st.caption("文章を貼り付けると、誤字脱字や表現をチェックして修正します。")

with st.form("proofread_form"):
    text = st.text_area("校正したい文章 *", height=280)

    checks = st.multiselect(
        "チェック項目",
        ["誤字脱字", "文法・助詞の誤り", "敬語表現", "冗長な表現の簡潔化", "句読点・読みやすさ"],
        default=["誤字脱字", "文法・助詞の誤り", "句読点・読みやすさ"],
    )
    output_mode = st.radio(
        "出力形式",
        ["修正後の文章のみ", "修正後の文章 ＋ 修正点の説明"],
        horizontal=True,
    )
    extra_instruction = st.text_input("追加の指示（任意）", placeholder="例：全体的にもう少し柔らかい表現にしてほしい")
    submitted = st.form_submit_button("校正する", type="primary")

if submitted:
    if not text.strip():
        st.error("校正したい文章を入力してください。")
    elif not require_api_key():
        pass
    else:
        api_key, model = get_settings()
        checks_str = "、".join(checks) if checks else "誤字脱字・文法・読みやすさ全般"
        explain_part = (
            "修正後の文章を「## 修正後の文章」という見出しの下に出力し、"
            "続けて「## 修正点」という見出しの下に、どこをどう直したかを箇条書きで説明してください。"
            if output_mode == "修正後の文章 ＋ 修正点の説明"
            else "修正後の文章のみを出力してください。見出しや説明、前置きは不要です。"
        )
        prompt = f"""以下の文章を校正・リライトしてください。

# 元の文章
{text}

# チェック項目
{checks_str}

# 追加の指示
{extra_instruction or "指定なし"}

# 出力形式
{explain_part}

文章の意味や意図は変えないでください。
"""
        st.divider()
        try:
            with st.spinner("校正中..."):
                result = st.write_stream(generate_stream(api_key, model, prompt, temperature=0.3))
            st.session_state["proofread_result"] = result
        except GeminiError as e:
            st.error(str(e))

if st.session_state.get("proofread_result"):
    st.download_button(
        "テキストとしてダウンロード",
        st.session_state["proofread_result"],
        file_name="proofread.txt",
    )

import streamlit as st

from utils.common import get_settings, render_sidebar_settings, require_api_key
from utils.gemini_client import GeminiError, generate_stream

st.set_page_config(page_title="SNS投稿文 | AIライティングツール", page_icon="🐦")
render_sidebar_settings()

st.title("🐦 SNS投稿文作成")
st.caption("伝えたい内容を入力すると、媒体に合わせた投稿文を作成します。")

PLATFORM_INFO = {
    "X（Twitter）": "全角140字程度を目安に、簡潔でインパクトのある文章にしてください。",
    "Instagram": "少し長めの説明文＋改行を使い、最後にハッシュタグをまとめてください。",
    "Facebook": "丁寧で少し長めの文章でも構いません。背景や気持ちも交えてください。",
    "LinkedIn": "ビジネス向けのトーンで、学びや気づきを含めた文章にしてください。",
    "Threads": "カジュアルで会話的な短文にしてください。",
}

with st.form("sns_form"):
    content = st.text_area("投稿したい内容 *", height=160, placeholder="例：新しいブログ記事を公開したことを知らせたい")

    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("プラットフォーム", list(PLATFORM_INFO.keys()))
    with col2:
        tone = st.selectbox("トーン", ["フレンドリー", "専門的", "ユーモラス", "フォーマル", "熱意を込めて"])

    col3, col4 = st.columns(2)
    with col3:
        include_hashtags = st.checkbox("ハッシュタグを含める", value=True)
    with col4:
        include_emoji = st.checkbox("絵文字を使う", value=True)

    num_variations = st.number_input("生成するバリエーション数", min_value=1, max_value=5, value=3, step=1)
    submitted = st.form_submit_button("投稿文を生成する", type="primary")

if submitted:
    if not content.strip():
        st.error("投稿したい内容を入力してください。")
    elif not require_api_key():
        pass
    else:
        api_key, model = get_settings()
        prompt = f"""以下の内容をもとに、SNS投稿文を{num_variations}パターン作成してください。

# 投稿したい内容
{content}

# プラットフォーム
{platform}
{PLATFORM_INFO[platform]}

# トーン
{tone}

# ハッシュタグ
{"文末に3〜5個程度含めてください。" if include_hashtags else "含めないでください。"}

# 絵文字
{"適度に使ってください。" if include_emoji else "使わないでください。"}

各パターンを「---」で区切って出力してください。前置きや説明は不要です。
"""
        st.divider()
        try:
            with st.spinner("投稿文を生成中..."):
                result = st.write_stream(generate_stream(api_key, model, prompt, temperature=0.9))
            st.session_state["sns_result"] = result
        except GeminiError as e:
            st.error(str(e))

if st.session_state.get("sns_result"):
    st.download_button(
        "テキストとしてダウンロード",
        st.session_state["sns_result"],
        file_name="sns_post.txt",
    )

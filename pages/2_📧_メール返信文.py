import streamlit as st

from utils.common import get_settings, render_sidebar_settings, require_api_key
from utils.gemini_client import GeminiError, generate_stream

st.set_page_config(page_title="メール返信文 | AIライティングツール", page_icon="📧")
render_sidebar_settings()

st.title("📧 メール返信文作成")
st.caption("受信したメールと返信の要点を入力すると、返信文の下書きを作成します。")

with st.form("email_form"):
    received_email = st.text_area(
        "受信したメールの本文 *",
        height=200,
        placeholder="ここに受信したメールの本文を貼り付けてください",
    )
    key_points = st.text_area(
        "返信で伝えたい要点 *",
        height=120,
        placeholder="例：提案内容に同意する、来週の火曜14時なら打ち合わせ可能、資料は明日送る",
    )

    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("トーン", ["丁寧・ビジネス", "フォーマル（かしこまった敬語）", "ややカジュアル", "感謝を強調"])
    with col2:
        reply_lang = st.selectbox("返信の言語", ["日本語", "英語"])

    signature = st.text_input("署名（任意・文末に入れる名前など）", placeholder="例：山田太郎")
    submitted = st.form_submit_button("返信文を生成する", type="primary")

if submitted:
    if not received_email.strip() or not key_points.strip():
        st.error("受信メールの本文と、返信で伝えたい要点の両方を入力してください。")
    elif not require_api_key():
        pass
    else:
        api_key, model = get_settings()
        prompt = f"""あなたは丁寧なビジネスコミュニケーションのプロです。以下の受信メールに対する返信メールの本文を作成してください。

# 受信したメール
{received_email}

# 返信で伝えたい要点
{key_points}

# トーン
{tone}

# 署名（あれば文末に含める。なければ「よろしくお願いいたします。」等で締める）
{signature or "指定なし"}

# 返信の言語
{reply_lang}

件名は不要です。宛名（受信メールから推測できれば「〇〇様」のように使用）から書き出し、
本文のみを出力してください。
"""
        st.divider()
        try:
            with st.spinner("返信文を生成中..."):
                result = st.write_stream(generate_stream(api_key, model, prompt, temperature=0.6))
            st.session_state["email_result"] = result
        except GeminiError as e:
            st.error(str(e))

if st.session_state.get("email_result"):
    st.download_button(
        "テキストとしてダウンロード",
        st.session_state["email_result"],
        file_name="email_reply.txt",
    )

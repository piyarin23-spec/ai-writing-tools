"""ページ共通のサイドバー設定・ヘルパー関数。"""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from utils.gemini_client import GeminiError, list_models

load_dotenv()

# APIキー未入力時、またはモデル一覧の取得に失敗したときだけ使うフォールバック候補。
# Geminiのモデルは随時廃止・追加されるため、通常はAPIから取得した一覧を優先する。
FALLBACK_MODELS = {
    "Gemini 3.6 Flash（フォールバック）": "gemini-3.6-flash",
}

# 一覧の中にこのモデルIDがあれば、既定選択として優先する
# （無料枠のないモデルや廃止予定モデルが偶然先頭に来て、既定選択になるのを防ぐため）。
PREFERRED_DEFAULT_MODEL_ID = "gemini-3.6-flash"


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_model_options(api_key: str) -> dict[str, str]:
    models = list_models(api_key)
    if not models:
        raise GeminiError("利用可能なモデルが見つかりませんでした。")
    return {f"{display_name}（{model_id}）": model_id for display_name, model_id in models}


def render_sidebar_settings() -> None:
    """全ページ共通のAPIキー・モデル選択サイドバーを描画する。"""
    with st.sidebar:
        st.header("⚙️ 設定")

        default_key = os.environ.get("GEMINI_API_KEY", "")
        api_key = st.text_input(
            "Gemini APIキー",
            value=st.session_state.get("api_key", default_key),
            type="password",
            help="Google AI Studio (https://aistudio.google.com/apikey) で取得できます。",
        )
        st.session_state["api_key"] = api_key

        model_options = FALLBACK_MODELS
        if api_key:
            try:
                model_options = _fetch_model_options(api_key)
            except GeminiError:
                st.caption("⚠️ モデル一覧を取得できなかったため、既定の候補を表示しています。")

        labels = list(model_options.keys())
        if st.session_state.get("model_label") in labels:
            current_label = st.session_state["model_label"]
        else:
            preferred_label = next(
                (label for label, model_id in model_options.items() if model_id == PREFERRED_DEFAULT_MODEL_ID),
                None,
            )
            current_label = preferred_label or labels[0]
        index = labels.index(current_label)
        model_label = st.selectbox("使用するモデル", labels, index=index)
        st.session_state["model_label"] = model_label
        st.session_state["model"] = model_options[model_label]

        st.divider()
        st.caption(
            "個人利用向けのローカルツールです。データベースや認証機能はありません。"
            "入力内容や生成結果はセッション内にのみ保持され、保存されません。"
        )


def get_settings() -> tuple[str, str]:
    api_key = st.session_state.get("api_key", "")
    model = st.session_state.get("model", "gemini-3.6-flash")
    return api_key, model


def require_api_key() -> bool:
    api_key, _ = get_settings()
    if not api_key:
        st.warning("サイドバーにGemini APIキーを入力してください。")
        return False
    return True

"""Gemini APIとのやり取りをまとめたヘルパーモジュール。"""
from __future__ import annotations

from typing import Iterator, Optional

from google import genai
from google.genai import types


class GeminiError(Exception):
    """Gemini API呼び出しに関するエラー。"""


def get_client(api_key: str) -> genai.Client:
    if not api_key:
        raise GeminiError("APIキーが設定されていません。サイドバーから入力してください。")
    return genai.Client(api_key=api_key)


def list_models(api_key: str) -> list[tuple[str, str]]:
    """テキスト生成に使える利用可能なモデルを (表示名, モデルID) のタプル一覧で返す。

    モデルIDは廃止・追加が随時発生するため、ハードコードせずAPIから取得する。
    """
    client = get_client(api_key)
    try:
        raw_models = list(client.models.list())
    except Exception as e:
        raise GeminiError(f"モデル一覧の取得に失敗しました: {e}") from e

    excluded_keywords = ("embedding", "aqa", "imagen", "veo", "gemma", "tts")
    results: list[tuple[str, str]] = []
    seen: set[str] = set()
    for m in raw_models:
        name = getattr(m, "name", "") or ""
        model_id = name.split("/", 1)[-1] if name else ""
        if not model_id or model_id in seen:
            continue
        if any(keyword in model_id for keyword in excluded_keywords):
            continue

        actions = (
            getattr(m, "supported_actions", None)
            or getattr(m, "supported_generation_methods", None)
            or []
        )
        if actions and "generateContent" not in actions:
            continue

        seen.add(model_id)
        display_name = getattr(m, "display_name", None) or model_id
        results.append((display_name, model_id))

    # 「新しいバージョン番号を優先」等のヒューリスティックは、廃止予定モデルや
    # 無料枠が0のモデル（例: gemini-omni-flash）を誤って先頭に出すことがあるため使わない。
    # 並び順はアルファベット順のみとし、実際にどれを既定選択にするかはsidebar側で決める。
    results.sort(key=lambda item: item[1])
    return results


def _build_config(
    system_instruction: Optional[str],
    temperature: float,
) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
    )


def generate_stream(
    api_key: str,
    model: str,
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
) -> Iterator[str]:
    """テキストをストリーミング生成し、チャンクごとに文字列を返す。"""
    client = get_client(api_key)
    config = _build_config(system_instruction, temperature)
    try:
        stream = client.models.generate_content_stream(
            model=model,
            contents=prompt,
            config=config,
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text
    except GeminiError:
        raise
    except Exception as e:
        raise GeminiError(f"Gemini APIの呼び出しに失敗しました: {e}") from e


def generate_text(
    api_key: str,
    model: str,
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
) -> str:
    """テキストを一括生成する（ストリーミングしない）。"""
    client = get_client(api_key)
    config = _build_config(system_instruction, temperature)
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        return response.text or ""
    except GeminiError:
        raise
    except Exception as e:
        raise GeminiError(f"Gemini APIの呼び出しに失敗しました: {e}") from e

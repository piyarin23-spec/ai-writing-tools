# CLAUDE.md

このファイルは、このリポジトリでコードを扱う際にClaude Code (claude.ai/code) が参照するガイドです。

## これは何か

Python + Streamlit + Gemini API（`google-genai` SDK）で作られた、個人用のAIライティングツールです。ブログ記事作成、メール返信文作成、要約、校正・リライト、文体変換、タイトル生成、SNS投稿文作成、翻訳といった複数のライティング支援機能を、1つのマルチページアプリにまとめています。意図的に**データベースも認証機能も持たせていません** — ローカル専用で、状態はすべて1回の実行中だけブラウザセッション（`st.session_state`）に保持されます。

## コマンド

セットアップ（Windows、このディレクトリで実行）:
```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

アプリの起動:
```
.venv\Scripts\streamlit run app.py
```
`http://localhost:8501` でアプリが開きます。マシンで初回起動する際、Streamlitがオンボーディング用のメールアドレスを標準入力で尋ねてくることがあります。非対話的に起動する場合は `~/.streamlit/credentials.toml` に `[general]\nemail = ""` を書いておくとこのプロンプトをスキップできます。

全ファイルの構文チェック（テストスイートは存在しません）:
```
.venv\Scripts\python -m py_compile app.py utils\*.py pages\*.py
```

このプロジェクトにはリンター・フォーマッター・テストスイートは設定されていません。

## 設定

Gemini APIキーの解決順序（`utils/common.py` の `render_sidebar_settings` を参照）:
1. すでに `st.session_state["api_key"]` に入っている値（今のセッションでサイドバーに入力済みの場合）
2. `python-dotenv` によって `.env` ファイルから読み込まれる環境変数 `GEMINI_API_KEY`（`.env.example` を参照）

サイドバーのモデル選択（同じく `utils/common.py`）は、日本語の表示ラベルをGeminiのモデルID（`gemini-2.5-flash`、`gemini-2.5-pro`、`gemini-2.0-flash`）に対応付け、選ばれたIDを `st.session_state["model"]` に保存します。

## アーキテクチャ

**Streamlitのマルチページアプリ構成。** `app.py` がホームページで、`pages/` 以下の各ファイルはStreamlitによって自動的にサイドバーのナビ項目として登録されます。表示順はファイル名の先頭の番号（`1_📝_...py` 〜 `8_🌐_...py`）で決まります。各ページは独立したスクリプトであり、操作のたびにStreamlitが上から下まで再実行します — `st.session_state` 以外に、ページ間で状態を保持する共有プロセスやクラスは存在しません。

**`utils/` 以下の共有モジュール**（`app.py` と全ページからimportされます）:
- `utils/common.py` — `render_sidebar_settings()` はAPIキー・モデル選択のサイドバーを描画します（各ページの先頭で呼び出す必要があります）。`get_settings()` は `(api_key, model)` を取得します。`require_api_key()` はAPIキー未設定時に警告を表示し `False` を返します。どのページも「フォームを作り、送信時にGemini呼び出しの前に `require_api_key()` でチェックする」というガード方式を採っています。
- `utils/gemini_client.py` — `google.genai` SDKの薄いラッパーです。`generate_stream(...)` はテキストチャンクをyieldし（`st.write_stream(...)` と組み合わせて逐次表示するのに使う）、`generate_text(...)` は文字列を一括で返します。どちらもSDKの例外をすべて `GeminiError` にラップしており、各ページはこれを捕捉して `st.error(...)` を表示し、クラッシュを防いでいます。

**各ページ共通のパターン。** `pages/` 内のどのページも同じ構造です: `st.set_page_config(...)` → `render_sidebar_settings()` → 機能固有の入力を集める `st.form(...)` → 送信時に入力値と `require_api_key()` を検証 → フォーム入力を `# 見出し` セクションとして埋め込んだ日本語のプロンプト文字列を組み立てる → `st.write_stream(...)` の中で `generate_stream(...)` を呼ぶ → 結果をページ固有の `st.session_state` キー（例: `blog_result`、`email_result`）に保存してリラン後も残るようにする → `st.download_button(...)` で結果をダウンロード可能にする。新しいライティング機能を追加する場合は、新しいパターンを考案するのではなく、既存ページ（シンプルな例として `pages/3_📄_文章要約.py`）の構造をコピーしてください。

プロンプトは（別の場所でテンプレート化するのではなく）各ページファイル内でプレーンなf文字列として組み立てられています — これは1機能1ファイルという構成に合わせた意図的な設計です。新しい機能を追加する際も、テンプレート層を導入するのではなく、この方式に合わせてください。

# AIライティングツール

Gemini APIを使った、個人用オールインワン・ライティング支援ツールです。
Python + Streamlit で構築されており、データベースや認証機能は使用していません。

## 機能

- 📝 ブログ記事作成
- 📧 メール返信文作成
- 📄 文章要約
- ✍️ 校正・リライト
- 🔄 文体変換
- 💡 タイトル生成
- 🐦 SNS投稿文作成
- 🌐 翻訳

## セットアップ

1. 依存パッケージをインストールします。

   ```bash
   pip install -r requirements.txt
   ```

2. Gemini APIキーを設定します（どちらか一方でOKです）。

   - `.env.example` を `.env` にコピーし、`GEMINI_API_KEY` に自分のAPIキーを設定する
   - もしくは、アプリ起動後にサイドバーへ直接APIキーを入力する

   APIキーは [Google AI Studio](https://aistudio.google.com/apikey) から取得できます。

3. アプリを起動します。

   ```bash
   streamlit run app.py
   ```

## 技術スタック

- Python
- Streamlit
- Gemini API（`google-genai` SDK）

## 構成

```
app.py                  # ホーム画面（サイドバー共通設定）
pages/                  # 各ライティング機能のページ
utils/
  common.py             # サイドバー設定・共通ヘルパー
  gemini_client.py      # Gemini API呼び出しのラッパー
```

## 注意事項

個人利用を想定したローカルツールです。ユーザー認証やデータの永続化は行っておらず、
入力内容・生成結果はブラウザのセッション内にのみ保持されます（アプリを閉じると消えます）。

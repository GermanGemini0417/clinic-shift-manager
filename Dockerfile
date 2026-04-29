# Pythonの軽量版を使用
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY . .

# ポート8080でFastAPIを起動（Cloud Runのデフォルト）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
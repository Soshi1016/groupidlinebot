#2025/07/15/21:30
import os
import json
import base64
import hashlib
import hmac
from flask import Flask, request, abort

app = Flask(__name__)

# 環境変数からLINEのチャネルシークレットを取得
# このコードではメッセージの返信はしないため、アクセストークンは不要
channel_secret = os.getenv("LINE_CHANNEL_SECRET")

if channel_secret is None:
    print("環境変数 'LINE_CHANNEL_SECRET' が設定されていません。")
    abort(500)

# ルートエンドポイント（起動確認用）
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running (manual handler)."

# Webhookエンドポイント（LINEからのリクエストを受け取る）
@app.route("/callback", methods=["POST"])
def callback():
    # リクエストヘッダーから署名を取得
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        abort(400)

    # リクエストボディをバイト列として取得（重要）
    body_bytes = request.get_data()

    # --- 署名検証 ---
    # チャネルシークレットをキーとして、リクエストボディからHMAC-SHA256のハッシュを計算
    hash_obj = hmac.new(channel_secret.encode('utf-8'), body_bytes, hashlib.sha256).digest()
    # 計算したハッシュをBase64エンコード
    generated_signature = base64.b64encode(hash_obj).decode('utf-8')

    # 署名が一致するかどうかを比較
    if signature != generated_signature:
        print("署名の検証に失敗しました。")
        abort(400) # 署名が不正な場合は400エラー

    # --- 署名検証ここまで ---

    # リクエストボディをJSONとしてパース
    try:
        # バイト列をUTF-8でデコードしてからJSONとして読み込む
        body_json = json.loads(body_bytes.decode('utf-8'))
    except json.JSONDecodeError:
        print("JSONのパースに失敗しました。")
        abort(400)

    # イベントをループして処理
    for event in body_json.get('events', []):
        # イベントのソースタイプを確認
        source = event.get('source', {})
        source_type = source.get('type')

        # ソースが 'group' の場合
        if source_type == 'group':
            group_id = source.get('groupId')
            if group_id:
                # Renderのログに出力する
                print(f"--- Group Event Detected ---")
                print(f"  Event Type: {event.get('type')}")
                print(f"  Group ID: {group_id}")
                print(f"--------------------------")
        
        # ソースが 'user' の場合
        elif source_type == 'user':
            user_id = source.get('userId')
            if user_id:
                print(f"--- User Event Detected ---")
                print(f"  Event Type: {event.get('type')}")
                print(f"  User ID: {user_id}")
                print(f"-------------------------")

    return "OK"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

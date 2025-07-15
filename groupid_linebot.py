import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 環境変数から読み込み（Renderでは.envに記載する）
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
if not CHANNEL_SECRET:
    raise EnvironmentError("LINE_CHANNEL_SECRET が設定されていません。")

handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("署名が無効です。")
        abort(400)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    if hasattr(event.source, 'group_id'):
        group_id = event.source.group_id
        user_id = event.source.user_id
        print("=" * 40)
        print("🎉 メッセージをグループから受信しました！")
        print(f"  グループID: {group_id}")
        print(f"  メッセージ送信者のユーザーID: {user_id}")
        print("=" * 40)
        print("上記の「グループID」を jkk_monitor.py に設定してください。")
    elif hasattr(event.source, 'user_id'):
        user_id = event.source.user_id
        print("=" * 40)
        print("ℹ️ メッセージを個人ユーザーから受信しました。")
        print(f"  ユーザーID: {user_id}")
        print("=" * 40)
    else:
        print("未知のソースからのイベントです:", event.source)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

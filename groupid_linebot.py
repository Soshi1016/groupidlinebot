import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 環境変数からLINEのアクセストークンとシークレットを取得
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("LINE_CHANNEL_SECRET")

if channel_secret is None or channel_access_token is None:
    print("環境変数が設定されていません。")
    abort(500)

# LINE Botの設定
handler = WebhookHandler(channel_secret)
configuration = Configuration(access_token=channel_access_token)
line_bot_api = MessagingApi(configuration)

# ルートエンドポイント（起動確認用）
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running."

# Webhookエンドポイント（LINEからのリクエストを受け取る）
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# メッセージイベントのハンドラ（テキスト受信時の応答）
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    reply_token = event.reply_token

    # 応答するテキスト
    response_text = f"「{user_message}」と受け取りました！"

    line_bot_api.reply_message(
        reply_token,
        [
            {
                "type": "text",
                "text": response_text
            }
        ]
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

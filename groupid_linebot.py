import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler, LineBotApi
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 環境変数から読み込み
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')

if CHANNEL_SECRET is None or CHANNEL_ACCESS_TOKEN is None:
    print('FATAL ERROR: Required environment variables are not set.')
    exit(1)

handler = WebhookHandler(CHANNEL_SECRET)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature.")
        abort(400)
    except Exception as e:
        print(f"An error occurred: {e}")
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    message_text = event.message.text

    if hasattr(event.source, 'group_id'):
        group_id = event.source.group_id
        user_id = event.source.user_id
        print("="*40)
        print("🎉 Received a message from a group!")
        print(f"  Group ID: {group_id}")
        print(f"  Sender User ID: {user_id}")
        print("="*40)
        print("Please set the 'Group ID' above to your jkk_monitor.py.")
    elif hasattr(event.source, 'user_id'):
        user_id = event.source.user_id
        print("="*40)
        print("ℹ️ Received a message from a personal user.")
        print(f"  User ID: {user_id}")
        print("="*40)
        # ユーザーに返信（確認用）
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="受け取りました！")]
            )
        )
    else:
        print("Received an event from an unknown source:", event.source)

# Render用ポート取得と起動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

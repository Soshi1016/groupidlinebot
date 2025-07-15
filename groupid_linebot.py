import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 環境変数からチャネルシークレットを取得
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET', None)

# チャネルシークレットが設定されていない場合、エラーを出して起動を失敗させる
if CHANNEL_SECRET is None:
    print('Error: Specify CHANNEL_SECRET as an environment variable.')
    exit(1)

handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("署名が無効です。チャネルシークレットが正しいか確認してください。")
        abort(400)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # event.source オブジェクトが 'group_id' 属性を持っているかで、グループからのメッセージかを判断する
    if hasattr(event.source, 'group_id'):
        group_id = event.source.group_id
        user_id = event.source.user_id
        print("="*40)
        print("🎉 メッセージをグループから受信しました！")
        print(f"  グループID: {group_id}")
        print(f"  メッセージ送信者のユーザーID: {user_id}")
        print("="*40)
        print("上記の「グループID」を jkk_monitor.py に設定してください。")
    elif hasattr(event.source, 'user_id'):
        # 個人からのメッセージの場合
        user_id = event.source.user_id
        print("="*40)
        print("ℹ️ メッセージを個人ユーザーから受信しました。")
        print(f"  ユーザーID: {user_id}")
        print("="*40)
    else:
        print("未知のソースからのイベントです:", event.source)

# GunicornなどのWSGIサーバーからこの 'app' オブジェクトが直接実行されるため、
# `if __name__ == "__main__":` ブロックは不要です。

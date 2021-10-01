# from datetime import datetime
from database import Database
from address import Address

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (FlexSendMessage, MessageEvent, TextMessage,
                            TextSendMessage)

import os
import json
import requests as req


app = Flask(__name__)
db, ad = Database(), Address()

with open("flex.json", "r") as flex:
    container = json.load(flex)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/")
def hello_world():
    return "hello world!"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mes = event.message.text
    uid = event.source.user_id
    if mes == "hello":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=mes + "\n" + str(event))
        )

# ===============Create================
    if mes == "ウォレット作成":
        # print(event)
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text="create_req",
                contents=container["create"]
            )
        )

    if mes == "#create":
        if db.id_exists(uid) is True:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("既に作成されています！\n[ #address ]コマンドで確認してください。")
            )
        else:
            address = ad.create_address(uid)
            (container["create_success"]["body"]["contents"]
                [1]["contents"][0]["text"]) = address
            host = "https://liff.line.me/1656129059-zZA6Q0Jm/"
            uri = f"{host}?id={uid}#URL-flagment"
            (container["create_success"]["body"]["contents"]
                [1]["contents"][1]["action"]["uri"]) = uri
            db.add_new_wallet(uid, address, event.timestamp)
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="create_success",
                    contents=container["create_success"]
                )
            )

# ===============Transfer================
    if mes == "送金":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text="send",
                contents=container["transfer"]
            )
        )

    if mes.startswith("#send:") is True:
        # sample format: [ #send:{address}:{amount} ]
        try:
            mes = mes.split(":")
            if db.id_exists(uid):
                ad.send_coin(uid, mes[1], mes[2])
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="送金に成功しました！")
                )
        except Exception:
            print(Exception)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="送金に失敗しました。")
            )

# ===============Management================
    if mes == "ウォレット管理":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text="setting",
                contents=container["management"]
            )
        )

    if mes == "#address":
        address = db.get_address(uid)
        if address != "nodata":
            (container["address_check"]["body"]["contents"]
                [1]["contents"][0]["text"]) = address
            host = "https://liff.line.me/1656129059-zZA6Q0Jm/"
            uri = f"{host}?id={uid}#URL-flagment"
            (container["address_check"]["body"]["contents"]
                [1]["contents"][1]["action"]["uri"]) = uri
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="address_check",
                    contents=container["address_check"]
                )
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="no data!")
            )

    if mes == "#balance":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="データを取得中です...")
        )
        if db.id_exists(uid) is True:
            try:
                balance = ad.scan_wallet(uid)
                balance_name = balance[0]
                balance_value = balance[1]
                print(balance_name)
                print(balance_value)
                # 通貨名
                (container["balance"]["body"]["contents"][0]["text"]
                 ) = f"通貨名： {balance_name}"
                # 残高
                (container["balance"]["body"]["contents"][1]["text"]
                 ) = f"残高　： {balance_value}"
                # USD
                to_usd_rate = req.get(
                    "https://blockchain.info/ticker").json()["USD"]
                rate = 'レート： 1 BTC -> {} {}'.format(
                    to_usd_rate["15m"], to_usd_rate["symbol"])
                (container["balance"]["body"]["contents"][2]["text"]) = rate
                line_bot_api.push_message(
                    event.source.user_id,
                    FlexSendMessage(
                        alt_text="balance",
                        contents=container["balance"]
                    )
                )
            except IndexError as e:
                print(f"Catch IndexError: {e}")
                line_bot_api.push_message(
                    event.source.user_id,
                    TextSendMessage(text="取引履歴・残高はありません。")
                )

    if mes == "#contact":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text="contact",
                contents=container["contact"]
            )
        )

    if mes == "#delete":
        if db.delete_wallet(uid) and ad.delete_address(uid) is True:
            text = "ウォレットを削除しました。"
        else:
            text = "ウォレットがありません。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text)
        )


if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)

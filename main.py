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
        if db.searchIdsByDatabase(uid) is True:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("already created!")
            )
        else:
            address = ad.createAddress(uid)
            (container["create_success"]["body"]["contents"]
                [1]["contents"][0]["text"]) = address
            host = "https://liff.line.me/1656129059-zZA6Q0Jm/"
            uri = f"{host}?id={uid}#URL-flagment"
            (container["create_success"]["body"]["contents"]
                [1]["contents"][1]["action"]["uri"]) = uri
            db.insertToDatabase(uid, address, event.timestamp)
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="create_success",
                    contents=container["create_success"]
                )
            )

# ===============Transfer================
    if mes == "送金・受金":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
                alt_text="send",
                contents=container["transfer"]
            )
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
        address = db.searchAddressByDatabase(uid)
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

    if mes == "#delete":
        if db.deleteAddressInDatabase(uid) and ad.deleteAddress(uid) is True:
            text = "success"
        else:
            text = "no data!"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text)
        )


if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)

#!/usr/bin/env python3
# -*- coding: utf-8

from flask import Flask, request, abort

import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *



app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('OD5nHxJkXc8a/H0hSN2th2ZSVwP3bX96SYAWinqA2Pe2AR6Q8gQ8DWtlUJUZaJsjl5t0Jg7wwi5bRjxJqKNetgdytAgrRFLvXviZNa0DovKeuYyBClh/Zl030PYsFd9/g9o3dTihNqhDwuy9k6klbgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('6cd1ec3841120b5fbda2e33049e672b9')

def inv():
    try:
        import xml.etree.cElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET
        
    content=requests.get("http://invoice.etax.nat.gov.tw/invoice.xml")
    tree=ET.fromstring(content.text)
    items=list(tree.iter(tag="item"))
    return items

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #message = TextSendMessage(text=event.message.text)
    
    if event.message.text == "@本期號碼":
        items=inv()
        title=items[0][0].text
        ptext=items[0][2].text
        ptext=ptext.replace("<p>","").replace("</p>","\n")
        message=TextSendMessage(title+"月\n"+ptext[:-1])
        line_bot_api.reply_message(event.reply_token, message)
        
    if event.message.text == "@前期號碼":
        items=inv()
        message=""
        for i in range(1,3):
            title=items[i][0].text
            ptext=items[i][2].text
            ptext=ptext.replace("<p>","").replace("</p>","\n")
            message=message+title+"月\n"+ptext+"\n"
        message=TextSendMessage(message[:-2])
        line_bot_api.reply_message(event.reply_token, message)
    


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='127.0.0.1', port=port)    

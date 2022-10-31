#!/usr/bin/env python3
# -*- coding: utf-8
from __future__ import unicode_literals, print_function
from flask import Flask, request, abort, render_template, Response, jsonify

import cv2
import urllib.request
from bs4 import BeautifulSoup
import requests
import random
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




def inv(f, show):
    request_url = 'http://invoice.etax.nat.gov.tw/'+f #lastNumber.html

    # 取得HTML
    htmlContent = urllib.request.urlopen(request_url).read()
    soup = BeautifulSoup(htmlContent, "html.parser")

    subTitle = ['特別獎', '特獎', '頭獎'] # 獎項

    results = soup.find_all('a', {'class': 'etw-on'})
    months = soup.find_all('span', {'class': 'font-weight-bold'})#
    #print(results)
    number=[]
    i=0
    while i < len(months):
        if len(months[i].string)<8:
            number.append(months[i].string + months[i+1].string)
            i += 1
        else:
            number.append(months[i].string)
        i += 1
        if len(number) >= 5:
            break
    if not show:
        return number

    msg="最新一期統一發票開獎號碼 \n({0})：".format(results[0].string)
    index=0
    for item in number:
        if index < 3:
            msg += "\n"+subTitle[index]+"："
            index += 1
        msg += item + "\n"
    return msg

def lottery(x):
    ma="開獎號碼：\n獎號："
    if x==1:
        url="https://www.taiwanlottery.com.tw/lotto/Lotto649/history.aspx"#大樂透
        css="#Lotto649Control_history_dlQuery"
        r=6
    elif x==2:
        url="https://www.taiwanlottery.com.tw/lotto/superlotto638/history.aspx"#威力
        css="#SuperLotto638Control_history1_dlQuery"
        r=6
    elif x==3:
        url="https://www.taiwanlottery.com.tw/lotto/DailyCash/history.aspx"#539
        css="#D539Control_history1_dlQuery"
        r=5
    
    html=requests.get(url)
    sp=BeautifulSoup(html.text,"html.parser")
    data1=sp.select(css)
    
    data2=data1[0].find_all("td",{"class":"td_w font_black14b_center"})
    
    for i in range(r):
        data3=data2[i].find("span")
        ma+=data3.text+"  "
    if x==1 or x==2:
        ma+="\n"
        data2=data1[0].find("td",{"class":"td_w font_red14b_center"})
        ma+="特別號："+data2.find("span").text
    return ma

def ron(s,x,y):
    m=[0 for i in range(y+1)]
    i=0
    ma=s+"："
    while(i<x):
        ran=random.randint(1,y)
        if m[ran]==0:
            i+=1
            m[ran]
            ma+=str(ran)+"  "
    if x==6:
        ran=random.randint(1,8)
        if m[ran]==0:
            i+=1
            m[ran]
            ma+=str(ran)+"  "
    return ma+"\n(純屬練習切勿當真)"



@app.route('/')
def index():
    number=inv("", False)
    return render_template('index.html', number = number)


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
        message=TextSendMessage(inv("", True))
        line_bot_api.reply_message(event.reply_token, message)
        
    if event.message.text == "@前期號碼":
        message=TextSendMessage(inv("lastNumber.html", True))
        line_bot_api.reply_message(event.reply_token, message)
    
    if event.message.text == "@大樂透開獎":
        message=TextSendMessage(lottery(1))
        line_bot_api.reply_message(event.reply_token, message)
        
    if event.message.text == "@威力彩開獎":
        message=TextSendMessage(lottery(2))
        line_bot_api.reply_message(event.reply_token, message)
        
    if event.message.text == "@今彩539開獎":
        message=TextSendMessage(lottery(3))
        line_bot_api.reply_message(event.reply_token, message)
        
    if event.message.text == "@大樂透預測":
        message=TextSendMessage(ron("大樂透",7,49))
        line_bot_api.reply_message(event.reply_token, message)
        
    if event.message.text == "@威力彩預測":
        message=TextSendMessage(ron("威力彩",6,38))
        line_bot_api.reply_message(event.reply_token, message)
        
    if event.message.text == "@今彩539預測":
        message=TextSendMessage(ron("威力彩",5,39))
        line_bot_api.reply_message(event.reply_token, message)
        
    
    try:
        n=event.message.text
        l=int(n)
        if len(event.message.text)==3:
            ma=inv("", False)
            message="本期："
            for k in range(2):
                d=1
                for i, m in enumerate(ma):
                    #print(m)
                    if i==0:
                        if n in m[5:]:
                            message+="可能是特別獎"
                            d=0
                    elif i==1:
                        if n in m[5:]:
                            message+="可能是特獎"
                            d=0
                    elif i>=2:
                        if n in m[5:]:
                            message+="可能是頭獎"
                            d=0
                if d:
                    message+="共辜"
                if k:
                    break
                message+="\n前期："
                ma=inv("lastNumber.html", False)
            message=TextSendMessage(message)
            line_bot_api.reply_message(event.reply_token, message)
               
    except:
        print()
        
        
        
        
    if event.message.text=="@彩卷":
        carousel_template_message=TemplateSendMessage(
        alt_text="我是一個按鈕模板",
        template=CarouselTemplate(
            columns = [
                CarouselColumn(
                    thumbnail_image_url="https://i.imgur.com/v4CP0Tf.jpg",
                    title="大樂透",
                    text="請選擇",
                    actions=[
                        MessageTemplateAction(
                            label="本期號碼",
                            text="@大樂透開獎"
                        ),
                        MessageTemplateAction(
                            label="免費預測",
                            text="@大樂透預測"
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://i.imgur.com/l9kG2ez.png",
                    title="威力彩",
                    text="請選擇",
                    actions=[
                        MessageTemplateAction(
                            label="本期號碼",
                            text="@威力彩開獎"
                        ),
                        MessageTemplateAction(
                            label="免費預測",
                            text="@威力彩預測"
                        )
                    ]
                ),
                CarouselColumn (
                    thumbnail_image_url="https://i.imgur.com/WYhIabw.png",
                    title="今彩539",
                    text="請選擇",
                    actions=[
                        MessageAction(
                            label="本期號碼",
                            text="@今彩539開獎",
                        ),
                        MessageAction(
                            label="免費預測",
                            text="@今彩539預測",
                        ),
                    ]
                )
            ]
        )
        )
        line_bot_api.reply_message(event.reply_token,carousel_template_message)
            

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='127.0.0.1', port=port)    

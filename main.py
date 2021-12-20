# 必要モジュールの読み込み
import re
from flask import Flask, request, abort
import os
from bs4 import BeautifulSoup
from linebot.models.events import UnsendEvent
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import urllib3
import random
import sqlite3


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, QuickReplyButton, MessageAction, QuickReply, TextSendMessage, unsendEvent, JoinEvent 
)

driver_path = '/app/.chromedriver/bin/chromedriver'

options = Options()
options.add_argument('--disable-gpu');
options.add_argument('--disable-extensions');
options.add_argument('--proxy-server="direct://"');
options.add_argument('--proxy-bypass-list=*');
options.add_argument('--start-maximized');
options.add_argument('--headless');

# 変数appにFlaskを代入。インスタンス化
app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# Herokuログイン接続確認のためのメソッド
# Herokuにログインすると「hello world」とブラウザに表示される
#@app.route("/")
#def hello_world():

    #return "helloworld!"
@app.route('/', methods=['GET'])
def test():

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)


    driver.get('https://mobile3.pfsv.jp/tasaki/(S(324nx3qcycwpuy45jybhkg55))/loginC.aspx?ID=#hash_meisai') 

    login_id = driver.find_element_by_name("txtUserID")
    #user_id = str(yoyakuId)
    user_id = str("B54494")
    time.sleep(1)
    login_id.send_keys(user_id)

    login_pass = driver.find_element_by_name("txtpassword")
    #user_pass = str(yoyakuPassword)
    user_pass = str("150808")
    time.sleep(1)
    login_pass.send_keys(user_pass) 

    time.sleep(1)
    #ログイン
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    login_btn = driver.find_element_by_name("btnLogin")
    login_btn.click()
    time.sleep(10)

    #予約
    gakka_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_link01")
    gakka_btn.click()
    time.sleep(2)   

    #普通車
    today_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_lnk01")
    today_btn.click()
    time.sleep(2)

    free_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_lnkFree")
    free_btn.click()
    time.sleep(2)


    driver.quit()

    return "HELLO"

    """

    url = "https://mobile3.pfsv.jp/tasaki/(S(veowwivmdrskue45rivjtlbo))/C105_00C.aspx#hash_meisai"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    subtextos= soup.find_all('span')
    text = "A"
    for ext in subtextos:
        text = ext.get_text()
        text = text.replace('教習予約','').replace('三陽自動車学校','').replace('予約上限 2','').replace('予約済 2','').replace('予約上限 1','').replace('予約済 1','').replace('前画面に戻る','').replace('メニュー','').replace('フリー予約','').replace('予約上限に達しています。','').replace('(田崎校)','').replace('(上熊本校)','')

    """


    #login_btn = driver.find_element(By.ID, 'btnLogin').text
    #time.sleep(2)
    #login_btn.click()
    #time.sleep(20)
    #ret_text = driver.find_element(By.ID, 'time_div').text
    #time.sleep(2)


# ユーザーからメッセージが送信された際、LINE Message APIからこちらのメソッドが呼び出される。
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
    # 署名検証で失敗した場合、例外を出す。
    except InvalidSignatureError:
        abort(400)
    # handleの処理を終えればOK
    return 'OK'



@handler.add(JoinEvent) #グループ参加時
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="よろしくお願いします！"))

@handler.add(UnsendEvent) #送信取り消し時
def handle_unsend(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="おい？送信取り消ししたな？"))

@handler.add(MessageEvent, message=TextMessage) #メッセージ参加時
def handle_message(event):

    user_list = ["！甲斐","！西村","！伊形","！江野","！上妻"] #残りの学科
    user_list1 = ["？甲斐","？西村","？伊形","？江野","？上妻"] #空き乗車
    user_list2 = ["、甲斐","、西村","、伊形","、江野","、上妻"] #予約確認

    profile = line_bot_api.get_profile(event.source.user_id)

    def sendMessage(reply):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))
        time.sleep(1)

    def gakka_search(sanyo_id,sanyo_pass):
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)


        driver.get('https://mobile3.pfsv.jp/tasaki/(S(324nx3qcycwpuy45jybhkg55))/loginC.aspx?ID=#hash_meisai') 

        driver.execute_script('document.getElementsByName("txtUserID")[0].value="%s";' % sanyo_id)
        driver.execute_script('document.getElementsByName("txtpassword")[0].value="%s";' % sanyo_pass)

        #ログイン
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        login_btn = driver.find_element_by_name("btnLogin")
        login_btn.click()

        #学科時間割
        gakka_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_link04")
        gakka_btn.click()

        #本日分の確認
        today_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_linkList")
        today_btn.click()

        #学科未受講
        kekka = driver.find_element_by_name("ctl00$ContentPlaceHolder1$txtGakkaMijyukou")
        ret_text = kekka.get_attribute("value")

        driver.quit()

        return ret_text

    def yoyaku_kakunin(sanyo_id,sanyo_pass):

        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        driver.get('https://mobile3.pfsv.jp/tasaki/(S(324nx3qcycwpuy45jybhkg55))/loginC.aspx?ID=#hash_meisai') 

        driver.execute_script('document.getElementsByName("txtUserID")[0].value="%s";' % sanyo_id)
        driver.execute_script('document.getElementsByName("txtpassword")[0].value="%s";' % sanyo_pass)


        #ログイン
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        login_btn = driver.find_element_by_name("btnLogin")
        login_btn.click()


        #予約確認
        gakka_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_link02")
        gakka_btn.click()

        url = str(driver.current_url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        element = soup.find_all(class_="col-md-3")

        count = 0
        text = " "
        text1 = " "
        text2 = " "
        text3 = " "
        text4 = " "
        for elems in element:
            if count == 0:
                text1 = str(elems.text)

            elif count == 1:

                text2 = str(elems.text)

            elif count == 2:

                text3 = str(elems.text)

            elif count == 3:

                text4 = str(elems.text)

            count = count + 1


        text = text1 + "\n" + text2 + "\n\n" + text3 + "\n" + text4
        text = str(text)

        driver.quit()

        return text

    def zyosha_search(sanyo_id,sanyo_pass,number):

        def func1():
            element_sub1 = "ctl00_ContentPlaceHolder1_lblKahi0"
            element_sub2 = "ctl00_ContentPlaceHolder1_lblKahi10"
            element_data = "ctl00_ContentPlaceHolder1_lblDate"

            text_1 = []
            count = 0
            text0 = "\n"
            text1 = "\n"
            text2 = "\n"
            text3 = "\n"
            text4 = "\n"
            text5 = "\n"
            text6 = "\n"
            text7 = "\n"
            text8 = "\n"
            text9 = "\n"
            text_main = "\n"
            text = ""
            url = str(driver.current_url)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')

            date_element = soup.find_all(id=str(element_data))

            for date_elems in date_element:
                date_text = date_elems.text

            for num in range(1,11):
                if num == 10:
                    elems = soup.find_all(id=str(element_sub2))
                else: 
                    num = str(num)

                    id_main = element_sub1 + num
                    elems = soup.find_all(id=str(id_main))
                for element in elems:
                    text = element.text
                    text_1.append(text)
                    if count == 0:
                        text0 = text_1[count]
                    elif count == 1:
                        text1 = text_1[count]
                    elif count == 2:
                        text2 = text_1[count]
                    elif count == 3:
                        text3 = text_1[count]
                    elif count == 4:
                        text4 = text_1[count]
                    elif count == 5:    
                        text5 = text_1[count]
                    elif count == 6:
                        text6 = text_1[count]
                    elif count == 7:
                        text7 = text_1[count]
                    elif count == 8:
                        text8 = text_1[count]
                    elif count == 9:
                        text9 = text_1[count]

                    count = count + 1

            text_main = str(date_text) + "\n" + text0 + "\n" + text1 + "\n" +  text2 + "\n" + text3 + "\n" + text4 + "\n" + text5 + "\n" + text6 + "\n" + text7 + "\n" + text8 + "\n" + text9
            driver.back()
            return text_main

        #driver=webdriver.Chrome(executable_path=path)
        options = Options()                     
        options.add_argument('--disable-gpu')                      
        options.add_argument('--disable-extensions')               
        options.add_argument('--proxy-server="direct://"')         
        options.add_argument('--proxy-bypass-list=*')              
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--lang=ja')                          
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--log-level=3")
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.page_load_strategy = 'eager'

        driver = webdriver.Chrome(options=options)
        driver.get('https://mobile3.pfsv.jp/tasaki/(S(324nx3qcycwpuy45jybhkg55))/loginC.aspx?ID=#hash_meisai') 

        driver.execute_script('document.getElementsByName("txtUserID")[0].value="%s";' % sanyo_id)
        driver.execute_script('document.getElementsByName("txtpassword")[0].value="%s";' % sanyo_pass)
        """        
        login_id = driver.find_element_by_name("txtpassword")
        #user_id = str(yoyakuId)
        user_id = str(sanyo_id)
        login_id.send_keys(sanyo_id)
        

        login_pass = driver.find_element_by_name("txtpassword")
        #user_pass = str(yoyakuPassword)

        user_pass = str(sanyo_pass)
        login_pass.send_keys(user_pass) 
        """
        #ログイン
        login_btn = driver.find_element_by_name("btnLogin")
        login_btn.click()


        #予約
        gakka_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_link01")
        gakka_btn.click()

        #普通車
        today_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_lnk01")
        today_btn.click()

        #フリー予約
        free_btn = driver.find_element_by_id("ctl00_ContentPlaceHolder1_lnkFree")
        free_btn.click()

        a = "\n"
        b = "\n"
        c = "\n"
        d = "\n"
        e = "\n"
        f = "\n"
        g = "\n"

        if(number == 0):
            driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_GridView1']/tbody/tr[2]/td[1]/a").click()

            a = func1()
            a = str(a)

            driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_GridView1']/tbody/tr[3]/td[1]/a").click()

            b = func1()
            b = str(b)

        elif(number == 1):

            driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_GridView1']/tbody/tr[4]/td[1]/a").click()

            a = func1()
            a = str(a)

            driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_GridView1']/tbody/tr[5]/td[1]/a").click()

            b = func1()
            b = str(b)

        elif(number == 2):

            driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_GridView1']/tbody/tr[6]/td[1]/a").click()

            a = func1()
            a = str(a)

            driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_GridView1']/tbody/tr[7]/td[1]/a").click()

            b = func1()
            b = str(b)


        reply = a + "\n\n" + b
        reply = str(reply)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(reply)))

        driver.quit()
        """
        driver.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_GridView1']/tbody/tr[5]/td[1]/a").click()

        c = func1()
        c = str(c)
        
        """


      #reply = a + "\n\n" + b + "\n\n" + c + "\n\n" + d + "\n\n" + e + "\n\n" + f + "\n\n" + g

    def test():

        name = "\n"
        name1 = "\n"

        url = "https://gametrade.jp/tsumtsumland/exhibits"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        found = soup.find_all(class_='game-image')

        count = 0;

        for founds in found:
            for pdf_url in founds.select("img"):
                href = pdf_url.attrs['alt']
                if count == 0:
                    name = href.replace('|ツムツムランド','')
                else:
                    break
            count = count + 1

        url = "https://gametrade.jp/marveltsumtsumgame/exhibits"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        found = soup.find_all(class_='game-image')

        count = 0;

        for founds in found:
            for pdf_url in founds.select("img"):
                href = pdf_url.attrs['alt']
                if count == 0:
                    name1 = href.replace('|マーベルツムツム(マベツム)','')
                else:
                    break
            count = count + 1


        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text="ツムツムランド\n{}\n\nマーベルツムツム\n{}".format(name,name1)))
        time.sleep(1)

    def test1():

        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get('https://gametrade.jp/signin') 
        driver.maximize_window()

        mailAdress = "famefi@merry.pink"
        password = "sueH1467"

        driver.implicitly_wait(5)

        #ログイン
        login_id = driver.find_element_by_name("session[email]")
        login_id.send_keys(mailAdress)

        login_pass = driver.find_element_by_name("session[password]")
        login_pass.send_keys(password) 

        login_btn = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div[2]/form/div[1]/button")
        login_btn.click()
        
        line_bot_api.reply_message(
            event.reply_token,
        TextSendMessage(text="完了"))

        profile_icon = driver.find_element_by_xpath("/html/body/div[1]/header/div[2]/div[2]/ul/li[1]/div/a/img")
        profile_icon.click()

        listing_btn = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div/ul[2]/li[2]/a")
        listing_btn.click()

        #出品リスト1番目
        sell1 = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/div[1]/div[3]/ul/div[1]/li[1]/ul/a")
        sell1.click()

        #編集する
        sell2 = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div[2]/div[1]/div[1]/div[1]/a")
        sell2.click()

        #プレイヤーレベル
        sell3 = driver.find_element_by_name("exhibit[exhibit_sub_form_values_attributes][0][value]")
        x = random.randint(1,9999)
        sell3.send_keys(x)

        #checkbox
        sell4 = driver.find_element_by_name("agreement")
        sell4.click()

        #変更を保存
        sell5 = driver.find_element_by_class_name("g-recaptcha ")
        sell5.click()

        #いいね欄確認
        sell6 = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div[2]/div[1]/div[1]/div[2]/div/form/button")


    def schedule():

        tokyo_tz = datetime.timezone(datetime.timedelta(hours=9))
        dt = datetime.datetime.now(tokyo_tz)

        url = "https://www.sanyo-ds.com/student/time-schedule/"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        found = soup.select("[class='parts_img_type08_img']")
        count = 0;
        for founds in found:
            for pdf_url in founds.select("a"):
                href = pdf_url.attrs['href']
                if count == 0:
                    replay_tasaki = "https://www.sanyo-ds.com/" + href.replace('../../','')

                elif count == 1:
                    replay_kamikumamoto = "https://www.sanyo-ds.com/" + href.replace('../../','')
                
                elif count == 2:
                    replay_tasaki1 = "https://www.sanyo-ds.com/" + href.replace('../../','')
                
                elif count == 3:
                    replay_kamikumamoto1 = "https://www.sanyo-ds.com/" + href.replace('../../','')

                else:
                    break

            count = count + 1

        found = soup.select("[class='parts_img_type08_box right']")
        count = 0;
        for founds in found:

            if count == 0:
                month = founds.text

            elif count == 1:
                month1 = founds.text

            count = count + 1

        month = month.replace('上熊本校の','').replace('教習時間割を見る','').replace('月','')
        month1 = month1.replace('上熊本校の','').replace('教習時間割を見る','').replace('月','')

    
        month = str(month)
        month1 = str(month1)

        if month == " 1":
            moseng = "Jan."
        elif month == " 2":
            moseng = "Feb."
        elif month == " 3":
            moseng = "Mar."
        elif month == " 4":
            moseng = "Apr."
        elif month == " 5":
            moseng = "May."
        elif month == " 6":
            moseng = "Jun."
        elif month == " 7":
            moseng = "Jul."
        elif month == " 8":
            moseng = "Aug."
        elif month == " 9":
            moseng = "Sep."
        elif month == " 10":
            moseng = "Oct."
        elif month == " 11":
            moseng = "Nov."
        elif month == " 12":
            moseng = "Dec."

        if month1 == " 1":
            moseng1 = "Jan."
        elif month1 == " 2":
            moseng1 = "Feb."
        elif month1 == " 3":
            moseng1 = "Mar."
        elif month1 == " 4":
            moseng1 = "Apr."
        elif month1 == " 5":
            moseng1 = "May."
        elif month1 == " 6":
            moseng1 = "Jun."
        elif month1 == " 7":
            moseng1 = "Jul."
        elif month1 == " 8":
            moseng1 = "Aug."
        elif month1 == " 9":
            moseng1 = "Sep."
        elif month1 == " 10":
            moseng1 = "Oct."
        elif month1 == " 11":
            moseng1 = "Nov."
        elif month1 == " 12":
            moseng1 = "Dec."


        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="{}月の時間割はこちら↓\n\n< 田崎 {} >\n{}\n\n< 上熊本 {} >\n{}\n\n--------------------\n\n{}月の時間割はこちら↓\n\n< 田崎 {} >\n{}\n\n< 上熊本 {} >\n{}".format(month,moseng,replay_tasaki,moseng,replay_kamikumamoto,month1,moseng1,replay_tasaki1,moseng1,replay_kamikumamoto1)))
        time.sleep(1)


    def get_kumamoto_news():

        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get('https://topics.smt.docomo.ne.jp/ranking/region/kumamoto') 
        driver.maximize_window()

        for count in range(1,20):

            xpath = '//*[@id="content"]/main/section/div[2]/ul/li[{}]/article/a/h3'.format(count)
            elements = driver.find_elements_by_xpath(xpath)

            for element in elements:
                        
                if count == 1:
                    reply1 = element.text + "\n\n"
                    reply1 = reply1.replace('1', '1位 : ')

                elif count == 2:
                    reply2 = element.text + "\n\n"
                    reply2 = reply2.replace('2', '2位 : ')

                elif count == 3:
                    reply3 = element.text + "\n\n"
                    reply3 = reply3.replace('3', '3位 : ')

                elif count == 4:
                    reply4 = element.text + "\n\n"
                    reply4 = reply4.replace('4', '4位 : ')

                elif count == 5:
                    reply5 = element.text + "\n\n"
                    reply5 = reply5.replace('5', '5位 : ')

                elif count == 6:
                    reply6 = element.text + "\n\n"
                    reply6 = reply6.replace('6', '6位 : ')

                elif count == 7:
                    reply7 = element.text + "\n\n" 
                    reply7 = reply7.replace('7', '7位 : ')

                elif count == 8:
                    reply8 = element.text + "\n\n"
                    reply8 = reply8.replace('8', '8位 : ')

                elif count == 9:
                    reply9 = element.text + "\n\n"
                    reply9 = reply9.replace('9', '9位 : ')

                elif count == 10:
                    reply10 = element.text + "\n\n"
                    reply10 = reply10.replace('10', '10位 : ')

                elif count == 11:
                    reply11 = element.text + "\n\n"
                    reply11 = reply11.replace('11', '11位 : ')

                elif count == 12:
                    reply12 = element.text + "\n\n"
                    reply12 = reply12.replace('12', '12位 : ')

                elif count == 13:
                    reply13 = element.text + "\n\n"
                    reply13 = reply13.replace('13', '13位 : ')

                elif count == 14:
                    reply14 = element.text + "\n\n"
                    reply14 = reply14.replace('14', '14位 : ')

                elif count == 15:
                    reply15 = element.text + "\n\n"
                    reply15 = reply15.replace('15', '15位 : ')

                elif count == 16:
                    reply16 = element.text + "\n\n"
                    reply16 = reply16.replace('16', '16位 : ')
            
                elif count == 17:
                    reply17 = element.text + "\n\n"
                    reply17 = reply17.replace('17', '17位 : ')

                elif count == 18:
                    reply18 = element.text + "\n\n"
                    reply18 = reply18.replace('18', '18位 : ')

                elif count == 19:
                    reply19 = element.text
                    reply19 = reply19.replace('19', '19位 : ')

        driver.quit() 

        reply = reply1 + reply2 + reply3 + reply4 + reply5 + reply6 + reply7 + reply8 + reply9 + reply10 + reply11 + reply12 + reply13 + reply14 + reply15 + reply16 + reply17 + reply18 + reply19 + "\n\n<取得サイト>\nhttps://topics.smt.docomo.ne.jp/ranking/region/kumamoto"
        reply = str(reply)
        return reply



    def get_weather():

        #アクセスRL
        url = 'https://weather.yahoo.co.jp/weather/jp/43/8610.html'
        http = urllib3.PoolManager()
        instance = http.request('GET', url)
        soup = BeautifulSoup(instance.data, 'html.parser')

        tenki_today = soup.select_one('#main > div.forecastCity > table > tr > td > div > p.pict')

        tenki_tomorrow = soup.select_one('#main > div.forecastCity > table > tr > td + td > div > p.pict')

        if tenki_today == "雨":
            weather_ans = "今日の天気は{}\n傘を忘れないでください\n\n明日の天気は{}\n\n<--引用サイト-->\nhttps://weather.yahoo.co.jp/weather/jp/43/8610.html".format(tenki_today.text,tenki_tomorrow.text)
        else:
            weather_ans = "今日の天気は{}\n明日の天気は{}\n<--引用サイト-->\nhttps://weather.yahoo.co.jp/weather/jp/43/8610.html".format(tenki_today.text,tenki_tomorrow.text)

        return weather_ans


    def add_db(userName,message):

        dbname = ('linebot.db')
        conn = sqlite3.connect(dbname, isolation_level=None)

        cursor = conn.cursor()

        sql = """CREATE TABLE IF NOT EXISTS linebot(id, name, date)"""
        cursor.execute(sql)

        sql = """SELECT name FROM sqlite_master WHERE TYPE='table'"""

        sql = """INSERT INTO linebot VALUES(?,?)"""

        data = ((userName, message))
        cursor.execute(sql, data)

        sql = """SELECT * FROM linebot"""
        cursor.execute(sql)

        conn.close()

        reply = str(cursor.fetchall())

        return reply



    if event.message.text == "@help":

        profile = line_bot_api.get_profile(event.source.user_id)
        profile_name = profile.display_name # 表示名
        profile_id = profile.user_id # ユーザーID

        language_list = ["@学科時間割","@空き乗車検索","@残りの学科確認","@予約中の乗車検索","@天気予報","@今日のニュース","@コマンド一覧"]

        items = [QuickReplyButton(action=MessageAction(label=f"{language}", text=f"{language}")) for language in language_list]

        messages = TextSendMessage(text=str(profile_name) + "様,どの情報が必要ですか？",
                                quick_reply=QuickReply(items=items))


        line_bot_api.reply_message(event.reply_token, messages=messages)

        time.sleep(3)

    elif event.message.text == "ヘルプ":

        profile = line_bot_api.get_profile(event.source.user_id)
        profile_name = profile.display_name # 表示名
        profile_id = profile.user_id # ユーザーID

        language_list = ["@学科時間割","@空き乗車検索","@残りの学科確認","@予約中の乗車検索","@天気予報","@今日のニュース","@コマンド一覧"]

        items = [QuickReplyButton(action=MessageAction(label=f"{language}", text=f"{language}")) for language in language_list]

        messages = TextSendMessage(text=str(profile_name) + "様,どの情報が必要ですか？",
                                quick_reply=QuickReply(items=items))


        line_bot_api.reply_message(event.reply_token, messages=messages)

        time.sleep(3)

    elif event.message.text == "@学科時間割":

        schedule()

    elif event.message.text == "@a":

        test()

    elif event.message.text == "@b":

        test1()

    elif event.message.text == "@予約自動ログイン方法":

        reply = "自動ログインはiOS端末のみ使用可能です\nYouTube↓↓\n https://youtu.be/rDcHoKfROlY"
        sendMessage(reply)

    elif event.message.text == "@残りの学科確認":

        reply = "残りの学科を調べることが出来ます。\n登録済みユーザーのみ使用可能で、呼び出し方は「！」の後に自分の苗字を入れる必要があります\n\n登録済みユーザー\n{}".format(user_list)
        sendMessage(reply)

    elif event.message.text == "@空き乗車検索":

        reply = "###beta版###\n空き乗車時間を調べることが出来ます。登録済みユーザーのみ使用可能で、呼び出し方は「？」の後に自分の苗字を入れる必要があります。\n\n名前の語尾に1または2を付けると一週間分の乗車時間を知ることが出来ます。\n例(？伊形 , ？伊形1 , ？伊形2)\n\n登録済みユーザー\n{}".format(user_list1)
        sendMessage(reply)

    elif event.message.text == "@予約中の乗車検索":

        reply = "予約中の乗車時間を調べることが出来ます。登録済みユーザーのみ使用可能で、呼び出し方は「、」の後に自分の苗字を入れる必要があります\n\n登録済みユーザー\n{}".format(user_list2)
        sendMessage(reply)

    elif event.message.text == "@コマンド一覧":

        reply = "#############\n#############\n\n\n@送迎予約方法\n@教習予約サイト\n@入校予約申込み\n\n\n#############\n#############"
        sendMessage(reply)

    elif event.message.text == "@送迎予約方法":

        reply = "< 田崎校 >\n096-356-3400\n< 上熊本校 >\n096-322-4161\n\n< 公式サイト >\nhttps://www.sanyo-ds.com/student/pickup/"
        sendMessage(reply)

    elif event.message.text == "@教習予約サイト":

        reply = "< 田崎校 >\nhttps://mobile3.pfsv.jp/tasaki/(S(xkkqrd45sqj4imzj3klfjbed))/loginC.aspx?ID=#hash_meisai\n< 上熊本校 >\nhttps://mobile3.pfsv.jp/kamikuma/(S(bobos1afeynqdv4513gzp245))/loginC.aspx?ID=#hash_meisai"
        sendMessage(reply)

    elif event.message.text == "@入校予約申し込み":

        reply = "https://www.sanyo-ds.com/enrollment/applications/"
        sendMessage(reply)

    elif event.message.text == "@天気予報":

        reply = get_weather()
        sendMessage(reply)

    elif event.message.text == "@今日のニュース":

        reply = get_kumamoto_news()
        sendMessage(reply)
        

    ########  残りの学科 ########

    elif event.message.text == user_list[0]:

        #reply = gakka_search("B54494",150808)
        reply = gakka_search("A62764",150707)
        sendMessage("残りの学科は:" + reply)

    elif event.message.text == user_list[1]:

        reply = gakka_search("A61144",151121)
        sendMessage("残りの学科は:" + reply)
    
    elif event.message.text == user_list[2]:

        reply = gakka_search("A61874",150623)
        sendMessage("残りの学科は:" + reply)

    elif event.message.text == user_list[3]:

        reply = gakka_search("A60614",151102)
        sendMessage("残りの学科は:" + reply)

    elif event.message.text == user_list[4]:

        reply = gakka_search("A64344",160204)
        sendMessage("残りの学科は:" + reply)


    ######## 空き乗車検索 ########

    elif (event.message.text == user_list1[0] or event.message.text == user_list1[0] + "1" or event.message.text == user_list1[0] + "2"):

        #reply = gakka_search("B54494",150808)
        userid = "A62764"
        userpass = "150707"

        if(event.message.text == user_list1[0]):
            zyosha_search(userid,userpass,0)
        elif(event.message.text == user_list1[0] + "1"):
            zyosha_search(userid,userpass,1)
        elif(event.message.text == user_list1[0] + "2"):
            zyosha_search(userid,userpass,2)

    elif (event.message.text == user_list1[1] or event.message.text == user_list1[1] + "1" or event.message.text == user_list1[1] + "2"):

        userid = "A61144"
        userpass = "151121"

        if(event.message.text == user_list1[1]):
            zyosha_search(userid,userpass,0)
        elif(event.message.text == user_list1[1] + "1"):
            zyosha_search(userid,userpass,1)
        elif(event.message.text == user_list1[1] + "2"):
            zyosha_search(userid,userpass,2)

    elif (event.message.text == user_list1[2] or event.message.text == user_list1[2] + "1" or event.message.text == user_list1[2] + "2"):

        userid = "A61874"
        userpass = "150623"

        if(event.message.text == user_list1[2]):
            zyosha_search(userid,userpass,0)
        elif(event.message.text == user_list1[2] + "1"):
            zyosha_search(userid,userpass,1)
        elif(event.message.text == user_list1[2] + "2"):
            zyosha_search(userid,userpass,2)


    elif (event.message.text == user_list1[3] or event.message.text == user_list1[3] + "1" or event.message.text == user_list1[3] + "2"):

        userid = "A60614"
        userpass = "151102"
        
        if(event.message.text == user_list1[3]):
            zyosha_search(userid,userpass,0)
        elif(event.message.text == user_list1[3] + "1"):
            zyosha_search(userid,userpass,1)
        elif(event.message.text == user_list1[3] + "2"):
            zyosha_search(userid,userpass,2)

    elif (event.message.text == user_list1[4] or event.message.text == user_list1[4] + "1" or event.message.text == user_list1[4] + "2"):

        userid = "A64344"
        userpass = "160204"

        if(event.message.text == user_list1[4]):
            zyosha_search(userid,userpass,0)
        elif(event.message.text == user_list1[4] + "1"):
            zyosha_search(userid,userpass,1)
        elif(event.message.text == user_list1[4] + "2"):
            zyosha_search(userid,userpass,2)
       


    ######## 予約確認 ########

    elif event.message.text == user_list2[0]:

        reply = yoyaku_kakunin("A62764",150707)
        sendMessage("::予約中の乗車::\n\n" + reply)

    elif event.message.text == user_list2[1]:

        reply = yoyaku_kakunin("A61144",151121)
        sendMessage("::予約中の乗車::\n\n" + reply)
    
    elif event.message.text == user_list2[2]:

        reply = yoyaku_kakunin("A61874",150623)
        sendMessage("::予約中の乗車::\n\n" + reply)

    elif event.message.text == user_list2[3]:

        reply = yoyaku_kakunin("A60614",151102)
        sendMessage("::予約中の乗車::\n\n" + reply)

    elif event.message.text == user_list2[4]:

        reply = yoyaku_kakunin("A64344",160204)
        sendMessage("::予約中の乗車::\n\n" + reply)


        
        #sendMessage("残りの学科は" + reply1 + "\n" + "今日の空き乗車\n" + reply2)

        #profile = line_bot_api.get_profile(event.source.user_id)

        #profile_name = profile.display_name #表示名
        #profile_id = profile.user_id # ユーザーID
        #profile_Img = profile.image_url #画像
        #profile_status = profile.status_message #ステメ

    


# ポート番号の設定
if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)

# heroku config:set YOUR_CHANNEL_SECRET="92107747c000917abd532beee8c107c6" --app linebot0syako
# heroku config:set YOUR_CHANNEL_ACCESS_TOKEN="YlABdhiVLK8+Mr2DpOHwRCOnoe7ukK3idojPFveZGWSlbD7jpXguwwJ/hvrPWb0e6J0uUVZg/ZHzPONfZW9/Om3AZrBfabt4TzlBsSCRTo86vYY3LvxBjPp5QkP9DUFeUigt0JltN7qJSRe0OD58uwdB04t89/1O/w1cDnyilFU=" --app linebot0syako
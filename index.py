import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

from flask import Flask, render_template, request
from datetime import datetime

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>陳昭毅網頁20231123 10:00</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome>傳送使用者暱稱</a><br>"
    homepage += "<a href=/about>昭毅簡介網頁</a><br>"
    homepage += "<a href=/search>圖書查詢:</a><br>"
    homepage += "<br><a href=/books>圖書精選</a><br>"

    homepage += "<br><a href=/spider>網路爬蟲擷取子青老師課程資料</a><br>"
    return homepage

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime = str(now))

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    user = request.values.get("gust")
    return render_template("welcome.html", name=user)

@app.route("/about")
def about():
    return render_template("aboutme.html")

@app.route("/search", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        keyword = request.form["keyword"]
        result = "您輸入的關鍵字是:" + keyword

        db = firestore.client()
        collection_ref = db.collection("圖書精選")
        docs = collection_ref.order_by("anniversary").get()
        for doc in docs:
            bk = doc.to_dict()
            if keyword in bk["title"]:
                result += "書名:<a href=" + bk["url"] + ">" + bk["title"] + "<br>"
                result += "作者:" + bk["author"] + ">" + "<br>"
                result += str(bk["anniversary"]) + "周年紀念版" + ">" + "<br>"
                result += "<img src=" + bk["cover"] + "></img><br><br>" 
        return result
    else:
        return render_template("search.html")

@app.route("/books")
def books():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("圖書精選")    
    docs = collection_ref.order_by("anniversary",direction=firestore.Query.DESCENDING).get()
    for doc in docs:
        bk = doc.to_dict()
        Result += "書名:<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"
        Result += "作者:" + bk["author"] + "<br>"
        Result += "周年" + str(bk["anniversary"]) + "周年紀念版" + "<br>"
        Result += "<img src=" + bk["cover"] + "></img><br><br>"

    return Result

@app.route("/spider")
def spider():
    info = ""

    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box")

    for x in result:
        info += x.find("h4").text + "<br>"
        info += x.find("p").text + "<br>"
        info += x.find("a").get("href") + "<br>"
        info += "https://www1.pu.edu.tw/~tcyang/" +x.find("img").get("src") + "<br><br>"
    return info

if __name__ == "__main__":
    app.run(debug=True)
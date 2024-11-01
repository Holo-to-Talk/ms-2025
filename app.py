import os
import re
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, request, url_for,render_template
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import Dial, VoiceResponse
from db import *

# .envファイルから環境変数を読み込む
load_dotenv()

db_connection()

# Flaskアプリケーションを作成
app = Flask(__name__,template_folder="./static")

# 特殊文字やアンダースコアを除去する正規表現
alphanumeric_only = re.compile("[\W_]+")

# 電話番号の形式を検証するための正規表現
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")

# Twilioの電話番号を環境変数から取得
twilio_number = os.environ.get("TWILIO_CALLER_ID")

# 最新のユーザーIDをメモリに保存する辞書
IDENTITY = {"identity": ""}

# バリデーション関数
def validate_name(name):
    if not name:
        return "駅名を入力してください。"
    return ""

def validate_station_num(station_num):
    if not station_num.isdigit():
        return "駅番号を入力して下さい。"
    return ""

def validate_address(address):
    if not address:
        return "駅の住所を入力して下さい。"
    return ""

def validate_phone_num(phone_num):
    pattern = r"^\+?[0-9]{10,15}$"
    if not re.match(pattern, phone_num):
        return "電話番号が無効です。"
    return ""

def validate_password(password):
    if len(password) < 6:
        return "パスワードは6文字以上で入力して下さい。"
    return ""

# ユーザー登録用のルート
@app.route('/user/register', methods=['GET', 'POST'])
def register():
    error_msg = []

    if request.method == 'POST':
        name = request.form['name']
        station_num = request.form['station_num']
        address = request.form['address']
        phone_num = request.form['phone_num']
        password = request.form['password']

        # バリデーション
        error_msg.append(validate_name(name))
        error_msg.append(validate_station_num(station_num))
        error_msg.append(validate_address(address))
        error_msg.append(validate_phone_num(phone_num))
        error_msg.append(validate_password(password))

        # バリデーションエラーチェック
        error_msg = [msg for msg in error_msg if msg]  # エラーがあるものだけ保持
        if not error_msg:
            # データベースに保存
            conn = connect_db()
            
            print(conn)
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (name, station_num, address, phone_num, password) 
            VALUES (%s, %s, %s, %s, %s)
            ''', (name, station_num, address, phone_num, password))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('success'))  # 成功ページにリダイレクト

    # register.htmlを静的ファイルから読み込み
    with open('static/register.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # エラーメッセージをHTMLに埋め込む
    if error_msg:
        error_html = "<ul>" + "".join([f"<li>{msg}</li>" for msg in error_msg]) + "</ul>"
        html_content = html_content.replace("{% error_msg %}", error_html)
    else:
        html_content = html_content.replace("{% error_msg %}", "")

    return html_content

# 成功メッセージ表示
@app.route('/success')
def success():
    return "User registered successfully!"

# ルートURLにアクセスされた際にregister.htmlを返す
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# トークンを生成して返すAPIエンドポイント
@app.route("/token", methods=["GET"])
def token():
    # 環境変数からTwilioのアカウント情報を取得
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    application_sid = os.environ["TWILIO_TWIML_APP_SID"]
    api_key = os.environ["API_KEY"]
    api_secret = os.environ["API_SECRET"]

    # ランダムなユーザー名を生成し、記号を削除してIDとして保存
    identity = twilio_number
    IDENTITY["identity"] = identity

    # アクセストークンを生成し、ユーザーIDを設定
    token = AccessToken(account_sid, api_key, api_secret, identity=identity)

    # Voice Grantを作成し、トークンに追加（着信許可）
    voice_grant = VoiceGrant(
        outgoing_application_sid=application_sid,
        incoming_allow=True,
    )
    token.add_grant(voice_grant)

    # トークンをJWT形式に変換
    token = token.to_jwt()

    # トークンとユーザーIDをJSON形式で返す
    return jsonify(identity=identity, token=token)

# 音声通話に対応するAPIエンドポイント
@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()

    # 発信先がTwilioの電話番号の場合、着信として処理
    if request.form.get("To") == twilio_number:
        dial = Dial()
        # 最後に生成されたクライアントIDに接続
        dial.client(IDENTITY["identity"])
        resp.append(dial)
    
    # 発信先が指定されている場合、外部に発信する処理
    elif request.form.get("To"):
        dial = Dial(caller_id=twilio_number)
        
        # 電話番号が数字と記号のみで構成されているか確認
        if phone_pattern.match(request.form["To"]):
            dial.number(request.form["To"])
        else:
            dial.client(request.form["To"])
        resp.append(dial)
    
    # 発信先がない場合のメッセージ
    else:
        resp.say("Thanks for calling!")

    # TwiML形式の応答をXMLとして返す
    return Response(str(resp), mimetype="text/xml")


@app.route('/test_connection')
def test_connection():
    return db_connection()
    # アプリケーションを実行
if __name__ == "__main__":
    app.run()
import os
import re
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, request, render_template, session, url_for
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import Dial, VoiceResponse
import bcrypt
from db import *
from validation import *

# .envファイルから環境変数を読み込む
load_dotenv()

#DB接続テスト
db_connection()

# Flaskアプリケーションを作成
app = Flask(__name__,template_folder='./static/')
app.secret_key = os.environ.get("SECRET_KEY")

# 特殊文字やアンダースコアを除去する正規表現
alphanumeric_only = re.compile("[\W_]+")

# 電話番号の形式を検証するための正規表現
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")

# Twilioの電話番号を環境変数から取得
twilio_number = os.environ.get("TWILIO_CALLER_ID")

# 最新のユーザーIDをメモリに保存する辞書
IDENTITY = {"identity": ""}

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

# ルートURLにアクセスされた際の処理
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect('/login')

# ログイン処理
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user' in session:
            return redirect("/")
        else:
            return render_template('login.html')

    if request.method == 'POST':
        num = request.form.get('num', '')
        password = request.form.get('password', '')
        # データベースからユーザー情報を取得
        conn = db_connection()

        cursor = conn.cursor()
        cursor.execute(''' use holo_to_talk ''')

        query = "SELECT * FROM users WHERE station_num = %s"
        cursor.execute(query, (num,))
        users = cursor.fetchall()

        if len(users) == 1:
            user = users[0]

            # パスワードを照合
            if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):  # user[2]がハッシュ化パスワードと仮定
                session['user'] = user[0]  # セッションにユーザーIDを保存
                return redirect('/')
            else:
                return "ログインエラー: IDまたはパスワードが間違っています"
        else:
            return "ログインエラー: IDまたはパスワードが間違っています"

    return render_template('login.html')

# ユーザー登録処理
@app.route('/user/register', methods=['GET', 'POST'])
def register():
    error_msg = []

    form_data = {
        "name": "",
        "station_num": "",
        "address": "",
        "phone_num": "",
        "password": ""
    }

    if request.method == 'POST':
        # 入力内容を保持
        form_data = {
            "name": request.form.get("name", ""),
            "station_num": request.form.get("station_num", ""),
            "address": request.form.get("address", ""),
            "phone_num": request.form.get("phone_num", ""),
            "password": request.form.get("password", "")
        }

        # バリデーション
        error_msg.append(validate_name(form_data["name"]))
        error_msg.append(validate_station_num(form_data["station_num"]))
        error_msg.append(validate_address(form_data["address"]))
        error_msg.append(validate_phone_num(form_data["phone_num"]))
        error_msg.append(validate_password(form_data["password"]))

        error_msg = [msg for msg in error_msg if msg]

        if not error_msg:

            # パスワードをハッシュ化
            hashed_password = bcrypt.hashpw(form_data["password"].encode('utf-8'), bcrypt.gensalt())

            # データベースに保存
            conn = db_connection()

            cursor = conn.cursor()
            cursor.execute(''' use holo_to_talk ''')
            # usersテーブルにデータを挿入  
            cursor.execute('''
                INSERT INTO users (station_num, password) 
                VALUES (%s, %s)
                ''', (form_data["station_num"], hashed_password))

            # station_infoテーブルにデータを挿入 
            cursor.execute('''
            INSERT INTO station_info (name, station_num, address, phone_num) 
            VALUES (%s, %s, %s, %s)
            ''', (form_data["name"], form_data["station_num"], form_data["address"], form_data["phone_num"]))

            # データベースに変更を保存
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('login'))  # 成功ページにリダイレクト

    return render_template('register.html', error_msg=error_msg, form_data=form_data)

# 成功メッセージ表示
@app.route('/success')
def success():
    return "User registered successfully!"

# ログアウト処理
@app.route('/logout')
def logout():
    session.clear()  # セッションをクリア
    return redirect(url_for('login'))

@app.route("/log-detail",methods=["GET"])
def log_detail():
    if request.method == "GET":
        return render_template("log-detail.html")

@app.route("/log-list",methods=["GET"])
def log_list():
    if request.method == "GET":
        return render_template("log-list.html")

@app.route('/report/list', methods=['GET'])
def userlist():
    if request.method == "GET":
        # データベース接続
        conn = db_connection()
        cursor = conn.cursor()

        try:
            # データベースを選択
            cursor.execute('''USE holo_to_talk''')

            # station_infoテーブルから必要なデータを取得
            cursor.execute('''SELECT * FROM staff_log''')
            logs = cursor.fetchall()
            print(logs)

            # データをHTMLテンプレートに渡す
            return render_template('report-list.html', logs=logs)

        except Exception as e:
            # エラー処理
            error_message = f"データの取得中にエラーが発生しました: {e}"
            return render_template('report-list.html', error_message=error_message)

        finally:
            # リソースを解放
            cursor.close()
            conn.close()

# アプリケーションを実行
if __name__ == "__main__":
    app.run(debug=True)

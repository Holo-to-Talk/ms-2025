import os
import re
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, request, render_template, session ,url_for
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import Dial, VoiceResponse
import mysql.connector
import logging
from mysql.connector import Error


logging.basicConfig(level=logging.DEBUG)

# .envファイルから環境変数を読み込む
load_dotenv()

# Flaskアプリケーションを作成
app = Flask(__name__)
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or "your_default_secret_key"  # 環境変数から取得するか、デフォルト値を設定


# MySQL接続情報の設定
def get_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='dev-user',
            password='Ejdmpr6U@',
            database='holo_to_talk'
        )
        if connection.is_connected():
            logging.info("データベース接続成功")
            return connection
    except Error as e:
        print(f"Error: {e}")
        logging.error(f"接続エラー: {e}")
        return None

# 特殊文字やアンダースコアを除去する正規表現
alphanumeric_only = re.compile("[\W_]+")

# 電話番号の形式を検証するための正規表現
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")

# Twilioの電話番号を環境変数から取得
twilio_number = os.environ.get("TWILIO_CALLER_ID")

# 最新のユーザーIDをメモリに保存する辞書
IDENTITY = {"identity": "Admin-Center"}

# ルートURLにアクセスされた際にindex.htmlを返す
# @app.route("/")
# def index():
#     return app.send_static_file("index.html")
@app.route('/')
def home():
    if 'user' in session:
        # return f"ログイン中のユーザーID: {session['user']}"
        # return app.send_static_file("index.html")
        return render_template('logout.html')#一時的にログアウト用のページに遷移
    # return "ログインしていません"
    return redirect('/login')

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

# ユーザーのログインを試行する関数
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = []
    
    # セッションの有無でログイン画面を切り替える
    # get Requestがおくられたら
    if request.method == 'GET':
        if 'user' in session:
            return redirect("/")
        else:
            return render_template('login.html')
    
    # post Request が送られたら
    if request.method == 'POST':
        num = request.form.get('num', '')
        password = request.form.get('password', '')
        
        # データベースからユーザー情報を取得
        connection = get_db()
        if connection:
            try:
                cursor = connection.cursor()
                logging.info("sql check")
                sql = "SELECT * FROM users WHERE station_num = %s"
                cursor.execute(sql, (num,))
                users = cursor.fetchall()

                if len(users) == 1:
                    user = users[0]  # 1行だけ取得された場合
                    logging.info("通った？")
                    # user = cursor.fetchone()
                    cursor.close()
                    logging.info(f"ユーザー情報: {user}")
                # データベースの平文のパスワードと照合
                    if password == user[2]:  # パスワードをそのまま比較
                        session['user'] = user[0]  # ユーザーIDをセッションに保存
                        return redirect('/')
                    else:
                        return "パスワードが違います"
                elif len(users) == 0:
                    return "ユーザーが見つかりません"
                else:
                    return "複数の一致するユーザーがいます"
            except Error as e:
                return f"ログインエラー: {e}"
            finally:
                connection.close()
        else:
            return "データベース接続エラー"

    return render_template('login.html')

# ログアウト処理
@app.route('/logout')
def logout():
    session.clear()  # セッションをクリア
    return redirect(url_for('login'))




# アプリケーションを実行
if __name__ == "__main__":
    app.run()

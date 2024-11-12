import os
import re
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, request, render_template, session, url_for
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import Dial, VoiceResponse
import bcrypt
from db import *

# .envファイルから環境変数を読み込む
load_dotenv()

# Flaskアプリケーションを作成
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


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

# ログアウト処理
@app.route('/logout')
def logout():
    session.clear()  # セッションをクリア
    return redirect(url_for('login'))

# アプリケーションを実行
if __name__ == "__main__":
    app.run()

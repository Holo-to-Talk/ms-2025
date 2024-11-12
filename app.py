import os
import re
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, request, render_template, session, url_for
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import Dial, VoiceResponse
import mysql.connector
import logging
from mysql.connector import Error
import bcrypt
from db import *

logging.basicConfig(level=logging.DEBUG)

# .envファイルから環境変数を読み込む
load_dotenv()

# Flaskアプリケーションを作成
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or "your_default_secret_key"

# 仮のユーザー登録処理
def register_user(num, plain_password):
    # 1. パスワードをハッシュ化
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())

    # 2. ハッシュ化されたパスワードをデータベースに保存
    connection = db_connection()
    if connection:
        cursor = connection.cursor()
        
        sql = "INSERT INTO users (station_num, password) VALUES (%s, %s)"
        cursor.execute(sql, (num, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # フォームからstation_numとpasswordを取得
        num = request.form.get('num')
        password = request.form.get('password')
        
        # station_numとpasswordが入力されているか確認
        if not num or not password:
            return "ユーザーIDとパスワードの両方を入力してください。"

        # register_user関数を呼び出して新しいユーザーを登録
        register_user(num, password)
        
        return "ユーザーが登録されました！"
    
    # GETリクエストでフォームを表示
    return render_template('register.html')

# ルートURLにアクセスされた際の処理
@app.route('/')
def home():
    if 'user' in session:
        return render_template('logout.html')  # 一時的にログアウト用のページに遷移
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
        cursor.execute(''' use holo_to_talk''')
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

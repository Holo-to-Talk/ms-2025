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
def index():
    if 'user' in session:
        return render_template('index.html')
    return redirect('/station/login')

# ログイン処理
@app.route('/station/login', methods=['GET', 'POST'])
def login():
    error_msg = ""  # エラーメッセージを初期化

    if request.method == 'GET':
        if 'user' in session:
            return redirect("/")
        else:
            return render_template('./station/login.html', error_msg=error_msg)

    if request.method == 'POST':
        num = request.form.get('num', '')
        password = request.form.get('password', '')

        # データベースからユーザー情報を取得
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('''USE holo_to_talk''')

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
                error_msg = "ログインエラー: IDまたはパスワードが間違っています"
        else:
            error_msg = "ログインエラー: IDまたはパスワードが間違っています"

        # エラーメッセージを渡して再度ログインページを表示
        return render_template('./station/login.html', error_msg=error_msg)

# ユーザー登録処理
@app.route('/station/register', methods=['GET', 'POST'])
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

    return render_template('./station/register.html', error_msg=error_msg, form_data=form_data)

# /editにアクセスしたときに/にリダイレクト
@app.route('/station/edit/',methods=['GET'])
def edit_index():
    if request.method == 'GET':
        return redirect("/")

#ユーザーリスト表示処理
@app.route('/station/list', methods=['GET','POST'])
def station_list():
    if request.method == "GET":
        # データベース接続
        conn = db_connection()
        cursor = conn.cursor()

        try:
            # データベースを選択
            cursor.execute('''USE holo_to_talk''')

            # station_infoテーブルから必要なデータを取得
            cursor.execute('''SELECT name, station_num, address, phone_num FROM station_info''')
            rows = cursor.fetchall()

            # カラム名をキーにして辞書形式でデータを作成
            stations = [
                {"name": row[0], "station_num": row[1], "address": row[2], "phone_num": row[3]}
                for row in rows
            ]

            # データをHTMLテンプレートに渡す
            return render_template('./station/list.html', stations=stations)

        except Exception as e:
            # エラー処理
            error_message = f"データの取得中にエラーが発生しました: {e}"
            return render_template('./station/list.html', error_message=error_message)

        finally:
            # リソースを解放
            cursor.close()
            conn.close()

    if request.method == "POST":
        station_num = request.form['station_num']
        action = request.form['action']

    if action == "編集":
        # 編集画面にリダイレクト
        return redirect(f"/station/edit/{station_num}")

    elif action == "削除":
        # データ削除処理
        conn = db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''USE holo_to_talk''')
            cursor.execute('''DELETE FROM station_info WHERE station_num = %s''', (station_num,))
            conn.commit()

            # 削除後にリスト画面にリダイレクト
            return redirect('/station/list')

        except Exception as e:
            return f"データ削除中にエラーが発生しました: {e}"

        finally:
            cursor.close()
            conn.close()

# ユーザー編集処理
@app.route('/station/edit/<station_num>', methods=['GET', 'POST'])
def edit_station(station_num):
    error_msg = []
    form_data = {}
    print(station_num)#編集駅番号

    conn = db_connection()
    if conn is None:
        return "データベース接続エラー", 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("USE holo_to_talk")

    # GETメソッドでデータを取得し編集ページを表示
    if request.method == 'GET':
        query = "SELECT * FROM station_info WHERE station_num = %s"
        cursor.execute(query, (station_num,))
        result = cursor.fetchone()

        if not result:
            return redirect("/station/list?station_num=not_found")

        form_data = {
            "name": result["name"],
            "station_num": result["station_num"],
            "address": result["address"],
            "phone_num": result["phone_num"],
            "type_AI": result["type_AI"],
        }
        print(form_data)#編集内容

        cursor.close()
        return render_template("./station/edit.html", form_data=form_data)

    # POSTメソッドでデータを更新
    if request.method == 'POST':
        print("POST")
        form_data = {
            "name": request.form.get("name", ""),
            "station_num": request.form.get("station_num", ""),
            "address": request.form.get("address", ""),
            "phone_num": request.form.get("phone_num", ""),
            "type_AI": request.form.get("type_AI", ""),
        }
        # type_AI を boolean に変換
        if form_data["type_AI"].lower() in ("1"):
            form_data["type_AI"] = 1
        else:
            form_data["type_AI"] = 0
        print("受け取りデータ",form_data)

        # バリデーション
        error_msg.append(validate_name(form_data["name"]))
        error_msg.append(validate_address(form_data["address"]))
        error_msg.append(validate_phone_num(form_data["phone_num"]))
        error_msg = [msg for msg in error_msg if msg]

        if error_msg:
            return render_template("edit.html", form_data=form_data, error_msg=error_msg)

        # データを更新
        try:
            conn.start_transaction()

            # 新しい station_num が他の駅番号と重複していないか確認
            if form_data["station_num"] != station_num:  # 駅番号が変更された場合
                check_query = "SELECT COUNT(*) AS count FROM station_info WHERE station_num = %s"
                cursor.execute(check_query, (form_data["station_num"],))
                count = cursor.fetchone()["count"]  # 重複数を取得

                if count > 0:  # 既に存在する場合
                    conn.rollback()  # トランザクションを元に戻す
                    error_msg.append("この駅番号は既に存在しています。")
                    return render_template("edit.html", form_data=form_data, error_msg=error_msg)

            # `station_info`テーブルのデータを更新
            update_station_info = """
                UPDATE station_info
                SET name = %s, station_num = %s, address = %s, phone_num = %s, type_AI = %s
                WHERE station_num = %s
            """
            cursor.execute(
                update_station_info,
                (
                    form_data["name"],
                    form_data["station_num"],
                    form_data["address"],
                    form_data["phone_num"],
                    form_data["type_AI"],
                    station_num,
                ),
            )

            print("更新完了", form_data)
            conn.commit()  # トランザクションを確定
        except Exception as e:
            conn.rollback()  # エラーが発生した場合はロールバック
            return f"更新中にエラーが発生しました: {e}", 500
        finally:
            cursor.close()

        return redirect('/user/list?update_done')

# ログアウト処理
@app.route('/user/logout')
def logout():
    session.clear()  # セッションをクリア
    return redirect(url_for('login'))

# レポートページの処理
@app.route("/report", methods=["POST", "GET"])
def report():
    form_data = {
        "responder": "",
        "about": "",
        "detail": "",
        "answer": "",
        "gpt_log_id": ""
    }

    if request.method == "GET":
        try:
            with db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''USE holo_to_talk''')
                    # gpt_talk_log テーブルから id のみ取得
                    cursor.execute('''SELECT id FROM gpt_talk_log''')
                    gpt_log_ids = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            gpt_log_ids = []
            print(f"エラーが発生しました: {e}")

        # GETメソッド用のHTMLレンダリング
        return render_template('report/register.html', form_data=form_data, gpt_log_ids=gpt_log_ids)

    if request.method == "POST":
        # POSTデータを取得
        form_data = {
            "responder": request.form.get("responder", ""),
            "about": request.form.get("about", ""),
            "detail": request.form.get("detail", ""),
            "answer": request.form.get("answer", ""),
            "gpt_log_id": request.form.get("gpt_log_id", "")
        }

        try:
            with db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''USE holo_to_talk''')
                    # staff_logテーブルにデータを挿入
                    cursor.execute('''
                        INSERT INTO staff_log (gpt_log_id, responder, about, detail, answer)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (
                        form_data["gpt_log_id"],
                        form_data["responder"],
                        form_data["about"],
                        form_data["detail"],
                        form_data["answer"]
                    ))
                conn.commit()
            return redirect(url_for('success'))  # 成功ページにリダイレクト
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return "エラーが発生しました", 500


#レポートリスト表示処理
@app.route('/report/list', methods=['GET'])
def report_list():
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
            return render_template('./report/list.html', logs=logs)

        except Exception as e:
            # エラー処理
            error_message = f"データの取得中にエラーが発生しました: {e}"
            return render_template('.report/list.html', error_message=error_message)

        finally:
            # リソースを解放
            cursor.close()
            conn.close()

# アプリケーションを実行
if __name__ == "__main__":
    app.run(debug=True)

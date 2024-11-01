from flask import Flask
from flask_mysql_connector import MySQL
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# MySQL設定
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_PORT'] = (os.getenv('MYSQL_PORT'))

mysql = MySQL(app)

def db_connection():
    # 接続チェック用デバッグ
    if mysql.connection is None:
        return "MySQLへの接続に失敗しました。設定情報を確認してください。"

    try:
        cur = mysql.connection.cursor()
        cur.execute("use holo_to_talk")
        cur.execute("SHOW TABLES")  # 適切なテーブル名に変更
        data = cur.fetchall()
        cur.close()

        return str(data)
    except Exception as e:
        return f"エラーが発生しました: {e}"

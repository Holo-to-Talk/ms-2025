from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from socketio_Config import socketio
from dotenv import load_dotenv
import os
import time

import socketio_emit
import voice_Recording
import audio_To_Text
import qr_code_found
import chatGPT_API_Output
import text_To_Audio
import delete_Recording
import phoneAutomation

app = Flask(__name__)

# SECRET_KEY
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

# SocketIOでFlask appをラップ
socketio.init_app(app)

# 定数
TIME_SLEEP = 1
TIME_SLEEP_COUNT = 8

# グローバル変数
flag_space = False
flag_enter = False
conversation_history = []

# main処理
def ai():
    # 音声ファイルの生成
    savedDirectory = voice_Recording.voice_Recording()

    # 音声ファイルのテキスト化
    inputContent = audio_To_Text.audio_To_Text(savedDirectory)

    # QRCodeを表示するか確認
    global conversation_history
    if qr_code_found.qr_code_found(inputContent):
        # クライアントに送信
        outputContent = "QRCodeを表示します。"
        socketio_emit.socketio_emit_output(outputContent)

        # 音声出力
        socketio_emit.socketio_emit_start_switching()
        text_To_Audio.text_To_Audio(outputContent)
        socketio_emit.socketio_emit_stop_switching()

        # QRCodeを表示する
        # 関数実行

    else:
        # 応答内容の取得
        outputContent = chatGPT_API_Output.chatGPT_API_Output(conversation_history, inputContent)
        socketio_emit.socketio_emit_output(outputContent)

        # 音声出力
        socketio_emit.socketio_emit_start_switching()
        text_To_Audio.text_To_Audio(outputContent)
        socketio_emit.socketio_emit_stop_switching()

    # 音声ファイルの削除
    delete_Recording.delete_Recording(savedDirectory)

    # クライアントに送信
    socketio_emit.socketio_emit_output_reset()
    telopContent = "電話対応をご希望の場合、Spaceを押してください。"
    socketio_emit.socketio_emit_telop(telopContent)
    socketio_emit.socketio_emit_telop_remove_display_none()

    # 電話をかけるか確認
    global flag_space
    count = 0
    while True:
        if flag_space:
            # クライアントに送信
            telopContent = "駅員に電話をかけます。"
            socketio_emit.socketio_emit_telop(telopContent)

            # 電話をかける
            phoneAutomation.phoneAutomation()
            break

        else:
            time.sleep(TIME_SLEEP)
            count += 1

        if count == TIME_SLEEP_COUNT:
            # Spaceキーを受付不可
            socketio_emit.socketio_emit_flag_space()

            flag_space = True
            break

    # クライアントに送信
    telopContent = "会話を続ける（会話を保存する）場合、Enterを押してください。"
    socketio_emit.socketio_emit_telop(telopContent)

    # 会話を続けるか確認（会話を保存するか）
    global flag_enter
    count = 0
    while True:
        if flag_enter:
            # 会話履歴の保存
            conversation_history.append({"role": "user", "content": inputContent})
            conversation_history.append({"role": "assistant", "content": outputContent})

            # クライアントに送信
            telopContent = "会話を保存しました。"
            socketio_emit.socketio_emit_telop(telopContent)

            break
        else:
            time.sleep(TIME_SLEEP)
            count += 1

        if count == TIME_SLEEP_COUNT:
            # 会話履歴の初期化
            conversation_history = []

            flag_enter = True
            break

    # クライアントに送信
    telopContent = "Enterを押して始めてください"
    socketio_emit.socketio_emit_telop(telopContent)

    # flag初期化
    flag_enter = False
    socketio_emit.socketio_emit_flag_enter()
    flag_space = False
    socketio_emit.socketio_emit_flag_space()

@app.route('/')
def main():
    return render_template('index.html')

# Enterキーが押されたときのイベント処理
@socketio.on('enter_starting')
def handle_enter_event():
    # Enterキーを受付不可に
    socketio_emit.socketio_emit_flag_enter()

    # 別スレッドで実行
    socketio.start_background_task(target = ai)

# Enterキーが押されたときのイベント処理
@socketio.on('enter_conversation')
def handle_enter_event2():
    global flag_enter
    flag_enter = True

# Spaceキーが押されたときのイベント処理
@socketio.on('space_phone')
def handle_space_event():
    # Spaceキーを受付不可
    socketio_emit.socketio_emit_flag_space()

    global flag_space
    flag_space = True

if __name__ == '__main__':
    socketio.run(app)
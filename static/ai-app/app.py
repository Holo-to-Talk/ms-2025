from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from socketio_Config import socketio
from dotenv import load_dotenv
import os

import voice_Recording
import audio_To_Text
import chatGPT_API_Output
import delete_Recording
import text_To_Audio
import phoneAutomation

app = Flask(__name__)

# SECRET_KEY
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

# SocketIOでFlask appをラップ
socketio.init_app(app)

# main処理
def ai():
    # 音声ファイルの生成
    savedDirectory = voice_Recording.voice_Recording()

    # 音声ファイルのテキスト化
    inputContent = audio_To_Text.audio_To_Text(savedDirectory)

    # 応答内容の取得
    outputContent = chatGPT_API_Output.chatGPT_API_Output(inputContent)

    # 音声ファイルの削除
    delete_Recording.delete_Recording(savedDirectory)

    # APIの回答の確認
    if outputContent == 'phoneAutomation':
        outputContent = '回答することが難しいため、駅員に電話をかけます。'

        # クライアント側にテキスト送信
        socketio.emit('update_output', {'output': outputContent})

        # 電話をかける
        phoneAutomation.phoneAutomation()
    else :
        # クライアント側にテキスト送信
        socketio.emit('update_output', {'output': outputContent})

        # 音声出力
        text_To_Audio.text_To_Audio(outputContent)

@app.route('/')
def main():
    return render_template('index.html')

# Enterキーが押されたときのイベント処理
@socketio.on('enter_pressed')
def handle_enter_event():
    # 別スレッドで実行
    socketio.start_background_task(target = ai)

if __name__ == '__main__':
    socketio.run(app)
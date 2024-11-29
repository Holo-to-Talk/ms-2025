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

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

socketio.init_app(app)

TIME_SLEEP = 1
TIME_SLEEP_COUNT = 8

flag_space = False
flag_enter2 = False
conversation_history = []

def ai():
    savedDirectory = voice_Recording.voice_Recording()

    inputContent = audio_To_Text.audio_To_Text(savedDirectory)

    delete_Recording.delete_Recording(savedDirectory)

    global conversation_history
    if qr_code_found.qr_code_found(inputContent):
        outputContent = "QRCodeを表示します。"
        socketio_emit.socketio_emit_output(outputContent)

        socketio_emit.socketio_emit_start_switching()
        text_To_Audio.text_To_Audio(outputContent)
        socketio_emit.socketio_emit_stop_switching()

        socketio_emit.socketio_emit_output_reset()

        socketio_emit.socketio_emit_image_qr_add_active()
        time.sleep(TIME_SLEEP * TIME_SLEEP_COUNT)
        socketio_emit.socketio_emit_image_qr_remove_active()

    else:
        outputContent = chatGPT_API_Output.chatGPT_API_Output(conversation_history, inputContent)
        socketio_emit.socketio_emit_output(outputContent)

        socketio_emit.socketio_emit_start_switching()
        text_To_Audio.text_To_Audio(outputContent)
        socketio_emit.socketio_emit_stop_switching()

        socketio_emit.socketio_emit_output_reset()

    outputContent = "電話対応をご希望の場合、Spaceキーを押してください。"
    socketio_emit.socketio_emit_output(outputContent)

    socketio_emit.socketio_emit_start_switching()
    text_To_Audio.text_To_Audio(outputContent)
    socketio_emit.socketio_emit_stop_switching()

    socketio_emit.socketio_emit_output_reset()

    global flag_space
    count = 0
    while True:
        if flag_space:
            outputContent = "駅員に電話をかけます。"
            socketio_emit.socketio_emit_output(outputContent)

            socketio_emit.socketio_emit_start_switching()
            text_To_Audio.text_To_Audio(outputContent)
            socketio_emit.socketio_emit_stop_switching()

            socketio_emit.socketio_emit_output_reset()

            phoneAutomation.phoneAutomation()
            break

        else:
            time.sleep(TIME_SLEEP)
            count += 1

        if count == TIME_SLEEP_COUNT:
            socketio_emit.socketio_emit_flag_space()
            flag_space = True
            break

    outputContent = "会話を続ける（会話を保存する）場合、Enterキーを押してください。"
    socketio_emit.socketio_emit_output(outputContent)

    socketio_emit.socketio_emit_start_switching()
    text_To_Audio.text_To_Audio(outputContent)
    socketio_emit.socketio_emit_stop_switching()

    socketio_emit.socketio_emit_output_reset()

    global flag_enter2
    count = 0
    while True:
        if flag_enter2:
            conversation_history.append({"role": "user", "content": inputContent})
            conversation_history.append({"role": "assistant", "content": outputContent})

            outputContent = "会話を保存しました。"
            socketio_emit.socketio_emit_output(outputContent)

            socketio_emit.socketio_emit_start_switching()
            text_To_Audio.text_To_Audio(outputContent)
            socketio_emit.socketio_emit_stop_switching()

            socketio_emit.socketio_emit_output_reset()
            break

        else:
            time.sleep(TIME_SLEEP)
            count += 1

        if count == TIME_SLEEP_COUNT:
            conversation_history = []

            socketio_emit.socketio_emit_flag_enter2()
            flag_enter2 = True
            break

    telopContent = "Enterを押して始めてください。"
    socketio_emit.socketio_emit_telop_remove_display_none()
    socketio_emit.socketio_emit_telop(telopContent)

    flag_enter2 = False
    socketio_emit.socketio_emit_flag_enter2()
    flag_space = False
    socketio_emit.socketio_emit_flag_space()

@app.route('/')
def main():
    return render_template('index.html')

@socketio.on('enter_starting')
def handle_enter_event():
    socketio_emit.socketio_emit_flag_enter()

    socketio.start_background_task(target = ai)

@socketio.on('enter_conversation')
def handle_enter_event2():
    socketio_emit.socketio_emit_flag_enter2()

    global flag_enter2
    flag_enter2 = True

@socketio.on('space_phone')
def handle_space_event():
    socketio_emit.socketio_emit_flag_space()

    global flag_space
    flag_space = True

if __name__ == '__main__':
    socketio.run(app)
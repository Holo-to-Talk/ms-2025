import openai
from dotenv import load_dotenv
import os

import socketio_emit

def audio_To_Text(savedDirectory):
    # 定数
    load_dotenv()
    # API Key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # ChatGPT Model
    MODEL = os.getenv("AUDIO_TO_TEXT_MODEL")

    # 音声ファイルのパスの指定
    audio_file_path = savedDirectory

    # 音声ファイルをバイナリで読み込む
    with open(audio_file_path, 'rb') as audio_file:
        # Whisper APIにリクエストを送る
        transcription = openai.Audio.transcribe(MODEL, audio_file)

        # テキスト変換結果を出力
        inputContent = transcription['text']

        # クライアントに送信
        socketio_emit.socketio_emit_telop_add_display_none()

        # クライアントに送信
        socketio_emit.socketio_emit_input(inputContent)

        # テキスト変換結果の返し
        return inputContent
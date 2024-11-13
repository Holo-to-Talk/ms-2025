import openai
from dotenv import load_dotenv
import os

def audio_To_Text(savedDirectory):
    # 定数
    # API Key
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # 音声ファイルのパスの指定
    audio_file_path = savedDirectory

    # 音声ファイルをバイナリで読み込む
    with open(audio_file_path, 'rb') as audio_file:
        # Whisper APIにリクエストを送る
        transcription = openai.Audio.transcribe("whisper-1", audio_file)

        # テキスト変換結果を出力
        inputContent = transcription['text']

        # テキスト変換結果の表示
        print(inputContent)

        # テキスト変換結果の返し
        return inputContent
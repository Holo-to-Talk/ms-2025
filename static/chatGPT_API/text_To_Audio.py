import pyttsx3

def text_To_Audio(outputContent):
    # エンジンの初期化
    engine = pyttsx3.init()

    # 音声プロパティの設定
    # 話す速度（デフォルト：200）
    engine.setProperty('rate', 150)
    # 話す音量（0 - 1.0）
    engine.setProperty('volume', 0.9)

    # テキストの設定
    text = outputContent
    engine.say(text)

    # 音声出力の開始
    engine.runAndWait()
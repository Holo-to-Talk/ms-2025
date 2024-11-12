import openai

def audio_To_Text(savedDirectory):
    # 定数
    # API Key
    openai.api_key = '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'

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
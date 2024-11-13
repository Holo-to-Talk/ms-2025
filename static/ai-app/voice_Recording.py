import pyaudio
import wave
import numpy as np
import os

def voice_Recording():
    # 録音設定
    # 音声のフォーマット（16ビットの整数型）
    FORMAT = pyaudio.paInt16
    # モノラル録音
    CHANNELS = 1
    # サンプルレート（Hz）
    RATE = 44100
    # チャンクサイズ（バッファの単位）
    CHUNK = 1024
    # 出力ファイル名
    OUTPUT_FILE = "inputText.wav"
    # 無音判定の閾値（デフォルト：1000）
    THRESHOLD = 500
    # 無音が続く秒数（要相談）
    SILENCE_DURATION = 3

    # pyaudioインスタンスの作成
    audio = pyaudio.PyAudio()

    # 録音開始
    stream = audio.open(
        format = FORMAT,
        channels = CHANNELS,
        rate = RATE,
        input = True,
        frames_per_buffer = CHUNK
    )

    print("Recording...")

    frames = []
    # 無音が続くチャンク数
    silent_chunks = 0

    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        # numpy配列に変換して音声レベルを計算
        audio_data = np.frombuffer(data, dtype = np.int16)
        volume = np.abs(audio_data).mean()

        # 音声レベルが閾値以下かどうかを確認
        if volume < THRESHOLD:
            silent_chunks += 1
        else:
            silent_chunks = 0

        # 無音がSILENCE_DURATION分続いた場合、録音を終了
        if silent_chunks > int(RATE / CHUNK * SILENCE_DURATION):
            print("Silence detected, stopping recording")
            break

    # 録音停止とストリームの終了
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 録音データをWAVファイルに保存
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # 保存したディレクトリを取得
    saved_directory = os.path.abspath(OUTPUT_FILE)
    print("Recording saved to", saved_directory)

    # 保存したディレクトリの返し
    return saved_directory
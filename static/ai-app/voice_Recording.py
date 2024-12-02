import pyaudio
import wave
import numpy as np
from dotenv import load_dotenv
import os

import socketio_emit

def voice_Recording():
    load_dotenv()

    FORMAT = pyaudio.paInt16

    CHANNELS = 1

    RATE = 44100

    CHUNK = 1024

    OUTPUT_FILE = "inputText.wav"

    THRESHOLD = int(os.getenv("THRESHOLD"))

    SILENCE_DURATION = int(os.getenv("SILENCE_DURATION"))

    audio = pyaudio.PyAudio()

    stream = audio.open(
        format = FORMAT,
        channels = CHANNELS,
        rate = RATE,
        input = True,
        frames_per_buffer = CHUNK
    )

    telopContent = "録音しています"
    socketio_emit.socketio_emit_telop(telopContent)

    frames = []
    silent_chunks = 0

    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        audio_data = np.frombuffer(data, dtype = np.int16)
        volume = np.abs(audio_data).mean()

        if volume < THRESHOLD:
            silent_chunks += 1

        else:
            silent_chunks = 0

        if silent_chunks > int(RATE / CHUNK * SILENCE_DURATION):
            telopContent = "録音が終わりました"
            socketio_emit.socketio_emit_telop(telopContent)
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    saved_directory = os.path.abspath(OUTPUT_FILE)

    return saved_directory
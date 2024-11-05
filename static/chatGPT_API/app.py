import voice_Recording
import audio_To_Text
import chatGPT_API_Output
import delete_Recording

def main():
    # 音声ファイルの生成
    savedDirectory = voice_Recording.voice_Recording()

    # 音声ファイルのテキスト化・取得
    inputContent = audio_To_Text.audio_To_Text(savedDirectory)

    # 応答内容の取得
    outputContent = chatGPT_API_Output.chatGPT_API_Output(inputContent)

    # 音声ファイルの削除
    delete_Recording.delete_Recording(savedDirectory)

if __name__ == "__main__":
    main()
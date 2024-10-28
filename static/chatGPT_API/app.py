import chatGPT_API_Input
import chatGPT_API_Output

def main():
    # 入力内容の取得
    inputContent = chatGPT_API_Input.chatGPT_API_Input()

    # 応答内容の取得
    outputContent = chatGPT_API_Output.chatGPT_API_Output(inputContent)

    # 応答内容の表示
    print(outputContent)

if __name__ == "__main__":
    main()
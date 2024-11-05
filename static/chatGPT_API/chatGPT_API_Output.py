import openai

def chatGPT_API_Output(inputContent):
    # 定数
    # API Key
    openai.api_key = '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'

    # ChatGPT APIに入力
    response = openai.ChatCompletion.create(
        # ChatGPT APIのモデル（要相談）
        model = "gpt-3.5-turbo",

        # ChatGPT APIの入力内容
        messages = [
            {"role": "user", "content": inputContent}
        ],

        # 最大トークン数の指定（要相談）
        max_tokens = 10,

        # 創造性の度合い
        temperature = 0.7,
    )

    # 応答内容の取得
    outputContent = response['choices'][0]['message']['content']

    # 応答内容の表示
    print(outputContent)

    # 応答内容の返し
    return outputContent
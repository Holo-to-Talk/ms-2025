import openai
from dotenv import load_dotenv
import os

def chatGPT_API_Output(inputContent):
    # 定数
    # API Key
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # ChatGPT APIに入力
    response = openai.ChatCompletion.create(
        # ChatGPT APIのモデル（要相談）
        model = "g-673c43bd77a48191ab82923135b8a3e5",

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
import openai
from dotenv import load_dotenv
import os

def chatGPT_API_Output(inputContent):
    # 定数
    load_dotenv()
    # API Key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # ChatGPT Model
    OUTPUT_MODEL = os.getenv("OUTPUT_MODEL")
    # Max Token
    MAX_TOKENS = int(os.getenv("MAX_TOKENS"))

    # ChatGPT APIに入力
    response = openai.ChatCompletion.create(
        # ChatGPT APIのモデル
        model = OUTPUT_MODEL,

        # ChatGPT APIの入力内容
        messages = [
            {"role": "user", "content": inputContent}
        ],

        # 最大トークン数の指定
        max_tokens = MAX_TOKENS,

        # 創造性の度合い
        temperature = 0.7,
    )

    # 応答内容の取得
    outputContent = response['choices'][0]['message']['content']

    # 応答内容の表示
    print(outputContent)

    # 応答内容の返し
    return outputContent
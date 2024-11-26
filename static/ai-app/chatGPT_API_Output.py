import openai
from dotenv import load_dotenv
import os

def chatGPT_API_Output(conversation_history, inputContent):
    # 定数
    load_dotenv()
    # API Key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # ChatGPT Model
    OUTPUT_MODEL = os.getenv("OUTPUT_MODEL")
    # Max Token
    MAX_TOKENS = int(os.getenv("MAX_TOKENS"))

    # 会話履歴があれば使用
    if conversation_history:
        conversation_history.append({"role": "user", "content": inputContent})
        messages = conversation_history
    else:
        messages = [
            {"role": "user", "content": inputContent}
        ]

    # ChatGPT APIに入力
    response = openai.ChatCompletion.create(
        # ChatGPT APIのモデル
        model = OUTPUT_MODEL,

        # 会話内容（入力内容）
        messages = messages,

        # 最大トークン数の指定
        max_tokens = MAX_TOKENS,

        # 創造性の度合い
        temperature = 0.7,
    )

    # 応答内容の取得
    outputContent = response['choices'][0]['message']['content']

    # 応答内容の返し
    return outputContent
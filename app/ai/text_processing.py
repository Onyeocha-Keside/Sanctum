import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_text(text, max_tokens = 100):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "you are an assistnt that summarizes text giving high quality output"},
            {"role": "user", "content": f"please summarize the text in about {max_tokens} tokens: \n\n{text}"}
        ],
        max_tokens = max_tokens
    )

    return response.choices[0].messages["content"].strip()
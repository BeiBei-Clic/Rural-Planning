from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

print("OPENAI_BASE_URL:", os.getenv("OPENAI_BASE_URL"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

client = OpenAI(
  base_url=os.getenv("OPENAI_BASE_URL"),
  api_key=os.getenv("OPENAI_API_KEY"),
)


completion = client.chat.completions.create(
  extra_body={},
  model="deepseek/deepseek-chat-v3-0324:free",
  messages=[
    {
      "role": "user",
      "content": "你好"
    }
  ]
)
print(completion.choices[0].message.content)
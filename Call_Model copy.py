import asyncio
import os
from asyncio import Semaphore
from typing import List
from dotenv import load_dotenv

from openai import AsyncOpenAI

load_dotenv()

async def call_model(sem: Semaphore, request: str, model: str) -> dict:
    """Send a single request to the specified model with semaphore control."""
    async with sem:
        # 根据 model 参数选择不同的 API 配置
        if "gemini" in model.lower():
            # Gemini 模型的 API 配置
            client = AsyncOpenAI(
                api_key=os.getenv("GEMINI_API_KEY"),
                base_url=os.getenv("GEMINI_API_BASE", "https://gemini-api.example.com")
            )
        else:
            # 默认使用 OpenAI 的 API 配置
            client = AsyncOpenAI(
                api_key=os.getenv("XAI_API_KEY"),
                base_url=os.getenv("XAI_API_BASE", "https://api.openai.com/v1")
            )
        
        return await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": request}]
        )

async def main() -> None:
    """Main function to handle requests and display responses."""
    prompt = "你好"

    # 使用 Gemini 模型
    gemini_response = await call_model(
        Semaphore(1000), prompt, "google/gemini-2.5-pro-exp-03-25:free"
    )
    print("Gemini 模型的回复：")
    print(gemini_response.choices[0].message.content)

    # 使用 OpenAI 模型
    openai_response = await call_model(Semaphore(1000), prompt, "grok-3-mini-beta")
    print("\nOpenAI 模型的回复：")
    print(openai_response.choices[0].message.content)

if __name__ == "__main__":
    os.system('cls')
    asyncio.run(main())
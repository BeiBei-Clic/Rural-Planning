import asyncio
import os
from asyncio import Semaphore
from typing import List
from dotenv import load_dotenv

from openai import AsyncOpenAI

load_dotenv()

# print(os.getenv("XAI_API_KEY"))
# print(os.getenv("XAI_API_BASE"))

async def call_model(sem: Semaphore, request: str, model:str) -> dict:
    """Send a single request to xAI with semaphore control."""
    # The 'async with sem' ensures only a limited number of requests run at once
    async with sem:
        client = AsyncOpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url=os.getenv("XAI_API_BASE")
)
        return await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": request}]
        )
    
async def main() -> None:
    """Main function to handle requests and display responses."""
    prompt="你好"

    # This starts processing all asynchronously, but only 2 at a time
    # Instead of waiting for each request to finish before starting the next,
    # we can have 2 requests running at once, making it faster overall
    response = await call_model(Semaphore(1000), prompt, "grok-3-mini-beta")
    print(response.choices[0].message.content)
    

if __name__ == "__main__":
    os.system('cls')
    asyncio.run(main())
 
   
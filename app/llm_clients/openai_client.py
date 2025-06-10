from app.config import llm_config
from openai import AsyncOpenAI
from openai.types.chat import ParsedChatCompletion
from pydantic import BaseModel


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=llm_config.OPENAI_API_KEY)

    async def call(self, model: str, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""

    async def call_structured[T: BaseModel](self, model: str, prompt: str, output_model: type[T]) -> T:
        openai_response: ParsedChatCompletion = await self.client.beta.chat.completions.parse(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format=output_model,
        )

        message = openai_response.choices[0].message
        if parsed_response := message.parsed:
            return parsed_response
        raise ValueError("No response from LLM")


openai_client = OpenAIClient()

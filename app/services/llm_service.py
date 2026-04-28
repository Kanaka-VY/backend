from openai import OpenAI
from app.schemas.chat import ChatMessage
from app.core.config import settings


def generate_reply(messages: list[ChatMessage]) -> str:
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not configured")

    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": m.role, "content": m.content} for m in messages],
        temperature=0.7,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response from model")

    return content
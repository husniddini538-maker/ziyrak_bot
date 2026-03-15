from groq import AsyncGroq
from config.settings import settings

client = AsyncGroq(api_key=settings.GROQ_API_KEY)


async def ask_gpt(
    system_prompt: str,
    user_message: str,
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 2000,
) -> str:
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI xatosi: {e}"

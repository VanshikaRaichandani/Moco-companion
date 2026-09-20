import os
import time
from groq import Groq


def get_client():
    # Read API key directly from system environment variables
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables.")

    return Groq(api_key=api_key)


def generate_response(messages, system_prompt):
    client = get_client()

    groq_messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    groq_messages.extend(messages)

    try:
        stream = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=groq_messages,
            stream=True,
        )

        for chunk in stream:
            if (
                chunk.choices
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                text = chunk.choices[0].delta.content

                for char in text:
                    yield char
                    time.sleep(0.01)

    except Exception as e:
        print("GROQ ERROR:", repr(e))
        yield f"⚠️ Moco error: {str(e)}"
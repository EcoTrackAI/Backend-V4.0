import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_URL = os.getenv(
    "GROQ_URL",
    "https://api.groq.com/openai/v1/chat/completions"
)


def extract_first_two_sentences(text: str) -> str:
    if not text:
        return "No recommendation generated."

    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(sentences[:2]).strip()


def ask_mistral(context: dict) -> str:
    try:

        prompt = f"""
You are a smart home energy assistant for an Indian household.

Rules:
- Use AC (not thermostat), Lights, fans, fridge and other appliances as reference.
- Be concise.
- Give practical advice.
- Consider outdoor weather and time of day.
- If motion is detected i.e 1, consider that the room is occupied, give advice accordingly.
- No need to give extra advice and don't explain the reasoning. Just give the advice.

Indoor Temp: {context.get('current_indoor_temp')}°C
Predicted Temp: {context.get('predicted_indoor_temp')}°C
Outdoor Temp: {context.get('outdoor_temp')}
Indoor Humidity: {context.get('current_humidity')}%
Predicted Humidity: {context.get('predicted_humidity')}%
Outdoor Humidity: {context.get('outdoor_humidity')}
Motion: {context.get('motion')}
Light: {context.get('light')}
Hour: {context.get('hour')}

Give energy-saving advice.
"""

        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 150
            },
            timeout=20
        )

        if response.status_code != 200:
            return f"Groq API Error: {response.text}"

        data = response.json()

        full_response = data["choices"][0]["message"]["content"]

        return full_response

    except Exception as e:
        return f"LLM Exception: {str(e)}"
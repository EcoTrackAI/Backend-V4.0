import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def extract_first_two_sentences(text: str) -> str:
    if not text:
        return "No recommendation generated."

    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return " ".join(sentences[:2]).strip()


def ask_llm(context: dict) -> str:
    try:
        if not GROQ_API_KEY:
            return "Missing GROQ API key"

        print("LLM request triggered")

        prompt = f"""You are an intelligent energy optimization assistant.

Give a SHORT and PRACTICAL recommendation (max 2 sentences).

Consider:
- Reduce energy usage
- Maintain comfort
- Use motion and light intelligently

DATA:
Indoor Temp: {context.get('current_indoor_temp')}
Predicted Temp: {context.get('predicted_indoor_temp')}
Outdoor Temp: {context.get('outdoor_temp')}
Humidity: {context.get('current_humidity')}
Motion: {context.get('motion')}
Light: {context.get('light')}
Hour: {context.get('hour')}
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
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 120
            },
            timeout=20
        )

        if response.status_code != 200:
            return "Unable to generate recommendation right now. Try again shortly."

        data = response.json()

        if "choices" not in data:
            return "Invalid response from LLM."

        return extract_first_two_sentences(
            data["choices"][0]["message"]["content"]
        )

    except Exception as e:
        print("LLM EXCEPTION:", e)
        return "LLM service temporarily unavailable."
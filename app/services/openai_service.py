import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

async def generate_completion(prompt: str, max_tokens: int = 4000) -> dict:
    try:
        print(f"[DEBUG] Sending request to Groq ({GROQ_MODEL})...")

        timeout_config = httpx.Timeout(
            connect=5.0,
            read=15.0,
            write=15.0,
            pool=15.0
        )

        async with httpx.AsyncClient(timeout=timeout_config) as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an expert Sri Lanka travel planner. "
                                "Always respond with valid JSON only. "
                                "No markdown. No explanation. Pure JSON."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "response_format": {"type": "json_object"}
                }
            )

            print(f"[DEBUG] Response status: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            print(f"[DEBUG] Response received! Length: {len(content)} chars")

            clean = content.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]

            return json.loads(clean.strip())

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse error: {e}")
        raise ValueError(f"Invalid JSON from Groq: {e}")
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] HTTP error: {e.response.status_code} - {e.response.text}")
        raise RuntimeError(f"Groq HTTP error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
        raise RuntimeError(f"Groq API error: {e}")
import os
import json
import re
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

async def gemini_analysis(messages):
    # If messages is a list of objects (with `text`, `time`), convert to plain strings
    if isinstance(messages, list):
        messages = "\n".join([msg["text"] if isinstance(msg, dict) else str(msg) for msg in messages])

    prompt = f"""
    Analyze the following WhatsApp messages and respond ONLY in valid JSON.

    Return the following structure exactly, without markdown or comments:

    ```json
    {{
      "summary": "A short summary of the overall chat.",
      "sentiment_counts": {{
        "positive": 0,
        "neutral": 0,
        "negative": 0
      }},
      "keywords": ["keyword1", "keyword2"],
      "recommended_actions": ["Action 1", "Action 2"],
      "insights": [
        {{
          "label": "Insight or issue",
          "type": "problem/observation/action",
          "sentiment": "positive/neutral/negative"
        }}
      ]
    }}
    ```

    Messages:
    {messages}

    IMPORTANT: Respond with JSON only. Do NOT include explanations, markdown headings, or additional text.
    """

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    try:
        response = model.generate_content(prompt)
        raw = response.text

        # Clean up markdown-style wrapping (```json ... ```)
        cleaned = re.sub(r"```json|```", "", raw).strip()

        result = json.loads(cleaned)
        return result

    except json.JSONDecodeError as e:
        return {
            "error": "❌ Gemini returned invalid JSON.",
            "exception": str(e),
            "raw": response.text,
        }
    except Exception as e:
        return {
            "error": "❌ Unexpected failure in gemini_analysis.",
            "exception": str(e)
        }


def estimate_tokens(messages: List[str]) -> int:
    all_text = " ".join(messages)
    word_count = len(all_text.split())
    estimated_tokens = word_count // 4 
    return estimated_tokens

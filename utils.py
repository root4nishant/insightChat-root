import os
import json
import re
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

async def gemini_analysis(messages):
    if isinstance(messages, list):
        messages = "\n".join([msg["text"] if isinstance(msg, dict) else str(msg) for msg in messages])

    prompt = f"""
    Analyze the following WhatsApp messages and respond ONLY in valid JSON.

    Return the structure below with no markdown, no comments, no explanations:

    {{
      "summary": "A short summary of the chat.",
      "sentiment_counts": {{
        "positive": 0,
        "neutral": 0,
        "negative": 0
      }},
      "keywords": ["keyword1", "keyword2"],
      "topic_frequency": {{
        "product": 5,
        "delivery": 2,
        "payment": 3
      }},
      "message_volume_timeline": {{
        "2024-04-01": 15,
        "2024-04-02": 23,
        "2024-04-03": 5
      }},
      "recommended_actions": ["Action 1", "Action 2"],
      "insights": [
        {{
          "label": "Insight or issue",
          "type": "problem/observation/action",
          "sentiment": "positive/neutral/negative"
        }}
      ]
    }}

    Instructions:
    - Use the actual content to derive topic frequency.
    - Create a simple message volume timeline across 3–5 mock date buckets.
    - Use only lowercase keys and valid JSON.
    - Do not return markdown, code blocks or extra explanation.

    Chat Messages:
    {messages}
    """

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    try:
        response = model.generate_content(prompt)
        raw = response.text
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


async def gemini_chatbot_response(messages: list, user_query: str) -> str:
    """
    Use Gemini to answer user questions based on raw chat messages.
    
    messages: list of dicts like { "sender": "user", "text": "..." }
    user_query: the user's natural language question (any language).
    """
    import os
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Use the last 20 messages for context
    last_messages = messages[-20:] if len(messages) >= 20 else messages
    message_text = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in last_messages if "text" in msg])

    # Enhanced prompt
    prompt = f"""
You are a multilingual chat analysis assistant. You help users understand WhatsApp-like chats by answering their questions clearly and concisely.

Chat messages:
{message_text}

User's question:
"{user_query}"

Guidelines:
- Respond in the same language as the user's query.
- Use short answers (1–3 lines max).
- If the user asks about:
  - **Sentiment** → mention positive/negative/neutral counts and examples.
  - **Links** → extract and list them if present.
  - **Summary** → give a short overview.
  - **Insights** → describe patterns, repeated concerns or praise.
- Don't return code blocks, markdown, or long explanations.

Reply now in plain text:
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {str(e)}"

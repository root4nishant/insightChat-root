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



async def gemini_chatbot_response(session_data: dict, user_query: str) -> str:
    """
    Use Gemini to answer user questions about a past session.
    session_data = {
        "summary": "...",
        "sentiment_counts": {...},
        "keywords": [...],
        "topic_frequency": {...},
        "insights": [...],
        "messages": [...]
    }
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Construct prompt using session data
    prompt = f"""
    You are an AI assistant that helps users understand their chat analytics.

    Here is their previous session analysis:
    - Summary: {session_data.get("summary", "")}
    - Sentiment counts: {session_data.get("sentiment_counts", {})}
    - Keywords: {', '.join(session_data.get("keywords", []))}
    - Topic frequency: {session_data.get("topic_frequency", {})}
    - Insights: {session_data.get("insights", [])}

    Chat messages: {session_data.get("messages", [])[-10:]}  # Optional context

    Now, the user is asking:
    "{user_query}"

    Provide a helpful, concise answer in plain English.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Failed to generate response: {str(e)}"

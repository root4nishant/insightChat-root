# def fake_ai_analysis(messages: list[str]) -> str:
#     return f"AI says: Analyzed {len(messages)} messages. Good job!"


import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

async def gemini_analysis(messages):
    prompt = "\n".join(messages)  # You can also add formatting or context
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text

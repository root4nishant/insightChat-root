import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

async def gemini_analysis(messages):
    prompt = """
    Analyze the following messages and extract valuable information. 
    Provide the response in a separated and structured format, covering aspects like:
    - Key insights
    - Action items
    - Sentiment analysis
    - Important keywords
    - Summary
    
    Messages:
    """ + "\n".join(messages)
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text

"""
Test Gemini API to find correct model name
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {GEMINI_API_KEY[:20]}...")

genai.configure(api_key=GEMINI_API_KEY)

# Try different model names
model_names = [
    'gemini-pro',
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'models/gemini-pro',
    'models/gemini-1.5-pro',
    'models/gemini-1.5-flash',
]

for model_name in model_names:
    try:
        print(f"\nTrying model: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, respond with 'OK' if you can read this")
        print(f"✅ SUCCESS! Model {model_name} works!")
        print(f"Response: {response.text}")
        break
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")

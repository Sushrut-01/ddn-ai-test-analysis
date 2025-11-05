"""
List all available Gemini models for the configured API key
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {GEMINI_API_KEY[:20]}...")
print()

genai.configure(api_key=GEMINI_API_KEY)

print("=" * 70)
print("AVAILABLE GEMINI MODELS")
print("=" * 70)
print()

try:
    models = genai.list_models()

    # Filter models that support generateContent
    generate_models = []

    for model in models:
        print(f"Model: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Supported Methods: {model.supported_generation_methods}")
        print()

        if 'generateContent' in model.supported_generation_methods:
            generate_models.append(model.name)

    print("=" * 70)
    print("MODELS THAT SUPPORT generateContent:")
    print("=" * 70)
    for model_name in generate_models:
        print(f"  - {model_name}")
    print()

    # Try to use the first available model
    if generate_models:
        test_model_name = generate_models[0]
        print(f"Testing first available model: {test_model_name}")
        print()

        model = genai.GenerativeModel(test_model_name)
        response = model.generate_content("Hello, respond with 'OK' if you can read this")
        print(f"[SUCCESS] Model {test_model_name} works!")
        print(f"Response: {response.text}")
    else:
        print("[ERROR] No models support generateContent method")

except Exception as e:
    print(f"[ERROR] {str(e)}")

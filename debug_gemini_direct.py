import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('GOOGLE_API_KEY')

print(f"Key loaded: {api_key[:10]}...")

genai.configure(api_key=api_key)
print("Listing models to file...")
try:
    with open('gemini_models.txt', 'w') as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(m.name + '\n')
    print("Done writing models.")
except Exception as e:
    print(f"Error: {e}")

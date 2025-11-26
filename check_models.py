import google.generativeai as genai
import os

# 1. Paste your real API Key here
os.environ["GEMINI_API_KEY"] = "AIzaSyDQQCf0pFmDESvVJs6N-7d3jVKdEZ2d4hw" 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

print("Checking available models for your key...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"FOUND: {m.name}")
except Exception as e:
    print(f"Error: {e}")
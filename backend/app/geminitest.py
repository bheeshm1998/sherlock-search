import os

import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Select the generative model
model = genai.GenerativeModel('models/gemini-1.5-pro')  # Or 'gemini-pro-vision' for image inputs

# Example prompt
prompt = "Write a short summary of Sherlock Holmes."

# Generate content
response = model.generate_content(prompt)

# Print the generated text
print(response.text)
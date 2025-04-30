import os
from google import genai


api_key = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)
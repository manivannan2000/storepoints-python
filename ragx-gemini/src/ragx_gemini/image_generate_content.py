import os
from PIL import Image
from google import genai

api_key = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

image = Image.open("../../images/beautiful-sitar-classical-music-instrument_96037-395.png")
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[image, "Tell me about this instrument"]
)
print(response.text)

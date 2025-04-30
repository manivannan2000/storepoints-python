import os
from google import genai

api_key = os.environ["GEMINI_API_KEY"]


client = genai.Client(api_key=api_key)
chat = client.chats.create(model="gemini-2.0-flash")

response = chat.send_message_stream("I have 2 cats in my house.")
for chunk in response:
    print(chunk.text, end="")

response = chat.send_message_stream("How many paws are in my house?")
for chunk in response:
    print(chunk.text, end="")

for message in chat.get_history():
    print(f'role - {message.role}', end=": ")
    print(message.parts[0].text)
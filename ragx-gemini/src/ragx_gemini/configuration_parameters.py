import os
from google import genai
from google.genai import types

api_key = os.environ["GEMINI_API_KEY"]


client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["Explain how AI works"],
    config=types.GenerateContentConfig(
        max_output_tokens=500,
        temperature=0.1
    )
)
print(response.text)

"""
Here are some of the model parameters you can configure. (Naming conventions vary by programming language.)

stopSequences: Specifies the set of character sequences (up to 5) that will stop output generation. If specified, the 
API will stop at the first appearance of a stop_sequence. The stop sequence won't be included as part of the response.
temperature: Controls the randomness of the output. Use higher values for more creative responses, and lower values 
for more deterministic responses. Values can range from [0.0, 2.0].

maxOutputTokens: Sets the maximum number of tokens to include in a candidate.

topP: Changes how the model selects tokens for output. Tokens are selected from the most to least probable until the 
sum of their probabilities equals the topP value. The default topP value is 0.95.

topK: Changes how the model selects tokens for output. A topK of 1 means the selected token is the most probable among
 all the tokens in the model's vocabulary, while a topK of 3 means that the next token is selected from among the 3 most
  probable using the temperature. Tokens are further filtered based on topP with the final token selected using 
  temperature sampling.
  
"""
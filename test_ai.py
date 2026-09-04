import os
from dotenv import load_dotenv
from google import genai

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Create the client
client = genai.Client(api_key=api_key)

# Send a test message
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello and confirm you are working!"
)

# Print the AI's reply
print(response.text)
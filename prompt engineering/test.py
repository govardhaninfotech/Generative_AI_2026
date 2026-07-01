from dotenv import load_dotenv
import os

load_dotenv()

G_API_KEY = os.getenv("GROQ_API_KEY")
print(G_API_KEY)
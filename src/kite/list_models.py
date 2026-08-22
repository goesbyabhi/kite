import os

import httpx
from dotenv import load_dotenv


load_dotenv()

api_key = os.environ["GEMINI_API_KEY"]

response = httpx.get(
    "https://generativelanguage.googleapis.com/v1beta/models",
    params={"key": api_key},
    timeout=30,
)

response.raise_for_status()

for model in response.json()["models"]:
    methods = model.get("supportedGenerationMethods", [])

    if "generateContent" in methods:
        print(model["name"])

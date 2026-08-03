import requests

BASE_URL = "http://127.0.0.1:8000"


def send_message(message):

    response = requests.post(f"{BASE_URL}/chat", json={"message": message})

    return response.json()["answer"]

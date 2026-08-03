import requests

from config import BASE_URL, SESSION_ID, API_KEY


def send_message(message):

    url = f"{BASE_URL}/chat"

    headers = {}

    if API_KEY:
        headers["X-API-Key"] = API_KEY

    data = {"message": message, "session_id": SESSION_ID}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:

        return response.json()["ai_response"]

    return response.text

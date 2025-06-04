import requests
import os
from django.conf import settings
from decouple import config

LINE_API_URL = "https://api.line.me/v2/bot/message/push"
LINE_ACCESS_TOKEN = config("LINE_CHANNEL_ACCESS_TOKEN")

def send_line_message(group_id: str, message: str) -> dict:
    """
    LINE公式アカウントを使ってグループにメッセージを送信する
    """
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": group_id,
        "messages": [
            {"type": "text", "text": message}
        ]
    }

    response = requests.post(LINE_API_URL, headers=headers, json=data)
    return {
        "status_code": response.status_code,
        "response": response.json() if response.content else {},
        "success": response.status_code == 200
    }

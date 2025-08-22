import requests
import os
import json

class Tools():
    def __init__(self):
        with open("tools_function.json") as f:
            self.tools_func = json.load(f)

    def push(self, text):
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "message": text,
            }
        )

    def record_user_details(self, email, name="Name not provided", notes="not provided"):
        self.push(f"Recording {name} with email {email} and notes {notes}")
        return {"recorded": "ok"}

    def record_unknown_question(self, question):
        self.push(f"Recording {question}")
        return {"recorded": "ok"}
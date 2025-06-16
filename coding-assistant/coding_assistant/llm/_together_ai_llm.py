import os
from dotenv import load_dotenv
import requests
from together import Together


load_dotenv()


class TogetherAILLM:
    def __init__(self, model_name):
        self.api_key = os.getenv("TOGETHER_API_KEY")
        self.client = Together(api_key=self.api_key)

        self.model_name = model_name
    
    def get_response(self, data):

        url = "https://api.together.xyz/v1/chat/completions"

        payload = {
            "model": data["model_name"],
            "messages": [
                {"role": "system", "content": data["system_prompt"]},
                {"role": "user", "content": data["user_prompt"]}
            ],
            "context_length_exceeded_behavior": "error",
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)

        try:
            response = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(vars(e))
            print(vars(response))
            exit(123)

        return response

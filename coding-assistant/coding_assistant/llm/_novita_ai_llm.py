import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class NovitaAILLM:
    def __init__(self, model_name: str = "qwen/qwen2.5-7b-instruct") -> None:
        self.api_key = os.getenv("NOVITA_API_KEY")
        self.client = OpenAI(base_url="https://api.novita.ai/v3/openai", api_key=self.api_key)
        self.model_name = model_name
        
    def get_response(self, data):
                
        response = self.client.chat.completions.create(
            model=data["model_name"],
            messages=[
                {"role": "system", "content": data["system_prompt"]},
                {"role": "user", "content": data["user_prompt"]}
            ],
            **data["llm_kwargs"]
        )

        try:
            response = response.choices[0].message.content
        except Exception as e:
            print(vars(e))
            print(response)
            exit(123)

        return response

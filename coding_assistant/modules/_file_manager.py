import os
import json
from dotenv import load_dotenv

from .. import utils
from .. import prompts

load_dotenv()


class FileManager:
    def __init__(self, file_path: str) -> None:
        self.path = file_path
        self.name = os.path.basename(file_path)
        self.ext = os.path.splitext(self.name)[1].lower()
        self.content = utils.read_text_file(self.path)
        self.hash = utils.hash_file_content(self.content)
        self.entities = {}
        self.embeddings = {}

    def get_entities(self, llm_model: object, embedding_model: object) -> None:

        output_format = """
        {
            "global_variables": [
                {
                    "name": "var1",
                    "definition": "var1 = 10",
                    "description": "var1 is equal to integer 10"
                }
            ],
            "functions": [
                {
                    "name": "function1",
                    "body": "def function1(x):\n    return x + 5",
                    "description": "This function adds 5 to the input value."
                }
            ],
            "class_methods": [
                {
                    "name": "ClassA.method1",
                    "body": "class ClassA:\n    def method1(self):\n        return 'Method 1 called'",
                    "description": "This is a class method that returns a string."
                }
            ]
        }
        """
        
        response = llm_model.retrieve_response(
            system_prompt=prompts.extract_info.EXTRACT_INFO_SYSTEM_PROMPT,
            user_prompt=prompts.extract_info.EXTRACT_INFO_USER_PROMPT,
            system_prompt_kwargs={"output_format": output_format},
            user_prompt_kwargs={"file_content": self.content},
            llm_kwargs={}
        )
        
        response = response.replace("```json", "").replace("```", "")

        try:
            response = json.loads(response)["entities"]
        except Exception as e:
            print(vars(e))
            print(response)
            exit(123)

        for n in response:
            n["file_path"] = self.path
            n["embeddings"] = embedding_model.encode(n["description"])

        self.entities = response
        
        
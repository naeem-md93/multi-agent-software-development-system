
from openai import OpenAI

from ._together_ai_llm import TogetherAILLM
from ._novita_ai_llm import NovitaAILLM


class LLM:
    def __init__(self, api_backend, model_name):
        
        if api_backend not in ("together.ai", "novita.ai"):
            raise ValueError(f"Invalid value {api_backend=}")
        
        if api_backend == "together.ai":
            self.client = TogetherAILLM(model_name=model_name)
        elif api_backend == "novita.ai":
            self.client = NovitaAILLM(model_name=model_name)
        
        self.model_name = model_name
        
    def retrieve_response(
        self,
        system_prompt,
        user_prompt,
        system_prompt_kwargs: dict = None,
        user_prompt_kwargs: dict = None,
        llm_kwargs: dict = None
    ):
        if system_prompt_kwargs is not None:
            system_prompt = system_prompt.format(**system_prompt_kwargs)
        
        if user_prompt_kwargs is not None:
            user_prompt = user_prompt.format(**user_prompt_kwargs)
            
        if llm_kwargs is None:
            llm_kwargs = {}
        
        data = {
            "model_name": self.model_name,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "llm_kwargs": llm_kwargs
        }

        result = self.client.get_response(data)

        return result
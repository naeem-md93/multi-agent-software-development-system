import os
import json
import dotenv
import subprocess
import tempfile
import requests
from openai import AzureOpenAI


dotenv.load_dotenv()


def get_novita_response(
    system_prompt: str,
    user_prompt: str,
    system_prompt_kwargs: dict = None,
    user_prompt_kwargs: dict = None,
    llm_kwargs: dict = None
) -> str:

    if system_prompt_kwargs is not None:
        system_prompt = system_prompt.format(**system_prompt_kwargs)

    if user_prompt_kwargs is not None:
        user_prompt = user_prompt.format(**user_prompt_kwargs)

    if llm_kwargs is None:
        llm_kwargs = {}

    headers = {
        "Content-Type": "application/json",
        "Authorization": os.getenv("NOVITA_API_KEY")
    }

    payload = {
        "model": os.getenv("NOVITA_MODEL_NAME"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        **llm_kwargs
    }

    response = requests.request(
        "POST",
        os.getenv("NOVITA_API_URL"),
        json=payload,
        headers=headers
    )

    try:
        response = response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(vars(e))
        print(response)
        exit(500)

    return response


def get_azure_response(
    system_prompt: str,
    user_prompt: str,
    system_prompt_kwargs: dict = None,
    user_prompt_kwargs: dict = None,
    llm_kwargs: dict = None
):
    client = AzureOpenAI(
        api_version=os.getenv("AZURE_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_SUBSCRIPTION_KEY"),
    )

    if system_prompt_kwargs is not None:
        system_prompt = system_prompt.format(**system_prompt_kwargs)

    if user_prompt_kwargs is not None:
        user_prompt = user_prompt.format(**user_prompt_kwargs)

    if llm_kwargs is None:
        llm_kwargs = {}

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=os.getenv("AZURE_DEPLOYMENT"),
        **llm_kwargs
    )

    try:
        response = response.choices[0].message.content
    except Exception as e:
        print(f"{system_prompt=}")
        print(f"{user_prompt=}")
        print(vars(e))
        print(response)
        exit(500)

    return response


def remove_markdown_fences(response: str, fence_type: str) -> str:

    if response.strip().startswith(f"```{fence_type}"):
        response = response.strip().removeprefix(f"```{fence_type}").removesuffix("```")

    return response


def string_to_json(response: str) -> dict:

    try:
        response = json.loads(response)
    except json.JSONDecodeError as e:
        print(response)
        print(vars(e))
        exit(500)

    return response

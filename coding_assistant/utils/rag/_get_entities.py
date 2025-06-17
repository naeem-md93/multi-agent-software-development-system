import json

from ... import prompts


def get_entities(llm_model: object, embedding_model: object, content: str) -> None:


    response = llm_model.retrieve_response(
        system_prompt=prompts.extract_info.EXTRACT_INFO_SYSTEM_PROMPT,
        user_prompt=prompts.extract_info.EXTRACT_INFO_USER_PROMPT,
        user_prompt_kwargs={"file_content": content},
    )

    print(response)

    try:
        response = response.replace("```json", "").replace("```", "")
        response = json.loads(response)["entities"]
    except Exception as e:
        print(vars(e))
        print(response)
        exit(123)

    for n in response:
        n["embeddings"] = embedding_model.encode(n["description"])

    return response

from ... import prompts


def respond_user(llm: object, user_input: str, project_summary: str, relevant_data: list[dict]) -> str:

    text = "==========\n"
    for d in relevant_data:
        text += f"Entity Path: {d['file_path']}\n"
        text += f"Entity Name: {d['name']}\n"
        text += f"Entity Type: {d['type']}\n"
        text += f"Entity Definition: \n{d['definition']}\n"
        text = "==========\n"

    response = llm.retrieve_response(
        system_prompt=prompts.respond_user.RESPOND_USER_SYSTEM_PROMPT,
        user_prompt=prompts.respond_user.RESPOND_USER_USER_PROMPT,
        user_prompt_kwargs={
            "user_request": user_input,
            "project_summary": project_summary,
            "relevant_data": text
        }
    )

    return response
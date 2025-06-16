from ... import prompts

def get_project_description(llm: object, data: list[dict]) -> str:

    text = ""
    for d in data:
        text += "==========\n"
        text += f"File Path: {d['path']}\n"
        text += f"Last Modified: {d['last_modified']}\n"
        for n in d["entities"]:
            text += "----------\n"
            text += f" - Entity Name: {n['name']}\n"
            text += f" - Entity Type: {n['type']}\n"
            text += f" - Entity Description: {n['description']}\n"

    response = llm.retrieve_response(
        system_prompt=prompts.project_readme.PROJECT_README_SYSTEM_PROMPT,
        user_prompt=prompts.project_readme.PROJECT_README_USER_PROMPT,
        user_prompt_kwargs={"project_data": text}
    )

    return response

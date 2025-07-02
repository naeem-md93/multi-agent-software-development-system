import json
import copy

from ..state import ProjectState
from .. import constants as C


def planning_agent(state: ProjectState) -> ProjectState:
    
    prd = state["analyzer"]["prd"]

    prompt_template = f"""
    You are a planning agent in a multi-agent software development system. You must split a Product Requirements Document (PRD) into implementable AI‐agent tasks.  

    !!!RESPOND WITH VALID JSON ONLY!!!

    YOUR RESPANSE JSON SCHEMA:
    {{
        "reasoning": "<your chain of thought>",
        "tasks": [
            {{
                "id": 1,
                "title": "<task title>",
                "description": "<why this matters>"
            }}
            /* more task objects, no trailing commas */
        ]
    }}

    Constraints:
        - Do NOT output any text outside of the JSON.
        - Do NOT wrap your answer in markdown or triple back‐ticks.
        - There is NO leading or trailing whitespace.
        - A virtualenv already exists. Don’t create one.
        - You’re already in the project root. Don’t change directories.
        - Don’t use any Git commands.

    Product Requirements Document:
    {prd}

    Your Response:
    """

    a_resp = C.LLM.invoke(prompt_template)
    print("==================")
    print(a_resp)
    print("==================")

    a_resp = a_resp.content.replace("```json", "").replace("```", "")
    a_resp = json.loads(a_resp)
    print("===============")
    print(json.dumps(a_resp))
    print("===============")

    result = copy.deepcopy(state)
    result["planner"] = a_resp

    return result

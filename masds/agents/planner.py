PROMPT = """
You are an experienced Software Engineer in a Multi-Agent Software Development System.
Your job is to split a Product Requirements Document (PRD) into a sequential list of implementable AI‐agent tasks.  

!!!RESPOND WITH VALID JSON ONLY!!!

YOUR RESPONSE JSON SCHEMA:
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


from typing_extensions import TypedDict, List, Dict
import copy

from .. import constants as C, utils


class PlannerState(TypedDict):
    reasoning: str
    tasks: List[Dict[str, str | int]]


def planning_agent(state):

    prompt = copy.deepcopy(PROMPT)
    prompt = prompt.format(prd=state["analyzer"]["prd"])

    a_resp = C.LLM.invoke(prompt)
    a_resp = utils.convert_response_to_json(a_resp)

    result = copy.deepcopy(state)
    result["planner"] = copy.deepcopy(a_resp)

    return result

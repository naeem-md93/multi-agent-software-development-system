import json
import copy
from typing import List, Annotated
from typing_extensions import TypedDict

from .. import constants as C
from ..state import ProjectState


def analysis_agent(state: ProjectState) -> ProjectState:
    messages = []
    is_clear = False
    description = state["description"]

    while not is_clear:
        prompt = f"""
        You are an expert Software Developer.
        Your job is to read a project description and a list of previous conversations. you should read the project description carefully and write a Product Requirement Document (PRD) if the project descrition in clear. Otherwise, you should ask follow-up questions from the user. your response should be exactly in this JSON format:
        {{
            "reasoning": "<your internal reasoning and chain of thoughts>",
                "is_clear": "<boolean (true or false). whether the project descrition is clear for writing a PRD or not>",
                "prd": "<PRD text if the project description is clear for writing a PRD. otherwise, leave it blank.>",
                "questions": [ // list of questions
                    "question 1",
                    "question 2",
                    ...
                ] "<follow-up questions if the project description is not clear for writing a PRD. otherwise, leave it blank.>"
            }}

        Project Description:
        {description}

        Previous Messages:
        {messages}
        """

        a_resp = C.LLM.invoke(prompt)
        a_resp = a_resp.content.replace("```json", "").replace("```", "")
        a_resp = json.loads(a_resp)
        a_resp["is_clear"] = a_resp["is_clear"] in (True, "True", "true")
        
        messages.append({
            "type": "assistant",
            "questions": a_resp["questions"]
        })


        is_clear = a_resp["is_clear"]

        if not is_clear:
            u_resp = input(a_resp["questions"])
            messages.append({
                "type": "user",
                "answers": u_resp
            })

    result = copy.deepcopy(state)
    result["analyzer"] = {
        "reasoning": a_resp["reasoning"],
        "messages": messages,
        "prd": a_resp["prd"],
        "is_clear": a_resp["is_clear"]
    }

    return result

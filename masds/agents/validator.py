PROMPT = """
You are an expert JSON fixer specialized in converting malformed JSON strings into valid JSON without altering the original content beyond what’s necessary to correct syntax errors.

When provided with a raw JSON string and the associated decoding error details, your task is to:

1. Identify and fix only the syntax issues that caused the parsing error.
2. Preserve all original data and structure; do not add, remove, or modify any keys or values beyond syntax corrections.
3. Explain your reasoning and chain-of-thought in an internal "reasoning" field.
4. Return the corrected JSON string in a "implementation" field.

Respond strictly in this JSON format:
{{
  "reasoning": "<detailed internal reasoning and steps you took>",
  "implementation": "<the corrected JSON string>"
}}

Inputs:
- json_string: The original, malformed JSON string.
- json_error: The exact error message you received when attempting to parse json_string.


JSON String:
{json_string}

ERROR:
{json_error}

Your Response:
"""


import json
from json.decoder import JSONDecodeError

from .. import constants as C


def validate_json_response(resp: str) -> str:
    resp = resp.replace("```json", "").replace("```", "")
    
    print("================================")
    print(resp)
    print("================================")

    try:
        result = json.loads(resp)
        return result

    except JSONDecodeError as e:
        print("####################################")
        print(vars(e))
        print("####################################")

        resp = C.LLM.invoke(PROMPT.format(
            json_string=resp,
            json_error=str(vars(e))
        ))
        return validate_json_response(resp.content)


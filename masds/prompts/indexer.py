SYSTEM_PROMPT = """
You are CodeInsight, an AI assistant specialized in analyzing source files.  
When given the contents of a file, you must produce **only** a JSON object with two fields:

1. "reasoning": A transparent, step‑by‑step chain of thought describing how you arrived at your analysis (for logging purposes only—this will not be shown to end users).  
2. "explanation": A clear, less than 100 words, concise summary of the file’s contents, listing each global variable, function, and class defined in the file and describing its purpose.

Your JSON output must be valid (no extra text, no Markdown, no comments), and must follow this exact schema:

```json
{
  "reasoning": "<your internal reasoning here>",
  "explanation": "<your high‑level explanation here>"
}

Do not output anything else.
"""

USER_PROMPT = """
# START OF THE FILE CONTENTS
File Content:
{contents}
# END OF THE FILE CONTENTS

Please analyze this file and return a JSON object following the schema specified in the system prompt.
"""

import json
from .. import utils


def get_llm_response(
    system_prompt_kwargs: dict = None,
    user_prompt_kwargs: dict = None,
    llm_kwargs: dict = None,
):
    response = utils.rag_utils.get_azure_response(
        system_prompt=SYSTEM_PROMPT,
        system_prompt_kwargs=system_prompt_kwargs,
        user_prompt=USER_PROMPT,
        user_prompt_kwargs=user_prompt_kwargs,
        llm_kwargs=llm_kwargs,
    )

    response = utils.rag_utils.remove_markdown_fences(response, "json")
    response = utils.rag_utils.string_to_json(response)

    print("indexer response =========================")
    print(json.dumps(response, indent=2))
    print("==========================================")

    return response["explanation"]

SYSTEM_PROMPT = """
You are DevAgent-Bot, an AI agent acting as a Software Developer / Engineer in a multi-agent development system.

Your inputs are:
  • task_title: a short, descriptive title of the task  
  • task_explanation: a detailed description of what the task entails  
  • instructions: the Tech Lead’s step-by-step implementation plan  
  • guidelines: coding conventions and best practices to follow  
  • required_files: an array of objects, each with:
      – file_path: the path to an existing file  
      – file_contents: the current contents of that file  

Your responsibilities:

1. **Internal reasoning**  
   - Read all inputs and record your thought process in a top-level `"reasoning"` field (for logging only).

2. **Produce implementation output**  
   - Output **only** valid JSON matching exactly this schema (no extra keys or prose):

     ```json
     {
       "reasoning": "<your internal chain-of-thought>",
       "developer": {
         "implementation": "<bash script that creates, modifies, or deletes files>"
       }
     }
     ```

3. **Script formatting requirements**  
   - The value of `"implementation"` must be a **single JSON string** containing the raw bash script, with **actual** line breaks (not literal `\n` sequences).  
   - The script **must** begin on the very first line with the shebang:
     ```bash
     #!/bin/bash
     ```
   - Here-document delimiters (`<<EOL`) and their terminators (`EOL`) must each appear **alone on their own lines**, with no leading whitespace.  
   - **Do not** embed escaped newlines (`\n`) or tabs (`\t`); write out the script exactly as it should appear in the `.sh` file.  
   - Use only valid JSON string escapes for any embedded quotes or backslashes: `\"`, `\\`, `\/`, `\b`, `\f`, `\r`, `\t`, `\\uXXXX`.

4. **Validation**  
   - After composing, internally “lint” your JSON by parsing it with a JSON parser.  
   - Confirm that when the `"implementation"` string is written directly to a `.sh` file, it executes correctly without syntax errors.  
   - Fix any escaping or structural issues before returning your response.
"""

USER_PROMPT = """
task_title: {task_title}

task_explanation:
{task_explanation}

instructions:
{instructions}

guidelines:
{guidelines}

required_files:
{required_files}

Please generate your JSON response following the schema defined in the system prompt.
"""

import json
from .. import utils


def implement_a_task(database: dict, task: dict):

    text = "----------\n"
    for i, x in enumerate(task["developer_required_files"]):
        d_type = "File" if database[x]["type"] == "file" else "Directory"
        text += f"{d_type} {i + 1} Path: {x}\n"
        text += f"{d_type} {i + 1} Contents:\n{database[x]['contents']}\n"
        text += "----------\n"
    print(text)

    response = utils.rag_utils.get_azure_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT,
        system_prompt_kwargs=None,
        user_prompt_kwargs={
            "task_title": task["task_title"],
            "task_explanation": task["task_explanation"],
            "instructions": task["developer_instructions"],
            "guidelines": task["developer_guidelines"],
            "required_files": text

        },
        llm_kwargs={"temperature": 0.5}
    )

    response = utils.rag_utils.remove_markdown_fences(response, "json")
    response = utils.rag_utils.string_to_json(response)

    print("developer implementation ==========================")
    print(json.dumps(response, indent=2))
    print("====================================")

    current_task = {
        "task_id": task["task_id"],
        "task_title": task["task_title"],
        "task_explanation": task["task_explanation"],
        "task_status": task["task_status"],

        "developer_instructions": task["developer_instructions"],
        "developer_guidelines": task["developer_guidelines"],
        "developer_required_files": task["developer_required_files"],
        "developer_implementation": response["developer"]["implementation"],

        "tester_instructions": task["tester_instructions"],
        "tester_guidelines": task["tester_guidelines"],
        "tester_required_files": task["tester_required_files"],

    }
    return current_task


def execute_developer_codes(task: dict) -> dict:

    reports = {
        "implementation": utils.os_utils.run_script(task["developer_implementation"], 30)
    }

    print("developer implementation reports ==========================")
    print(json.dumps(reports, indent=2))
    print("====================================")

    current_task = {
        "task_id": task["task_id"],
        "task_title": task["task_title"],
        "task_explanation": task["task_explanation"],
        "task_status": task["task_status"],

        "developer_instructions": task["developer_instructions"],
        "developer_guidelines": task["developer_guidelines"],
        "developer_required_files": task["developer_required_files"],
        "developer_implementation": task["developer_implementation"],

        "developer_implementation_stdout_report": reports["implementation"]["stdout"],
        "developer_implementation_stderr_report": reports["implementation"]["stderr"],
        "developer_implementation_error_type_report": reports["implementation"]["error_type"],

        "tester_instructions": task["tester_instructions"],
        "tester_guidelines": task["tester_guidelines"],
        "tester_required_files": task["tester_required_files"],
    }

    return current_task
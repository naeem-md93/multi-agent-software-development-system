SYSTEM_PROMPT = """
You are an AI agent in the role of a Software Developer / Software Engineer.  
Your inputs are provided as follows:  
  • task_title: a short title of the task to implement  
  • task_explanation: a detailed description of what the task entails  
  • instructions: the Tech Lead’s step‑by‑step instructions for implementation  
  • guidelines: the Tech Lead’s coding conventions and best practices to follow  
  • required_files: a list of objects, each with:  
      – file_path: the path to an existing file  
      – file_contents: the current contents of that file  

Your job is to:  
1. Read and reason over all inputs. Document your internal chain of thought in a `"reasoning"` field (for logging only).  
2. Produce **only** the implementation steps—file creation/modification/deletion—wrapped in a bash script under the `"implementation"` key.  
3. Produce a separate bash script under the `"execution"` key that, when run, executes the newly implemented functionality (e.g., runs the entry‑point or main function).  
4. **Begin both bash scripts with a proper shebang on the first line** (`#!/bin/bash`).  
5. After those scripts, provide a `"file_changes"` list of objects, each with:  
   - `path`: the path of the file that will be created, modified, or deleted  
   - `change_type`: one of `"created"`, `"modified"`, or `"deleted"`  
   - `explanation`: why and how the file is being changed  

Always output **only** valid JSON in the exact following schema (no extra keys, no comments outside JSON):  
```json
{
  "reasoning": "<your internal reasoning here>",
  "developer": {
    "implementation": "<bash script that creates and modifies files>",
    "execution": "<bash script that runs the implemented functionality>",
    "file_changes": [
      {
        "path": "<path/to/file.ext>",
        "change_type": "created|modified|deleted",
        "explanation": "<why this file is created/modified/deleted>"
      }
      // …additional file changes
    ]
  }
}

Whenever you output JSON, you must:
1. Only use valid JSON string‑escapes: \" \\ / \b \f \n \r \t \\uXXXX.
2. Never emit \ followed by any other character (e.g. \$ is invalid).
3. After generating the JSON, perform an internal “lint”:
    - Parse it with a JSON parser.
    - If the parser errors, fix your escaping before returning.

4. Always wrap scripts or multi‑line text in a JSON string using one of:
    a) A here‑doc inside the JSON (e.g. an array of lines), or
    b) Double‑escaped newlines (\\n) and backslashes (\\\\).
"""


USER_PROMPT = """
task_title: {task_title}
task_explanation: {task_explanation}
instructions: {instructions}

guidelines: {guidelines}

required_files:
{required_files}

Please generate your JSON response following the schema defined in the system prompt.
"""

import json
from .. import utils


def implement_a_task(database: dict, task: dict):

    required_files = "\n==========\n"
    for x in task["developer_required_files"]:
        required_files += f"File Path: {x}\n"
        required_files += f"File Contents:\n{database[x]}\n"
        required_files += "--------------\n"
    required_files += "=============\n"

    response = utils.rag_utils.get_azure_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT,
        system_prompt_kwargs=None,
        user_prompt_kwargs={
            "task_title": task["task_title"],
            "task_explanation": task["task_explanation"],
            "instructions": task["developer_instructions"],
            "guidelines": task["developer_guidelines"],
            "required_files": required_files

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
        "branch_name": task["branch_name"],
        "developer_instructions": task["developer_instructions"],
        "developer_guidelines": task["developer_guidelines"],
        "developer_required_files": task["developer_required_files"],
        "developer_implementation": response["developer"]["implementation"],
        "developer_execution": response["developer"]["execution"],
        "developer_file_changes": response["developer"]["file_changes"],
        "tester_instructions": task["tester_instructions"],
        "tester_guidelines": task["tester_guidelines"],
        "tester_required_files": task["tester_required_files"],

    }
    return current_task


def execute_developer_codes(task: dict) -> dict:

    reports = utils.os_utils.execute_scripts(task["developer_implementation"], task["developer_execution"])

    print("developer implementation reports ==========================")
    print(json.dumps(reports, indent=2))
    print("====================================")

    current_task = {
        "task_id": task["task_id"],
        "task_title": task["task_title"],
        "task_explanation": task["task_explanation"],
        "task_status": task["task_status"],

        "branch_name": task["branch_name"],

        "developer_instructions": task["developer_instructions"],
        "developer_guidelines": task["developer_guidelines"],
        "developer_required_files": task["developer_required_files"],
        "developer_implementation": task["developer_implementation"],
        "developer_execution": task["developer_execution"],
        "developer_file_changes": task["developer_file_changes"],

        "developer_implementation_stdout_report": reports["implementation"]["stdout"],
        "developer_implementation_stderr_report": reports["implementation"]["stderr"],
        "developer_implementation_error_type_report": reports["implementation"]["error_type"],

        "developer_execution_stdout_report": reports["execution"]["stdout"],
        "developer_execution_stderr_report": reports["execution"]["stderr"],
        "developer_execution_error_type_report": reports["execution"]["error_type"],

        "tester_instructions": task["tester_instructions"],
        "tester_guidelines": task["tester_guidelines"],
        "tester_required_files": task["tester_required_files"],
    }

    return current_task
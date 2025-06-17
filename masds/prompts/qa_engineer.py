SYSTEM_PROMPT = """
You are an AI agent in the role of a QA Engineer / Test Engineer.  
Your inputs are provided as follows:  
  • task_title: a short title of the task under test  
  • task_explanation: a detailed description of what the task implements  
  • instructions: the Tech Lead’s step‑by‑step testing instructions  
  • guidelines: the Tech Lead’s testing conventions and best practices to follow  
  • developer_implementation: the bash script string that the Developer Agent produced to implement the task  
  • required_files: a list of objects, each with:  
      – file_path: the path to an existing file or resource  
      – file_contents: the current contents of that file  

Your job is to:  
1. Read and reason over all inputs. Document your internal chain of thought in a `"reasoning"` field (for logging only).  
2. Produce **only** the test implementation—creating/modifying/deleting test files—wrapped in a bash script under the `"implementation"` key.  
3. Produce a separate bash script under the `"execution"` key that, when run, executes the test suite (e.g., via `pytest`, `npm test`, or another runner).  
4. **Start each generated bash script with the line `#!/bin/bash`** so that it will execute correctly.  
5. After those scripts, provide a `"file_changes"` list of objects, each with:  
   - `path`: the path of the test file to be created, modified, or deleted  
   - `change_type`: one of `"created"`, `"modified"`, or `"deleted"`  
   - `explanation`: why and how the test file is being changed  

Always output **only** valid JSON in the exact following schema (no extra keys, no comments outside JSON):  
```json
{
  "reasoning": "<your internal reasoning here>",
  "tester": {
    "implementation": "<bash script that creates/modifies test files>",
    "execution": "<bash script that runs the test suite>",
    "file_changes": [
      {
        "path": "<path/to/test_file.ext>",
        "change_type": "created|modified|deleted",
        "explanation": "<why this test file is created/modified/deleted>"
      }
      // …additional file changes
    ]
  }
}

Whenever you output JSON, you must:
1. Only use valid JSON string‑escapes: \" \\ / \b \f \n \r \t \\uXXXX.
2. Never emit \ followed by any other character (e.g. \$ is invalid).
3. After generating the JSON, perform an internal “lint”:
  • Parse it with a JSON parser.
  • If the parser errors, fix your escaping before returning.
4. Always wrap scripts or multi‑line text in a JSON string using one of:
    a) A here‑doc inside the JSON (e.g. an array of lines), or
    b) Double‑escaped newlines (\\n) and backslashes (\\\\).
"""

USER_PROMPT = """
Task Title: {task_title}

Task Explanation: {task_explanation}

Testing Instructions: {instructions}

Testing Guidelines: {guidelines}

Developer Implementation:
{developer_implementation}

Required Files:
{required_files}

Please generate your JSON response following the schema defined in the system prompt.
"""


import json
from .. import utils


def implement_a_test(database: dict, task: dict):

    required_files = "\n==========\n"
    for x in task["tester_required_files"]:
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
            "instructions": task["tester_instructions"],
            "guidelines": task["tester_guidelines"],
            "developer_implementation": task["developer_implementation"],
            "required_files": required_files
        },
        llm_kwargs={"temperature": 0.5}
    )

    response = utils.rag_utils.remove_markdown_fences(response, "json")
    response = utils.rag_utils.string_to_json(response)

    print("tester implementation ==========================")
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
        "developer_implementation": task["developer_implementation"],
        "developer_execution": task["developer_execution"],
        "developer_file_changes": task["developer_file_changes"],

        "developer_implementation_stdout_report": task["developer_implementation_stdout_report"],
        "developer_implementation_stderr_report": task["developer_implementation_stderr_report"],
        "developer_implementation_error_type_report": task["developer_implementation_error_type_report"],
        "developer_execution_stdout_report": task["developer_execution_stdout_report"],
        "developer_execution_stderr_report": task["developer_execution_stderr_report"],
        "developer_execution_error_type_report": task["developer_execution_error_type_report"],

        "tester_instructions": task["tester_instructions"],
        "tester_guidelines": task["tester_guidelines"],
        "tester_required_files": task["tester_required_files"],
        "tester_implementation": response["tester"]["implementation"],
        "tester_execution": response["tester"]["execution"],
        "tester_file_changes": response["tester"]["file_changes"],

    }
    return current_task


def execute_tester_codes(task):
    reports = utils.os_utils.execute_scripts(task["tester_implementation"], task["tester_execution"])

    print("tester implementation reports ==========================")
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

        "developer_implementation_stdout_report": task["developer_implementation_stdout_report"],
        "developer_implementation_stderr_report": task["developer_implementation_stderr_report"],
        "developer_implementation_error_type_report": task["developer_implementation_error_type_report"],
        "developer_execution_stdout_report": task["developer_execution_stdout_report"],
        "developer_execution_stderr_report": task["developer_execution_stderr_report"],
        "developer_execution_error_type_report": task["developer_execution_error_type_report"],

        "tester_instructions": task["tester_instructions"],
        "tester_guidelines": task["tester_guidelines"],
        "tester_required_files": task["tester_required_files"],
        "tester_implementation": task["tester_implementation"],
        "tester_execution": task["tester_execution"],
        "tester_file_changes": task["tester_file_changes"],

        "tester_implementation_stdout_report": reports["implementation"]["stdout"],
        "tester_implementation_stderr_report": reports["implementation"]["stderr"],
        "tester_implementation_error_type_report": reports["implementation"]["error_type"],
        "tester_execution_stdout_report": reports["execution"]["stdout"],
        "tester_execution_stderr_report": reports["execution"]["stderr"],
        "tester_execution_error_type_report": reports["execution"]["error_type"],
    }

    return current_task

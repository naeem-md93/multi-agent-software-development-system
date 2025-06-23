SYSTEM_PROMPT = """
You are TestAgent‑Bot, an AI agent in the role of QA Engineer / Test Engineer in a multi‑agent development system.

Your inputs are:
  • task_title: the task’s short title  
  • task_explanation: what the task is supposed to implement  
  • instructions: the Tech Lead’s step‑by‑step testing plan  
  • guidelines: the Tech Lead’s testing best practices  
  • developer_implementation: the bash script the Developer Agent produced  
  • required_files: an array of objects, each with:
      – file_path: path to an existing file  
      – file_contents: current contents of that file  

Your jobs:

1. **Internal reasoning**  
   - Analyze all inputs and record your thought process in a top‑level `"reasoning"` field (for logging only).

2. **Test implementation script**  
   - Under `"implementation"`, output a bash script that creates or updates test files to verify the developer’s work according to the testing plan.  
   - Begin with `#!/bin/bash` on the first line.

3. **Test execution script**  
   - Under `"execution"`, output a bash script that runs the complete test suite (e.g., `pytest`, `npm test`, etc.).  
   - Also begin with `#!/bin/bash`.

4. **Output format**  
   - **Only** valid JSON, following exactly this schema:
     ```json
     {
       "reasoning": "<internal reasoning>",
       "tester": {
         "implementation": "<bash script>",
         "execution": "<bash script>",
       }
     }
     ```
    - Internally lint your JSON before returning.  
    - Wrap multi‑line scripts with properly escaped newlines (`\\n`) or a here‑doc style if supported.
"""

USER_PROMPT = """
Task Title: {task_title}

Task Explanation:
{task_explanation}

Testing Instructions:
{instructions}

Testing Guidelines:
{guidelines}

Required Files:
{required_files}

Developer Implementation:
{developer_implementation}

Please generate your JSON response following the schema defined in the system prompt.
"""


import json
from .. import utils


def implement_a_test(database: dict, task: dict):

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
            "instructions": task["tester_instructions"],
            "guidelines": task["tester_guidelines"],
            "developer_implementation": task["developer_implementation"],
            "required_files": text
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

        "developer_instructions": task["developer_instructions"],
        "developer_guidelines": task["developer_guidelines"],
        "developer_required_files": task["developer_required_files"],
        "developer_implementation": task["developer_implementation"],

        "developer_implementation_stdout_report": task["developer_implementation_stdout_report"],
        "developer_implementation_stderr_report": task["developer_implementation_stderr_report"],
        "developer_implementation_error_type_report": task["developer_implementation_error_type_report"],

        "tester_instructions": task["tester_instructions"],
        "tester_guidelines": task["tester_guidelines"],
        "tester_required_files": task["tester_required_files"],
        "tester_implementation": response["tester"]["implementation"],
        "tester_execution": response["tester"]["execution"],
    }

    return current_task


def execute_tester_codes(task):
    reports = {
        "implementation": utils.os_utils.run_script(task["tester_implementation"], 30),
        "execution": utils.os_utils.run_script(task["tester_execution"], 30),

    }

    print("tester implementation reports ==========================")
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

        "developer_implementation_stdout_report": task["developer_implementation_stdout_report"],
        "developer_implementation_stderr_report": task["developer_implementation_stderr_report"],
        "developer_implementation_error_type_report": task["developer_implementation_error_type_report"],

        "tester_instructions": task["tester_instructions"],
        "tester_guidelines": task["tester_guidelines"],
        "tester_required_files": task["tester_required_files"],
        "tester_implementation": task["tester_implementation"],
        "tester_execution": task["tester_execution"],

        "tester_implementation_stdout_report": reports["implementation"]["stdout"],
        "tester_implementation_stderr_report": reports["implementation"]["stderr"],
        "tester_implementation_error_type_report": reports["implementation"]["error_type"],
        "tester_execution_stdout_report": reports["execution"]["stdout"],
        "tester_execution_stderr_report": reports["execution"]["stderr"],
        "tester_execution_error_type_report": reports["execution"]["error_type"],
    }

    return current_task

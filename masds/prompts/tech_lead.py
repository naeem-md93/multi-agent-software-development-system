ASSIGNMENT_SYSTEM_PROMPT = """
You are an AI Task Dispatcher playing the role of a Tech Lead / Engineering Manager in a multi‑agent development system.  
Your responsibility is to take as input:  
  1. An array of file change history objects (possibly empty) that record which files have been created, modified, or deleted so far and why.  
  2. A single task’s explanation (derived from the Product Owner’s breakdown).  

As the Tech Lead, you must:  
  • Review the file change history to identify and surface relevant code artifacts for this task.  
  • Assign clear, actionable, and prioritized instructions to two agents—a Developer Agent and a Tester Agent—each wrapped in executable bash scripts that create or modify files and insert the necessary code or tests.  
  • Specify for each agent which existing files they need (with file paths) and explain why those files are required.  
  • Enforce coding and testing best practices through explicit guidelines for each agent.  
  • Suggest a concise, descriptive git branch name that reflects the task’s scope.  
  • Capture your internal decision‑making process in the `"reasoning"` field, detailing how you selected files, structured the workflow, and derived the branch name.  

Always output **only** valid JSON in the exact structure below (no additional keys, no comments, no prose outside the JSON):  
```json
{
  "reasoning": "<internal chain‑of‑thought here>",
  "task": {
    "task_title": "<input task title>",
    "task_explanation": "<input task explanation>",
    "branch_name": "<suggested git branch name>",
    "developer_instructions": "<bash‑wrapped implementation steps>",
    "developer_guidelines": "<coding conventions and best practices>",
    "developer_required_files": [
      "<path/to/relevant/file1>",
      "<path/to/relevant/file2>"
    ],
    "tester_instructions": "<bash‑wrapped testing steps>",
    "tester_guidelines": "<testing conventions and best practices>",
    "tester_required_files": [
      "<path/to/relevant/fileA>",
      "<path/to/relevant/fileB>"
    ]
  }
}
"""

ASSIGNMENT_USER_PROMPT = """
File Changes History:
<START OF FILE CHANGES HISTORY>
{file_changes_history}
<END OF FILE CHANGES HISTORY>

Task Explanation:
{task_explanation}

Please produce the JSON response following the schema defined in the system prompt.
"""


REVIEW_SYSTEM_PROMPT = """
You are an AI agent in the role of a QA Lead / Technical Lead.  
Your responsibility is to review the outputs and reports from both the Developer Agent and the Tester Agent for a given task, decide if the task is complete, and—if not—provide updated instructions and guidelines for further work.  

Your inputs are provided as follows:  
  • task_explanation: the detailed description of the task  
  
  • developer_instructions: the original instructions given to the Developer Agent  
  • developer_guidelines: the original coding guidelines given to the Developer Agent  
  • developer_implementation: the bash script the Developer Agent produced  
  • developer_reports:  
      – stdout_implementation: stdout from running the implementation script  
      – stderr_implementation: stderr from running the implementation script  
      – error_type_implementation: the error type (e.g. timeout, execution_error, or null)  
      – stdout_execution: stdout from running the execution script  
      – stderr_execution: stderr from running the execution script  
      – error_type_execution: the error type for execution  
      
  • tester_instructions: the original instructions given to the Tester Agent  
  • tester_guidelines: the original testing guidelines given to the Tester Agent  
  • tester_implementation: the bash script the Tester Agent produced  
  • tester_reports:  
      – stdout_test_impl: stdout from running the test‑implementation script  
      – stderr_test_impl: stderr from running the test‑implementation script  
      – error_type_test_impl: the error type for the test‑implementation  
      – stdout_test_exec: stdout from running the test‑execution script  
      – stderr_test_exec: stderr from running the test‑execution script  
      – error_type_test_exec: the error type for the test‑execution  

Your job is to:  
1. Analyze all inputs, comparing actual outputs and errors against the original instructions and guidelines.  
2. Decide whether the task is **done** (both implementation and tests passed and met guidelines) or **in-progress** (anything failed or deviated).  
3. In a top‑level `"reasoning"` field, log your internal chain‑of‑thought: what passed, what failed, and why you reached your decision.  
4. Under `"task"`, set `"task_status"` to `"done"` or `"in-progress"`.  
5. If `"in-progress"`, supply updated `"developer_instructions"` and `"developer_guidelines"` and/or updated `"tester_instructions"` and `"tester_guidelines"` to correct any issues.  
6. If `"done"`, you may leave the new instruction/guideline fields empty strings ("").
7. If `"done"`, you should write a git commit message in the `"commit_message"` field explaining the task and file changes, otherwise, write an empty string ("").

Always output **only** valid JSON in this exact schema (no extra keys, no comments outside JSON):  
```json
{
  "reasoning": "<your internal reasoning here>",
  "task": {
    "task_status": "done|in-progress",
    "developer_instructions": "<new or repeated instructions for the developer>",
    "developer_guidelines": "<new or repeated guidelines for the developer>",
    "tester_instructions": "<new or repeated instructions for the tester>",
    "tester_guidelines": "<new or repeated guidelines for the tester>",
    "commit_message": "<a commit message explaining the task and file changes or empty>"
  }
}

Whenever you output JSON, you must:
1. Only use valid JSON string‑escapes: \" \\ / \b \f \n \r \t \\uXXXX.
2. Never emit `\` followed by any other character (e.g. `\$` is invalid).
3. After generating the JSON, perform an internal “lint”:
   - Parse it with a JSON parser.
   - If the parser errors, fix your escaping before returning.
4. Always wrap scripts or multi‑line text in a JSON string using one of:
   a) A `here-doc` inside the JSON (e.g. an array of lines), or  
   b) Double‑escaped newlines (`\\n`) and backslashes (`\\\\`).
"""


REVIEW_USER_PROMPT = """

task_explanation: {task_explanation}

developer_instructions: {developer_instructions}

developer_guidelines: {developer_guidelines}

developer_implementation:
{developer_implementation}

developer_reports:
  - stdout_implementation: {stdout_implementation}
  - stderr_implementation: {stderr_implementation}
  - error_type_implementation: {error_type_implementation}
  - stdout_execution: {stdout_execution}
  - stderr_execution: {stderr_execution}
  - error_type_execution: {error_type_execution}

tester_instructions: {tester_instructions}

tester_guidelines: {tester_guidelines}

tester_implementation:
{tester_implementation}

tester_reports:
  - stdout_test_impl: {stdout_test_impl}
  - stderr_test_impl: {stderr_test_impl}
  - error_type_test_impl: {error_type_test_impl}
  - stdout_test_exec: {stdout_test_exec}
  - stderr_test_exec: {stderr_test_exec}
  - error_type_test_exec: {error_type_test_exec}

Please generate your JSON response following the schema defined in the system prompt.
"""

import json
from .. import utils


def assign_a_task(changes_history: list[dict], task: dict):

    response = utils.rag_utils.get_azure_response(
        system_prompt=ASSIGNMENT_SYSTEM_PROMPT,
        user_prompt=ASSIGNMENT_USER_PROMPT,
        system_prompt_kwargs=None,
        user_prompt_kwargs={
            "file_changes_history": changes_history,
            "task_explanation": task["task_explanation"]
        },
        llm_kwargs={"temperature": 0.5}
    )
    response = utils.rag_utils.remove_markdown_fences(response, "json")
    current_task = utils.rag_utils.string_to_json(response)

    print("assign_a_task ==========================")
    print(json.dumps(current_task, indent=2))
    print("====================================")

    current_task = {
        "task_id": task["task_id"],
        "task_title": task["task_title"],
        "task_explanation": task["task_explanation"],
        "task_status": "in-progress",

        "branch_name": current_task["task"]["branch_name"],

        "developer_instructions": current_task["task"]["developer_instructions"],
        "developer_guidelines": current_task["task"]["developer_guidelines"],
        "developer_required_files": current_task["task"]["developer_required_files"],

        "tester_instructions": current_task["task"]["tester_instructions"],
        "tester_guidelines": current_task["task"]["tester_guidelines"],
        "tester_required_files": current_task["task"]["tester_required_files"],
    }

    return current_task



def review_a_task(task):

    response = utils.rag_utils.get_azure_response(
        system_prompt=REVIEW_SYSTEM_PROMPT,
        user_prompt=REVIEW_USER_PROMPT,
        system_prompt_kwargs=None,
        user_prompt_kwargs={
            "task_explanation": task["task_explanation"],

            "developer_instructions": task["developer_instructions"],
            "developer_guidelines": task["developer_guidelines"],
            "developer_implementation": task["developer_implementation"],

            "stdout_implementation": task["developer_implementation_stdout_report"],
            "stderr_implementation": task["developer_implementation_stderr_report"],
            "error_type_implementation": task["developer_implementation_error_type_report"],

            "stdout_execution": task["developer_execution_stdout_report"],
            "stderr_execution": task["developer_execution_stderr_report"],
            "error_type_execution": task["developer_execution_error_type_report"],

            "tester_instructions": task["tester_instructions"],
            "tester_guidelines": task["tester_guidelines"],
            "tester_implementation": task["tester_implementation"],

            "stdout_test_impl": task["tester_implementation_stdout_report"],
            "stderr_test_impl": task["tester_implementation_stderr_report"],
            "error_type_test_impl": task["tester_implementation_error_type_report"],
            "stdout_test_exec": task["tester_execution_stdout_report"],
            "stderr_test_exec": task["tester_execution_stderr_report"],
            "error_type_test_exec": task["tester_execution_error_type_report"],
        },
        llm_kwargs={"temperature": 0.5}
    )

    response = utils.rag_utils.remove_markdown_fences(response, "json")
    response = utils.rag_utils.string_to_json(response)

    print("review_a_task ==========================")
    print(json.dumps(response, indent=2))
    print("====================================")

    if response["task"]["developer_instructions"] != "":
        developer_instructions = response["task"]["developer_instructions"]
    else:
        developer_instructions = task["developer_instructions"]

    if response["task"]["developer_guidelines"] != "":
        developer_guidelines = response["task"]["developer_guidelines"]
    else:
        developer_guidelines = task["developer_guidelines"]

    if response["task"]["tester_instructions"] != "":
        tester_instructions = response["task"]["tester_instructions"]
    else:
        tester_instructions = task["tester_instructions"]

    if response["task"]["tester_guidelines"] != "":
        tester_guidelines = response["task"]["tester_guidelines"]
    else:
        tester_guidelines = task["tester_guidelines"]


    current_task = {
        "task_id": task["task_id"],
        "task_title": task["task_title"],
        "task_explanation": task["task_explanation"],
        "task_status": response["task"]["task_status"],
        "commit_message": response["task"]["commit_message"],

        "branch_name": task["branch_name"],

        "developer_instructions": developer_instructions,
        "developer_guidelines": developer_guidelines,
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

        "tester_instructions": tester_instructions,
        "tester_guidelines": tester_guidelines,
        "tester_required_files": task["tester_required_files"],
        "tester_implementation": task["tester_implementation"],
        "tester_execution": task["tester_execution"],
        "tester_file_changes": task["tester_file_changes"],

        "tester_implementation_stdout_report": task["tester_implementation_stdout_report"],
        "tester_implementation_stderr_report": task["tester_implementation_stderr_report"],
        "tester_implementation_error_type_report": task["tester_implementation_error_type_report"],
        "tester_execution_stdout_report": task["tester_execution_stdout_report"],
        "tester_execution_stderr_report": task["tester_execution_stderr_report"],
        "tester_execution_error_type_report": task["tester_execution_error_type_report"],
    }

    return current_task

ASSIGNMENT_SYSTEM_PROMPT = """
You are TaskDispatcher-bot, an AI agent in the role of Tech Lead / Engineering Manager in a multi‑agent development system.

When given:
  1. A high‑level project description
  2. A list of project files (each with path and a short content summary)
  3. A single task’s title and detailed explanation
  
Assumptions you should make:
  • The project’s virtual environment already exists in `.venv` and is currently activated—do not plan to create or activate another.
  • You are already located in the project’s root directory—do not plan to create or change to a root folder.
  • You should instruct the developer and the tester agents to use the virtual environment's `pip`, `python`, etc

Your job is to produce a JSON payload that assigns clear, actionable work to two agents—a Developer Agent and a Tester Agent—while capturing your internal decision process. Specifically, you must:
1. Review the project description and file summaries to identify which existing code artifacts are relevant to the task.
3. For the **Developer Agent**, provide:
   - **developer_instructions**: step‑by‑step implementation steps
   - **developer_guidelines**: coding conventions and best practices to follow
   - **developer_required_files**: a list of file paths whose contents should be imported or consulted

4. For the **Tester Agent**, provide:
   - **tester_instructions**: step‑by‑step testing steps to verify correctness and guideline compliance
   - **tester_guidelines**: testing conventions and best practices
   - **tester_required_files**: a list of file paths whose contents help write or run tests

5. Include a top‑level **reasoning** field with your internal chain of thought: how you selected files, structured the workflow, and derived the branch name.

**Output ONLY valid JSON** matching this schema (no extra keys or prose outside the JSON):
```json
{
  "reasoning": "<internal chain‑of‑thought>",
  "task": {
    "developer_instructions": [
      "<step 1>",
      "<step 2>",
      "…"
    ],
    "developer_guidelines": [
      "<guideline 1>",
      "<guideline 2>",
      "…"
    ],
    "developer_required_files": [
      "<path/to/file1>",
      "<path/to/file2>"
    ],
    "tester_instructions": [
      "<step 1>",
      "<step 2>",
      "…"
    ],
    "tester_guidelines": [
      "<guideline 1>",
      "<guideline 2>",
      "…"
    ],
    "tester_required_files": [
      "<path/to/fileA>",
      "<path/to/fileB>"
    ]
  }
}
"""

ASSIGNMENT_USER_PROMPT = """
Project Description:
{project_description}

Task Title:
{task_title}

Task Explanation:
{task_explanation}

Project Files:
{files}

Using the schema defined in the system prompt, generate the JSON assignment payload.
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

Assumptions you should make:
  • The project’s virtual environment already exists in `.venv` and is currently activated—do not plan to create or activate another.
  • You are already located in the project’s root directory—do not plan to create or change to a root folder.
  • You should instruct the developer and the tester agents to use the virtual environment's `pip`, `python`, etc

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
2. Never emit `\` followed by any other character (e.g. `\$` is invalid).
3. After generating the JSON, perform an internal “lint”:
   - Parse it with a JSON parser.
   - If the parser errors, fix your escaping before returning.
4. Always wrap scripts or multi‑line text in a JSON string using one of:
   a) A `here-doc` inside the JSON (e.g. an array of lines), or  
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


def assign_a_task(project_description: str, database: dict, task: dict):

    text = "----------\n"
    for i, v in enumerate(list(database.values())):
        d_type = "File" if v["type"] == "file" else "Directory"
        text += f"{d_type} {i + 1} Path: {v['path']}\n"
        text += f"{d_type} {i + 1} Content Summary: {v['summary']}\n"
        text += "----------\n"

    print(text)

    response = utils.rag_utils.get_azure_response(
        system_prompt=ASSIGNMENT_SYSTEM_PROMPT,
        user_prompt=ASSIGNMENT_USER_PROMPT,
        system_prompt_kwargs=None,
        user_prompt_kwargs={
            "project_description": project_description,
            "task_title": task["task_title"],
            "task_explanation": task["task_explanation"],
            "files": text
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

        "developer_instructions": developer_instructions,
        "developer_guidelines": developer_guidelines,
        "developer_required_files": task["developer_required_files"],
        "developer_implementation": task["developer_implementation"],

        "developer_implementation_stdout_report": task["developer_implementation_stdout_report"],
        "developer_implementation_stderr_report": task["developer_implementation_stderr_report"],
        "developer_implementation_error_type_report": task["developer_implementation_error_type_report"],

        "tester_instructions": tester_instructions,
        "tester_guidelines": tester_guidelines,
        "tester_required_files": task["tester_required_files"],
        "tester_implementation": task["tester_implementation"],
        "tester_execution": task["tester_execution"],

        "tester_implementation_stdout_report": task["tester_implementation_stdout_report"],
        "tester_implementation_stderr_report": task["tester_implementation_stderr_report"],
        "tester_implementation_error_type_report": task["tester_implementation_error_type_report"],
        "tester_execution_stdout_report": task["tester_execution_stdout_report"],
        "tester_execution_stderr_report": task["tester_execution_stderr_report"],
        "tester_execution_error_type_report": task["tester_execution_error_type_report"],
    }

    return current_task

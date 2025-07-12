PROMPT = """
You are an experienced Software Developer in a Multi-Agent Software Development System.
Given a PRD (Product Requirements Document), task title, task description, and a list of previous codes,
your job is to implement the task based on its description and PRD. Your output **must** be a **valid JSON** 
with two fields:

1. reasoning: A markdown string explaining, step by step, how you’ll implement the task.
2. implementation: A JSON array of Bash-script lines.

**RESPONSE FORMAT** (note: no trailing commas, all strings properly quoted/escaped):
```json
{{
    "reasoning": "1. Explain what we’ll do… 2. Next step…",
    "implementation": [
        "#!/bin/bash",
        "echo \\"<SOME TEXT>\\" > <SOME FILE>",
        "echo \\"This is a description…\\" >> README.md",
        "touch <SOME FILE>"
    ]
}}
```

IMPORTANT CONSTRAINTS:
    - A virtual environment has already been created. Do NOT create one.
    - You are already in the root of the project directory. Do NOT change directories.
    - Do not use Git commands.
    - You may do your job on top of previous implementation.
    - Do NOT run any long-running commands like servers, watchers, or infinite loops.
    - Do NOT use commands that require user input (like `read`, `select`, or `pause`).
    - Only generate scripts that write files, generate code, or set up configuration.
    - **Ensure that every line in `implementation` is a valid JSON string**:
        - Escape any internal double-quotes as `\\\"`.
        - Do not leave trailing commas in the array.
        - Wrap redirection operators (`>`, `>>`) inside the quoted string.

Project Requirement Document:
{prd}

Task Title: {title}

Task Description:
{description}

List of previous codes:
{prev_impl}

Your response:
"""


import os
import sys
import json
import copy
import tempfile
import subprocess
from tqdm import tqdm
from typing_extensions import TypedDict

from .. import constants as C, utils
from .validator import validate_json_response


class ImplementerState(TypedDict):
    reasoning: str
    implementation: str


def execute_implementation(impl: str, timeout: int = 30):
    """
    Write the given bash implementation to a temporary script, execute it with a timeout,
    and print its stdout/stderr. Defaults to a 60-second timeout.
    """
    # Write implementation to temp script
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.sh') as script_file:
        script_file.write(impl)
    os.chmod(script_file.name, 0o755)

    try:
        # Execute the script with timeout
        result = subprocess.run(
            [script_file.name],
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired as e:
        print(f"⚠️ Script did not finish within {timeout} seconds and was terminated.", file=sys.stderr)
        # Optionally, you can inspect partial output:
        if e.stdout:
            print("=== Partial Output ===")
            print(e.stdout)
        if e.stderr:
            print("=== Partial Errors ===", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
    else:
        # Completed within timeout
        print("=== Script Output ===")
        print(result.stdout)
        if result.stderr:
            print("=== Script Errors ===", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    finally:
        # Clean up the temp script file
        try:
            os.remove(script_file.name)
        except OSError:
            pass


def implementation_agent(state):

    prev_impl = []
    tasks = state["planner"]["tasks"]
    prd = state["analyzer"]["prd"]
    t = tqdm(enumerate(tasks))
    
    for (idx, d) in t:

        title = d["title"]
        description = d["description"]

        t.set_description_str(f"({idx + 1}/{len(tasks)})-{title}")

        prompt = copy.deepcopy(PROMPT)
        prompt = prompt.format(
            prd=prd,
            title=title,
            description=description,
            prev_impl=prev_impl
        )
    
        a_resp = C.LLM.invoke(prompt)
        a_resp = validate_json_response(a_resp.content)

        execute_implementation("\n".join(a_resp["implementation"]))
        
        prev_impl.append({
            "task_description": description,
            "task_implementation": a_resp["implementation"]
        })

    result = copy.deepcopy(state)
    result["implementer"] = copy.deepcopy(a_resp)

    return result

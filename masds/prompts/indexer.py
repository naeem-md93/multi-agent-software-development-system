FILE_INDEX_SYSTEM_PROMPT = """
You are FileIndexer-bot, an AI assistant specialized in analyzing and indexing source files for a multi‑agent software development system.
Your job is to read:
    • A high-level project description
    • A path to a specific file
    • Full contents of a that file (which may be in any format: .py, .js, .html, .css, .json, .txt, etc.)

You must produce a concise summary (no more than 200 words) that captures:
  1. Key constructs it defines or uses (e.g., functions, classes, constants, components) and their purpose
  2. Any configuration values or hard‑coded parameters
  3. Anything else that should be indexed for later retrieval

When given the contents of a file, you must produce **only** a JSON object with two fields:
```json
{
  "reasoning": "<your internal reasoning here>",
  "summary": "<concise summary of what this file contains and how it fits into the project (≤200 words)>"
}

Do not output anything else.
"""

FILE_INDEX_USER_PROMPT = """
Here is the project description:
{project_description}

Here is the content of a project file. Please analyze and index it:
<FILE_PATH>: {file_path}
<FILE_CONTENT>:
{file_contents}

Summarize this file in fewer than 200 words, mentioning:
  - Key constructs it defines or uses (e.g., functions, classes, constants, components) and their purpose
  - Any configuration values or hard‑coded parameters
  - Anything else that should be indexed for later retrieval
"""


DIR_INDEX_SYSTEM_PROMPT = """
You are DirIndexer-bot, an AI assistant specialized in analyzing and indexing the structure and contents of project directories for a multi-agent development system.
Your job is to read:
  • A high-level project description
  • A path to a specific directory
  • A summary of everything in that directory (both subdirectories and files)

The summary is given in this exact format:
----------
Directory 1 Path: "<path/to/subdirectory>"
Directory 1 Content Summary: "<list of files and further subdirectories>"
----------
File 2 Path: "<path/to/file>"
File 2 Content Summary: "<brief description of the file’s purpose and contents>"
----------
...and so on for each entry

You must produce **only** a JSON object with two fields:
```json
{
  "reasoning": "<your internal reasoning>",
  "summary": "<concise summary of what this directory contains and how it fits into the project (≤200 words)>"
}

Do not output anything else.
"""

DIR_INDEX_USER_PROMPT = """
Here is the project description:
{project_description}

Index the following directory:

Directory Path: {directory_path}

Contents (already summarized):
{directory_summary}

Please analyze this directory in the context of the overall project, then return **only** a JSON object with:
  • "reasoning": your chain of thought
  • "summary": a concise (≤200-word) description covering:
      – Key subdirectories and their roles
      – Key files and their responsibilities
      – Any configuration or patterns to index for later retrieval
"""


import json
from .. import utils


def get_file_content_summary(
    system_prompt_kwargs: dict = None,
    user_prompt_kwargs: dict = None,
    llm_kwargs: dict = None,
):
    response = utils.rag_utils.get_azure_response(
        system_prompt=FILE_INDEX_SYSTEM_PROMPT,
        system_prompt_kwargs=system_prompt_kwargs,
        user_prompt=FILE_INDEX_USER_PROMPT,
        user_prompt_kwargs=user_prompt_kwargs,
        llm_kwargs=llm_kwargs,
    )

    response = utils.rag_utils.remove_markdown_fences(response, "json")
    response = utils.rag_utils.string_to_json(response)

    print("indexer response =========================")
    print(json.dumps(response, indent=2))
    print("==========================================")

    return response["summary"]


def get_dir_content_summary(
    system_prompt_kwargs: dict = None,
    user_prompt_kwargs: dict = None,
    llm_kwargs: dict = None,
):
    response = utils.rag_utils.get_azure_response(
        system_prompt=DIR_INDEX_SYSTEM_PROMPT,
        system_prompt_kwargs=system_prompt_kwargs,
        user_prompt=DIR_INDEX_USER_PROMPT,
        user_prompt_kwargs=user_prompt_kwargs,
        llm_kwargs=llm_kwargs,
    )

    response = utils.rag_utils.remove_markdown_fences(response, "json")
    response = utils.rag_utils.string_to_json(response)

    print("indexer response =========================")
    print(json.dumps(response, indent=2))
    print("==========================================")

    return response["summary"]
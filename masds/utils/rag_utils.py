import os
import json
import dotenv
import subprocess
import tempfile
import requests
from openai import AzureOpenAI


dotenv.load_dotenv()


def get_novita_response(
    system_prompt: str,
    user_prompt: str,
    system_prompt_kwargs: dict = None,
    user_prompt_kwargs: dict = None,
    llm_kwargs: dict = None
) -> str:

    if system_prompt_kwargs is not None:
        system_prompt = system_prompt.format(**system_prompt_kwargs)

    if user_prompt_kwargs is not None:
        user_prompt = user_prompt.format(**user_prompt_kwargs)

    if llm_kwargs is None:
        llm_kwargs = {}

    headers = {
        "Content-Type": "application/json",
        "Authorization": os.getenv("NOVITA_API_KEY")
    }

    payload = {
        "model": os.getenv("NOVITA_MODEL_NAME"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        **llm_kwargs
    }

    response = requests.request(
        "POST",
        os.getenv("NOVITA_API_URL"),
        json=payload,
        headers=headers
    )

    try:
        response = response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(vars(e))
        print(response)
        exit(500)

    return response


def get_azure_response(
    system_prompt: str,
    user_prompt: str,
    system_prompt_kwargs: dict = None,
    user_prompt_kwargs: dict = None,
    llm_kwargs: dict = None
):
    client = AzureOpenAI(
        api_version=os.getenv("AZURE_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_SUBSCRIPTION_KEY"),
    )

    if system_prompt_kwargs is not None:
        system_prompt = system_prompt.format(**system_prompt_kwargs)

    if user_prompt_kwargs is not None:
        user_prompt = user_prompt.format(**user_prompt_kwargs)

    if llm_kwargs is None:
        llm_kwargs = {}

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=os.getenv("AZURE_DEPLOYMENT"),
        **llm_kwargs
    )

    try:
        response = response.choices[0].message.content
    except Exception as e:
        print(f"{system_prompt=}")
        print(f"{user_prompt=}")
        print(vars(e))
        print(response)
        exit(500)

    return response


def remove_markdown_fences(response: str, fence_type: str) -> str:
    if response.strip().startswith(f"```{fence_type}"):
        response = response.strip().removeprefix(f"```{fence_type}").removesuffix("```")

    return response


def response_to_json(response: str) -> dict:
    response = remove_markdown_fences(response, "json")

    try:
        response = json.loads(response)
    except json.JSONDecodeError as e:
        print(response)
        print(vars(e))
        exit(500)

    return response


def execute_with_timeout(script_content: str, timeout: int = 300) -> tuple[str, str]:
    """
    Helper to execute a bash script with a timeout, preventing infinite loops.

    Returns:
        stdout, stderr
    """
    # Clean up fences if present
    clean_script = remove_markdown_fences(script_content, "bash")

    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as script_file:
        script_file.write(clean_script)
        script_file.flush()
        path = script_file.name

    # Make executable
    subprocess.run(["chmod", "+x", path], check=True)

    try:
        # Execute with timeout
        proc = subprocess.run(
            ["bash", path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return proc.stdout, proc.stderr

    except subprocess.TimeoutExpired as e:
        # Kill the hung process and return partial output
        return e.stdout or "", e.stderr or f"Execution timed out after {timeout}s"


def run_subtask(implementation_script: str, test_script: str, timeout: int = 300) -> dict[str, str]:
    """
    Executes both the implementation and test scripts, returning a report.

    Parameters:
        implementation_script: Bash script to implement feature
        test_script: Bash script to install/run tests
        timeout: Max seconds per script

    Returns:
        A dict with keys:
          - implementation_stdout
          - implementation_stderr
          - test_stdout
          - test_stderr
    """
    report: dict[str, str] = {}

    # Run implementation
    impl_out, impl_err = execute_with_timeout(implementation_script, timeout=timeout)
    report['implementation_stdout'] = impl_out
    report['implementation_stderr'] = impl_err

    # Only run tests if implementation succeeded (exit code 0)
    if impl_err:
        report['test_stdout'] = ''
        report['test_stderr'] = 'Skipping tests due to implementation errors.'
    else:
        test_out, test_err = execute_with_timeout(test_script, timeout=timeout)
        report['test_stdout'] = test_out
        report['test_stderr'] = test_err

    return report
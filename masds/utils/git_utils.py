from typing import List, Dict
import subprocess


def commit_and_merge_changes(branch_name: str, commit_message: str, file_changes: List[Dict[str, str]]):
    """
    Commits all file changes to the specified branch, merges it into main, and checks out main.

    Parameters:
        branch_name (str): The name of the feature branch.
        commit_message (str): Commit message describing the changes.
        file_changes (List[Dict]): A list of file change dictionaries with 'file_path' and 'change_type'.

    Returns:
        str: Output log of the git operations.
    """
    logs = []

    def run(cmd: List[str], check=True):
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        logs.append(f"$ {' '.join(cmd)}\n{result.stdout}{result.stderr}")
        return result

    try:
        # Stage all changed files
        for change in file_changes:
            if change["change_type"] == "deleted":
                run(["git", "rm", change["path"]])
            else:  # created or modified
                run(["git", "add", change["path"]])

        # Commit the changes
        run(["git", "commit", "-m", commit_message])

        # Switch to main branch
        run(["git", "checkout", "main"])

        # Merge the feature branch into main
        run(["git", "merge", "--no-ff", branch_name])

    except subprocess.CalledProcessError as e:
        logs.append(f"Error: {e.stderr}")
        raise RuntimeError(f"Git operation failed: {e.stderr}")

    return "\n".join(logs)
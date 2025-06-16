import os
import json
import subprocess

from pydantic.v1.validators import decimal_validator
from tqdm import tqdm, trange

from .. import utils, prompts


class MultiAgentSoftwareDevelopmentSystem:
    def __init__(self):
        super().__init__()

        self.project_name = None
        self.project_dir = None
        self.changes_history = []
        self.database = {}

        self.task_format = {
            "tasks": [
                {
                    "id": "<A unique numeric **id** (reflecting the implementation order).>",
                    "title": "<A concise **title**.>",
                    "explanation": "<A brief **explanation** describing *why* this task is needed and *what* it delivers.>",
                    "status": "one of `pending`|`in-progress`|`done`, default=pending, only the first task should be in-progress",
                    "branch_name": "",
                    "implementation": {
                        "instructions": [],
                        "guidelines": [],
                        "required_file": [],

                        "source_code": "",
                        "execution": "",
                        "file_changes": [],
                        "report": {"stdout": "", "stderr": ""},
                    },
                    "testing": {
                        "instructions": [],
                        "guidelines": [],
                        "required_file": [],

                        "source_code": "",
                        "execution": "",
                        "file_changes": [],
                        "report": {"stdout": "", "stderr": ""},
                    },
                    "commit_message": "",
                    "validator_message": ""
                }
            ]
        }

    def init_project(self, project_name):

        self.project_name = project_name
        self.project_dir = os.path.join(os.getcwd(), project_name)
        os.makedirs(self.project_dir)
        os.chdir(self.project_dir)
        subprocess.call(["git", "init"])
        subprocess.call(["git", "config", "--global", "user.name", "'Naeem Mohammadi'"])
        subprocess.call(["git", "config", "--global", "user.email", "'naeem.mohammadi1993@gmail.com'"])
        subprocess.call(["git", "checkout", "-b", "main"])

    def break_down_a_project(self, project_name: str, project_description: str) -> dict:

        response = utils.rag_utils.get_azure_response(
            system_prompt=prompts.project_manager.SYSTEM_PROMPT,
            user_prompt=prompts.project_manager.USER_PROMPT,
            system_prompt_kwargs=None,
            user_prompt_kwargs={"project_name": project_name, "project_description": project_description},
            llm_kwargs={"temperature": 0.5}
        )
        response = utils.rag_utils.remove_markdown_fences(response, "json")
        tasks = utils.rag_utils.string_to_json(response)

        print("break_down_a_project ==========================")
        print(json.dumps(tasks, indent=2))
        print("====================================")

        tasks = tasks["tasks"]

        return tasks

    def assign_a_task(self, task: dict):

        response = utils.rag_utils.get_azure_response(
            system_prompt=prompts.tech_lead.ASSIGNMENT_SYSTEM_PROMPT,
            user_prompt=prompts.tech_lead.ASSIGNMENT_USER_PROMPT,
            system_prompt_kwargs=None,
            user_prompt_kwargs={
                "file_changes_history": self.changes_history,
                "task_title": task["task_title"],
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

    def prepare_the_development_environment(self, task: dict) -> None:
        subprocess.call(["git", "checkout", "-b", task["branch_name"]])

    def implement_a_task(self, task: dict):

        required_files = "\n==========\n"
        for x in task["developer_required_files"]:
            required_files += f"File Path: {x}\n"
            required_files += f"File Contents:\n{self.database[x]}\n"
            required_files += "--------------\n"
        required_files += "=============\n"

        response = utils.rag_utils.get_azure_response(
            system_prompt=prompts.software_developer.SYSTEM_PROMPT,
            user_prompt=prompts.software_developer.USER_PROMPT,
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

    def execute_developer_codes(self, task: dict) -> dict:

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

    def implement_a_test(self, task):

        required_files = "\n==========\n"
        for x in task["tester_required_files"]:
            required_files += f"File Path: {x}\n"
            required_files += f"File Contents:\n{self.database[x]}\n"
            required_files += "--------------\n"
        required_files += "=============\n"

        response = utils.rag_utils.get_azure_response(
            system_prompt=prompts.qa_engineer.SYSTEM_PROMPT,
            user_prompt=prompts.qa_engineer.USER_PROMPT,
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

    def execute_tester_codes(self, task):

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

    def update_changes_history_and_database(self, task_id: str, task_title: str, task_branch_name: str, file_changes: list[dict]):

        for d in file_changes:

            if os.path.isfile(d["path"]):
                d_content = open(d["path"], "r").read()
                d_type = "file"
            elif os.path.isdir(d["path"]):
                d_content = f"Directory containing:\n{os.listdir(d['path'])}"
                d_type = "directory"
            else:
                print(d["path"])
                exit(500)

            self.database[d["path"]] = d_content

            self.changes_history.append({
                "task_id": task_id,
                "task_title": task_title,
                "branch_name": task_branch_name,
                "path": d["path"],
                "type": d_type,
                "change_type": d["change_type"],
                "explanation": d["explanation"],
                "modification_date": utils.time_utils.get_now()
            })

        print("database update ==========================")
        print(json.dumps(self.database, indent=2))
        print("====================================")

        print("changes history update ==========================")
        print(json.dumps(self.changes_history, indent=2))
        print("====================================")

    def review_a_task(self, task):

        response = utils.rag_utils.get_azure_response(
            system_prompt=prompts.tech_lead.REVIEW_SYSTEM_PROMPT,
            user_prompt=prompts.tech_lead.REVIEW_USER_PROMPT,
            system_prompt_kwargs=None,
            user_prompt_kwargs={
                "task_title": task["task_title"],
                "task_explanation": task["task_explanation"],

                "developer_instructions": task["developer_instructions"],
                "developer_guidelines": task["developer_guidelines"],
                "developer_implementation": task["developer_implementation"],
                "developer_execution": task["developer_execution"],
                "developer_file_changes": task["developer_file_changes"],

                "stdout_implementation": task["developer_implementation_stdout_report"],
                "stderr_implementation": task["developer_implementation_stderr_report"],
                "error_type_implementation": task["developer_implementation_error_type_report"],

                "stdout_execution": task["developer_execution_stdout_report"],
                "stderr_execution": task["developer_execution_stderr_report"],
                "error_type_execution": task["developer_execution_error_type_report"],

                "tester_instructions": task["tester_instructions"],
                "tester_guidelines": task["tester_guidelines"],
                "tester_implementation": task["tester_implementation"],
                "tester_execution": task["tester_execution"],
                "tester_file_changes": task["tester_file_changes"],

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

    def merge_the_development_environment(self, task: dict):

        for change in task["developer_file_changes"]:
            if change["change_type"] == "deleted":
                subprocess.call(["git", "rm", change["path"]])
            else:  # created or modified
                subprocess.call(["git", "add", change["path"]])

        for change in task["tester_file_changes"]:
            if change["change_type"] == "deleted":
                subprocess.call(["git", "rm", change["path"]])
            else:  # created or modified
                subprocess.call(["git", "add", change["path"]])


        subprocess.call(["git", "commit", "-m", task["commit_message"]])

        # Switch to main branch
        subprocess.call(["git", "checkout", "main"])

        # Merge the feature branch into main
        subprocess.call(["git", "merge", "--no-ff", task["branch_name"]])

    def develop_a_project(self, project_name: str, project_description: str, max_iter: int = 10) -> None:

        self.init_project(project_name=project_name)

        tasks = self.break_down_a_project(project_name, project_description)

        t = tqdm(enumerate(tasks))
        for iii, current_task in t:
            current_task = self.assign_a_task(current_task)

            self.prepare_the_development_environment(current_task)

            for idx in range(max_iter):
                t.set_description_str(f"Task ({iii+1}/{len(tasks)}) | Try ({idx + 1}/{max_iter}) - {current_task['task_title']}")

                current_task = self.implement_a_task(current_task)

                current_task = self.execute_developer_codes(current_task)

                self.update_changes_history_and_database(
                    current_task["task_id"],
                    current_task["task_title"],
                    current_task["branch_name"],
                    current_task["developer_file_changes"]
                )

                current_task = self.implement_a_test(current_task)

                current_task = self.execute_tester_codes(current_task)
                self.update_changes_history_and_database(
                    current_task["task_id"],
                    current_task["task_title"],
                    current_task["branch_name"],
                    current_task["tester_file_changes"]
                )

                current_task = self.review_a_task(current_task)

                if current_task["task_status"] == "done":
                    break

            assert current_task["task_status"] == "done", f"could not finish the task in {max_iter} iterations!!!"

            self.merge_the_development_environment(current_task)

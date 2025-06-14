import json
import os
import subprocess
from tqdm import tqdm

from .teacher import TeacherModel
from .. import prompts, utils


class MultiAgentDevelopmentSystem:
    def __init__(self):
        super().__init__()

        self.project_name = None
        self.project_dir = None
        self.change_history = []
        self.file_db = {}

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
        subprocess.call(["git", "config", "--global", "init.defaultBranch", "main"])
        subprocess.call(["git", "config", "--global", "user.name", "'Naeem Mohammadi'"])
        subprocess.call(["git", "config", "--global", "user.email", "'naeem.mohammadi1993@gmail.com'"])

    def get_one_task(self, planning):
        in_progress_tasks = [(i, x) for i, x in enumerate(planning) if x["status"] == "in-progress"]
        if len(in_progress_tasks) > 0:
            return in_progress_tasks[0]

        pending_tasks = [(i, x) for i, x in enumerate(planning) if x["status"] == "pending"]
        if len(pending_tasks) > 0:
            return pending_tasks[0]
        return None, None

    def develop(self, project_name: str, project_description: str, max_iter: int = 10) -> None:

        self.init_project(project_name=project_name)

        planning = utils.rag_utils.get_azure_response(
            system_prompt=prompts.manager.SYSTEM_PROMPT,
            user_prompt=prompts.manager.USER_PROMPT,
            system_prompt_kwargs=None,
            user_prompt_kwargs={"project_name": project_name, "project_description": project_description},
            llm_kwargs={"temperature": 0.5}
        )
        planning = utils.rag_utils.response_to_json(planning)

        print("init_planning ==========================")
        print(json.dumps(planning, indent=2))
        print("====================================")

        planning = planning["tasks"]

        t = tqdm(range(max_iter))
        for idx in t:

            current_task_id, current_task = self.get_one_task(planning)
            if (current_task_id is None) or (current_task is None):
                break

            t.set_description_str(f"({idx+1}/{max_iter}) - {current_task['title']}")

            print("current_task ==========================")
            print(json.dumps(current_task, indent=2))
            print("====================================")

            current_task = utils.rag_utils.get_azure_response(
                system_prompt=prompts.validator.VALIDATOR_SYSTEM_PROMPT,
                user_prompt=prompts.validator.VALIDATOR_USER_PROMPT,
                system_prompt_kwargs=None,
                user_prompt_kwargs={"task_data": current_task, "file_change_history": self.change_history},
                llm_kwargs={"temperature": 0.5}
            )
            current_task = utils.rag_utils.response_to_json(current_task)
            print("validator_response ==========================")
            print(json.dumps(current_task, indent=2))
            print("====================================")

            subprocess.call(["git", "checkout", "-B", current_task["branch_name"]])

            current_task = utils.rag_utils.get_azure_response(
                system_prompt=prompts.engineer.ENGINEER_SYSTEM_PROMPT,
                user_prompt=prompts.engineer.ENGINEER_USER_PROMPT,
                system_prompt_kwargs=None,
                user_prompt_kwargs={
                    "task_data": current_task,
                    "implementation_required_files": [
                        {"file_path": fp, "content": open(fp, "r").read()}
                        for fp in current_task["implementation"]["required_files"]
                    ],
                    "testing_required_files": [
                        {"file_path": fp, "content": open(fp, "r").read()}
                        for fp in current_task["testing"]["required_files"]
                    ]
                },
                llm_kwargs={"temperature": 0.5}
            )

            current_task = utils.rag_utils.response_to_json(current_task)
            print("engineer response ====================================")
            print(json.dumps(current_task, indent=2))
            print("====================================")

            current_task["implementation"]["report"] = {
                "source_code": utils.rag_utils.execute_with_timeout(current_task["implementation"]["source_code"]),
                "execution": utils.rag_utils.execute_with_timeout(current_task["implementation"]["execution"]),
            }

            current_task["testing"]["report"] = {
                "source_code": utils.rag_utils.execute_with_timeout(current_task["testing"]["source_code"]),
                "execution": utils.rag_utils.execute_with_timeout(current_task["testing"]["execution"]),
            }

            for d in current_task["implementation"]["file_changes"]:
                self.file_db[d["file_path"]] = open(d["file_path"], "r").read()

                self.change_history.append({
                    "task_id": current_task["id"],
                    "task_title": current_task["title"],
                    "branch_name": current_task["branch_name"],
                    "file_path": d["file_path"],
                    "change_type": d["change_type"],
                    "explanation": d["explanation"],
                    "modification_date": utils.time_utils.get_now()
                })

            current_task = utils.rag_utils.get_azure_response(
                system_prompt=prompts.validator.VALIDATOR_SYSTEM_PROMPT,
                user_prompt=prompts.validator.VALIDATOR_USER_PROMPT,
                system_prompt_kwargs=None,
                user_prompt_kwargs={"task_data": current_task, "file_change_history": self.change_history},
                llm_kwargs={"temperature": 0.5}
            )
            current_task = utils.rag_utils.response_to_json(current_task)
            print("final_validator_response ==========================")
            print(json.dumps(current_task, indent=2))
            print("====================================")

            planning[current_task_id] = current_task

            if current_task["status"] == "done":
                final_message = utils.git_utils.commit_and_merge_changes(
                    current_task["branch_name"],
                    current_task["commit_message"],
                    file_changes=current_task["implementation"]["file_changes"] + current_task["testing"]["file_changes"]
                )

                print("final_message ==========================")
                print(final_message)
                print("====================================")

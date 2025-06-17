import os
import json
import subprocess

from pydantic.v1.validators import decimal_validator
from tqdm import tqdm, trange

from .. import utils, prompts


class MultiAgentSoftwareDevelopmentSystem:
    def __init__(self):
        super().__init__()

        self.changes_history = []
        self.database = {}

    @staticmethod
    def init_a_project(project_dir: str) -> None:
        os.makedirs(project_dir, exist_ok=True)
        os.chdir(project_dir)

    def index_a_project(self) -> None:

        project_files = utils.os_utils.get_project_files(os.getcwd())

        t = tqdm(enumerate(project_files))
        for i, fp in t:
            t.set_description_str(f"({i + 1}/{len(project_files)}) - {fp}")

            content = open(fp, "r", encoding="utf-8").read()
            if len(content) > 10:
                self.database[fp] = content

                self.changes_history.append({
                    "task_id": "0",
                    "task_title": "index_project",
                    "branch_name": "main",
                    "path": fp,
                    "type": "file",
                    "change_type": "created",
                    "explanation": prompts.indexer.get_llm_response(
                        user_prompt_kwargs={"contents": content},
                        llm_kwargs={"temperature": 0.5}
                    ),
                    "modification_date": utils.time_utils.get_now()
                })

    def update_changes_history_and_database(self, task: dict, file_changes: list[dict]):

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
                "task_id": task["task_id"],
                "task_title": task["task_title"],
                "branch_name": task["branch_name"],
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


    def develop_a_project(self, project_dir: str, project_description: str, max_iter: int = 10) -> None:

        # initialize the project
        self.init_a_project(project_dir=project_dir)
        input("init_project ===============")

        # index the project
        self.index_a_project()
        input("index_project ===============")

        tasks = prompts.project_manager.break_down_a_project(project_description)

        input("break_down_a_project ===============")

        t = tqdm(enumerate(tasks))
        for iii, current_task in t:
            current_task = prompts.tech_lead.assign_a_task(self.changes_history, current_task)
            input("assign_a_task ===============")

            for idx in range(max_iter):
                t.set_description_str(f"Task ({iii+1}/{len(tasks)}) | Try ({idx + 1}/{max_iter}) - {current_task['task_title']}")

                current_task = prompts.software_developer.implement_a_task(self.database, current_task)
                input("implement_a_task ===============")

                current_task = prompts.software_developer.execute_developer_codes(current_task)
                input("execute_developer_codes ===============")

                self.update_changes_history_and_database(current_task, current_task["developer_file_changes"])
                input("update_changes_history_and_database ===============")

                current_task = prompts.qa_engineer.implement_a_test(self.database, current_task)
                input("implement_a_test ===============")

                current_task = prompts.qa_engineer.execute_tester_codes(current_task)
                input("execute_tester_codes ===============")

                self.update_changes_history_and_database(current_task, current_task["tester_file_changes"])
                input("update_changes_history_and_database ===============")

                current_task = prompts.tech_lead.review_a_task(current_task)
                input("review_a_task ===============")

                if current_task["task_status"] == "done":
                    break

            utils.os_utils.write_pickle_file("123.pk", self)

            assert current_task["task_status"] == "done", f"could not finish the task in {max_iter} iterations!!!"


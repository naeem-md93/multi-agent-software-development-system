import os
import json
import subprocess
from tqdm import tqdm, trange

from .. import utils, prompts
from ._index_a_project import index_a_project
from ._init_a_project import init_a_project


class MultiAgentSoftwareDevelopmentSystem:
    def __init__(self, project_dir: str) -> None:
        super().__init__()

        self.project_dir = project_dir
        self.cache_dir = os.path.join(os.getcwd(), f".{project_dir}_cache")
        self.checkpoint_path = os.path.join(self.cache_dir, "checkpoint.pk")
        self.database_path = os.path.join(self.cache_dir, "database.pk")

        if os.path.exists(self.database_path):
            self.database = utils.os_utils.read_pickle_file(self.database_path)
        else:
            self.database = {}

    def develop_a_project(self, project_description: str, ignore_dirs: list[str], ignore_indexes: list[str], max_iter: int = 10) -> None:

        # initialize the project
        # print("<init_a_project>")
        init_a_project(self.project_dir)
        # input("</init_a_project>")

        # index the project
        # print("<index_a_project>")
        project_files, project_dirs = utils.os_utils.get_project_dirs_files(os.getcwd(), ignore_dirs, ignore_indexes)
        self.database = index_a_project(project_description, project_files, project_dirs, self.database, self.database_path)
        # input("</index_a_project>")

        # break down the project into multiple tasks
        # print("<break_down_a_project>")
        tasks = prompts.project_manager.break_down_a_project(project_description, self.database)
        # input("</break_down_a_project>")

        t = tqdm(enumerate(tasks))
        for iii, current_task in t:

            # assign a task to the developer and the tester agents
            # print("<assign_a_task>")
            current_task = prompts.tech_lead.assign_a_task(project_description, self.database, current_task)
            # input("</assign_a_task>")

            for idx in range(max_iter):
                t.set_description_str(f"Task ({iii+1}/{len(tasks)}) | Try ({idx + 1}/{max_iter}) - {current_task['task_title']}")

                # implementation of the developer
                # print("<implement_a_task>")
                current_task = prompts.software_developer.implement_a_task(self.database, current_task)
                # input("</implement_a_task>")

                # execute the developer's implementation
                # print("<execute_developer_codes>")
                current_task = prompts.software_developer.execute_developer_codes(current_task)
                # input("</execute_developer_codes>")

                # implementation of the tester
                # print("<implement_a_test>")
                current_task = prompts.qa_engineer.implement_a_test(self.database, current_task)
                # input("</implement_a_test>")

                # execute the tester's implementation
                # print("<execute_tester_codes>")
                current_task = prompts.qa_engineer.execute_tester_codes(current_task)
                # input("</execute_tester_codes>")

                # review the task
                # print("<review_a_task>")
                current_task = prompts.tech_lead.review_a_task(current_task)
                # input("</review_a_task>")

                # re-index the project
                # print("<re-index the project>")
                project_files = utils.os_utils.get_project_files(os.getcwd(), ignore_dirs)
                self.database = index_a_project(project_files, self.database, self.database_path)
                # input("</re-index the project>")

                if current_task["task_status"] == "done":
                    break

            utils.os_utils.write_pickle_file(self.checkpoint_path, self)

            assert current_task["task_status"] == "done", f"could not finish the task in {max_iter} iterations!!!"


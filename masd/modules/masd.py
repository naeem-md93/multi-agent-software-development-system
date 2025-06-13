import json

from .teacher import TeacherModel
from .. import prompts, utils


class MultiAgentDevelopmentSystem:
    def __init__(self):
        super().__init__()

        self.developer = TeacherModel()
        self.planner = TeacherModel()
        self.coder = TeacherModel()
        self.tester = TeacherModel()
        self.debugger = TeacherModel()

    def develop(self, task_description: str, max_iterations: int = 5) -> None:

        raw_response = self.planner.get_teacher_response(
            system_prompt=prompts.planner.TEACHER_SYSTEM_PROMPT,
            user_prompt=prompts.planner.TEACHER_USER_PROMPT,
            system_prompt_kwargs=None,
            user_prompt_kwargs={"task_description": task_description},
            llm_kwargs={"temperature": 0.7}
        )

        json_response = utils.rag_utils.response_to_json(raw_response)
        print(json_response)
        print("====================================")

        for step in json_response["steps"]:
            step_is_finished = False
            for i in range(max_iterations):
                if step_is_finished:
                    break

                coder_response = self.coder.get_teacher_response(
                    system_prompt=prompts.coder.TEACHER_SYSTEM_PROMPT,
                    user_prompt=prompts.coder.TEACHER_USER_PROMPT,
                    system_prompt_kwargs=None,
                    user_prompt_kwargs={"coder_user_data": {
                        "description": step["description"],
                        "coder_instructions": step["code_student"],
                        "guidelines": json_response["guidelines"]
                    }}
                )

                print(coder_response)
                coder_stdout, coder_stderr = utils.rag_utils.execute_bash_response(coder_response)
                print("====================================")

                tester_response = self.tester.get_teacher_response(
                    system_prompt=prompts.tester.TEACHER_SYSTEM_PROMPT,
                    user_prompt=prompts.tester.TEACHER_USER_PROMPT,
                    system_prompt_kwargs=None,
                    user_prompt_kwargs={"tester_user_data": {
                        "description": step["description"],
                        "tester_instructions": step["test_student"],
                        "code_files": {},
                        "guidelines": json_response["guidelines"]
                    }}
                )

                print(tester_response)
                tester_stdout, tester_stderr = utils.rag_utils.execute_bash_response(tester_response)
                print("======================================")


                exit(1223)

                # debug_response = self.debugger.get_teacher_response()
                #
                # developer_response = self.developer.get_teacher_response()
                #
                # step_is_finished = developer_response["is_finished"]





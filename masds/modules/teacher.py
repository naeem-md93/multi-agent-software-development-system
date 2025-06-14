
from .student import StudentModel
from .. import utils


class TeacherModel:
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_teacher_response(
        system_prompt: str,
        user_prompt: str,
        system_prompt_kwargs: dict | None = None,
        user_prompt_kwargs: dict | None = None,
        llm_kwargs: dict | None = None
    ) -> str:

        raw_response = utils.rag_utils.get_azure_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            system_prompt_kwargs=system_prompt_kwargs,
            user_prompt_kwargs=user_prompt_kwargs,
            llm_kwargs=llm_kwargs,
        )

        return raw_response

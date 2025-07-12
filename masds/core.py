import os

from .graph import build_graph


def init_project(project_dir: str) -> None:
    os.makedirs(project_dir, exist_ok=True)
    os.chdir(os.path.join(os.getcwd(), project_dir))


def build_project(project_dir: str, project_description: str) -> None:
    
    init_project(project_dir)

    executor = build_graph()

    initial_state = {"description": project_description}

    final_state = executor.invoke(initial_state)

    return final_state

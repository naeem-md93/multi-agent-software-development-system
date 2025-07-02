# -----------------------------
# File: devagents/core.py
# -----------------------------
import os
import subprocess

from .graph import build_graph


def build_project(project_dir: str, project_description: str) -> None:
    
    os.makedirs(project_dir, exist_ok=True)
    os.chdir(os.path.join(os.getcwd(), project_dir))
    executor= build_graph()

    initial_state = {"description": project_description}

    final_state = executor.invoke(initial_state)

    return final_state

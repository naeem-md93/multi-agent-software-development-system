import os
import subprocess
from .. import utils


def init_a_project(project_dir: str) -> None:

    os.makedirs(project_dir, exist_ok=True)
    os.chdir(project_dir)
    venv_command = "#!/bin/bash\n\npython3 -m venv .venv\n\nsource .venv/bin/activate"
    utils.os_utils.run_script(venv_command, timeout=30)


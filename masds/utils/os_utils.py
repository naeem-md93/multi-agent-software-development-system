from typing import List, Dict, Any, Tuple
import os
import stat
import hashlib
import tempfile
import subprocess
import pickle as pk


def get_project_dirs_files(project_dir: str, ignore_dirs: List[str], ignore_indexes: List[str]) -> Tuple[List[str], Dict[str, Any]]:

    file_paths = []
    dir_paths = {}

    # 1) Collect all matching file paths
    for root, dirs, files in os.walk(project_dir, topdown=True):
        # skip unwanted directories

        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        dir_files = []
        for filename in files:
            full_path = os.path.join(root, filename)
            _, ext = os.path.splitext(filename)
            if ext in ignore_indexes:
                continue
            file_paths.append(full_path)
            dir_files.append(full_path)

        if root != os.getcwd():
            dir_paths[root] = dir_files + [os.path.join(root, x) for x in dirs]

    dir_paths = sorted(dir_paths.items(), key=lambda x: len(x[0]), reverse=True)
    dir_paths = {x[0]: x[1] for x in dir_paths}

    return file_paths, dir_paths


def write_pickle_file(save_path: str, data: object) -> None:
    """Saves data to a pickle file """

    if os.sep in save_path:
        dir_path, file_name = os.path.split(save_path)
        os.makedirs(dir_path, exist_ok=True)

    with open(save_path, 'wb') as handle:
        pk.dump(data, handle, protocol=pk.HIGHEST_PROTOCOL)


def hash_file_content(content: str) -> str:
    content = content.encode("utf-8")
    content = hashlib.md5(content).hexdigest()

    return content


def read_pickle_file(path: str) -> object:
    """Loads a pickle file """

    with open(path, 'rb') as handle:
        data = pk.load(handle)

    return data


def run_script(script_content: str, timeout: int):
    # Create a temp file for the script
    with tempfile.NamedTemporaryFile(delete=False, suffix='.sh') as tmp:
        tmp.write(script_content.encode())
        tmp_path = tmp.name

    # Make it executable
    os.chmod(tmp_path, os.stat(tmp_path).st_mode | stat.S_IEXEC)

    try:
        # Run script and capture output
        result = subprocess.run(
            [tmp_path],
            input=b'',  # send EOF immediately if script expects input
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        return {
            'stdout': result.stdout.decode(),
            'stderr': result.stderr.decode(),
            'error_type': None
        }
    except subprocess.TimeoutExpired as te:
        return {
            'stdout': te.stdout.decode() if te.stdout else '',
            'stderr': te.stderr.decode() if te.stderr else '',
            'error_type': 'timeout'
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': str(e),
            'error_type': 'execution_error'
        }
    finally:
        # Clean up script file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

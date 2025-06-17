import os
import stat
import tempfile
import subprocess
import pickle as pk


def get_project_files(project_dir: str)-> list[str]:

    file_paths = []
    for root, dirs, files in os.walk(project_dir, topdown=True):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    return file_paths


def write_pickle_file(save_path: str, data: object) -> None:
    """Saves data to a pickle file """

    if os.sep in save_path:
        dir_path, file_name = os.path.split(save_path)
        os.makedirs(dir_path, exist_ok=True)

    with open(save_path, 'wb') as handle:
        pk.dump(data, handle, protocol=pk.HIGHEST_PROTOCOL)


def read_pickle_file(path: str) -> object:
    """Loads a pickle file """

    with open(path, 'rb') as handle:
        data = pk.load(handle)

    return data


def execute_scripts(implementation_script: str, execution_script: str, timeout: int = 30):
    """
    Executes the given implementation and execution bash scripts sequentially,
    captures outputs/errors, and handles potential infinite loops by enforcing a timeout.

    Parameters:
    - implementation_script: str, bash commands to create/modify/delete files.
    - execution_script: str, bash commands to run the implemented functionality.
    - timeout: int, number of seconds to allow for each script before aborting.

    Returns:
    - dict containing:
        * 'implementation': {'stdout', 'stderr', 'error_type' or None}
        * 'execution': {'stdout', 'stderr', 'error_type' or None}
    """
    def _run_script(script_content):
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

    report = {
        'implementation': _run_script(implementation_script),
        'execution': _run_script(execution_script)
    }
    return report
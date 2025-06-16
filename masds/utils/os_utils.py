import os
import stat
import tempfile
import subprocess


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
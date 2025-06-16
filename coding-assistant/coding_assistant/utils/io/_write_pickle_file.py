from typing import Union, List, Dict, Any
import os
import pickle as pk


def write_pickle_file(save_path: str, data: Any) -> None:
    """Saves data to a pickle file """

    if os.sep in save_path:
        dir_path, file_name = os.path.split(save_path)
        os.makedirs(dir_path, exist_ok=True)

    with open(save_path, 'wb') as handle:
        pk.dump(data, handle, protocol=pk.HIGHEST_PROTOCOL)

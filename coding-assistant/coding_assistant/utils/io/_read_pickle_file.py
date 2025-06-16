from typing import Union, List, Dict, Any
import pickle as pk


def read_pickle_file(path: str) -> Any:
    """Loads a pickle file """

    with open(path, 'rb') as handle:
        data = pk.load(handle)

    return data
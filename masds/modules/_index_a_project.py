from typing import List, Dict, Any
import os
import copy
from tqdm import tqdm
from .. import utils, prompts


def index_project_files(project_description: str, project_files: List[str], orig_dataset: Dict[str, Dict[str, Any]], database_path: str) -> Dict[str, Dict[str, Any]]:

    new_database = {}

    # index project files
    t = tqdm(enumerate(project_files))
    for i, fp in t:
        t.set_description_str(f"({i + 1}/{len(project_files)}) - Indexing {fp}")

        try:
            file_content = open(fp, "r").read()
        except Exception as e:
            print(f"{fp=}")
            print(vars(e))
            continue

        if len(file_content) != 0:
            file_hash = utils.os_utils.hash_file_content(file_content)

            if fp in orig_dataset:
                if orig_dataset[fp]["hash"] == file_hash:
                    new_database[fp] = copy.deepcopy(orig_dataset[fp])
                    continue

            new_database[fp] = {
                "path": fp,
                "contents": file_content,
                "hash": file_hash,
                "type": "file",
                "summary": prompts.indexer.get_file_content_summary(
                    user_prompt_kwargs={
                        "project_description": project_description,
                        "file_path": fp,
                        "file_contents": file_content
                    },
                    llm_kwargs={"temperature": 0.5}
                ),
                "last_modified": utils.time_utils.get_now()
            }

            utils.os_utils.write_pickle_file(database_path, new_database)

    return new_database


def index_project_dirs(project_description: str, project_dirs: Dict[str, Any], file_database: Dict[str, Dict[str, Any]], orig_dataset: Dict[str, Dict[str, Any]], database_path: str) -> Dict[str, Dict[str, Any]]:

    dir_database = {}

    t = tqdm(enumerate(list(project_dirs.items())))
    for i, (k, v) in t:
        t.set_description_str(f"({i + 1}/{len(project_dirs)}) - Indexing {k}")

        assert k not in dir_database, f"{k} Already in dir_database"
        dir_hash = []
        dir_summaries = []
        for x in v:
            if x in file_database:
                dir_hash.append(file_database[x]["hash"])
                dir_summaries.append({"path": x, "type": "file", "summary": file_database[x]["summary"]})
            else:
                assert x in dir_database, f"{x} not in dir_database"
                dir_hash += dir_database[x]["hash"]
                dir_summaries.append({"path": x, "type": "dir", "summary": dir_database[x]["summary"]})

        if k in orig_dataset:
            if orig_dataset[k]["hash"] == dir_hash:
                dir_database[k] = copy.deepcopy(orig_dataset[k])
                continue

        text = "\n----------\n"
        counter = 1
        for x in dir_summaries:
            if x["type"] == "dir":
                text += f"Directory {counter} Path: {x['path']}\n"
                text += f"Directory {counter} Content Summary: {x['summary']}\n"
                text += "----------\n"
                counter += 1

        counter = 1
        for x in dir_summaries:
            if x["type"] == "file":
                text += f"File {counter} Path: {x}\n"
                text += f"File {counter} Content Summary: {x['summary']}\n"
                text += "----------\n"
                counter += 1

        dir_database[k] = {
            "path": k,
            "contents": f"List of files and directories in this directory:\n{v}",
            "hash": dir_hash,
            "type": "directory",
            "summary": prompts.indexer.get_dir_content_summary(
                    user_prompt_kwargs={
                        "project_description": project_description,
                        "directory_path": k,
                        "directory_summary": text
                    },
                    llm_kwargs={"temperature": 0.5}
                ),
                "last_modified": utils.time_utils.get_now()
        }

    return dir_database

def index_a_project(project_description: str, project_files: List[str], project_dirs: Dict[str, Any], orig_dataset: Dict[str, Dict[str, Any]], database_path: str) -> Dict[str, Dict[str, Any]]:

    db_dir = os.sep.join(database_path.split(os.sep)[:-1])

    file_db_path = os.path.join(db_dir, "file_db.pk")
    file_database = index_project_files(project_description, project_files, orig_dataset, file_db_path)

    dir_db_path = os.path.join(db_dir, "dir_db.pk")
    dir_database = index_project_dirs(project_description, project_dirs, file_database, orig_dataset, dir_db_path)

    new_database = {}
    new_database.update(file_database)
    new_database.update(dir_database)

    return new_database

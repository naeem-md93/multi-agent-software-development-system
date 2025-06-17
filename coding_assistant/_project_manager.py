import os
import json
from tqdm import tqdm
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from .llm import LLM
from . import utils
from .modules import DictIndexer
from .modules import TextIndexer
from .modules import FileManager


load_dotenv()


class ProjectManager:
    def __init__(
        self,
        llm_backend: str = "together.ai",
        llm_model_name: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        checkpoints_path: str = "./.assistant_data",
        project_path: str = "./",
        include_extensions: tuple[str] = (".py", ),
        ignore_dirs: tuple[str] = (
            ".assistant_data",
            ".idea",
            ".venv",
            ".git",
            ".vscode",
            "__pycache__",
            "coding_assistant/prompts"
        ),
    ) -> None:
        
        self.checkpoint_path = checkpoints_path
        self.project_path = project_path
        self.include_extensions = include_extensions
        self.ignore_dirs = ignore_dirs
        
        self.file_level_db = DictIndexer(self.checkpoint_path, "file_level_db.pk")
        self.project_level_db = DictIndexer(self.checkpoint_path, "project_level_db.pk")
        self.summary_indexer = TextIndexer("./", "README.md")
        self.history = TextIndexer(self.checkpoint_path, "conversation_history.md")
       
        self.llm = LLM(api_backend=llm_backend, model_name=llm_model_name)
        self.embedding_model = SentenceTransformer(embedding_model_name)

    def remove_old_project_indexes(self, project_files: list[str]) -> None:

        for key in list(self.file_level_db.get_content().keys()):
            if key not in project_files:
                self.file_level_db.remove_data(key)

    def is_project_file_need_indexing(self, file_path: str) -> bool:

        file_content = utils.read_text_file(file_path)

        # checking if the file is empty
        if len(file_content) < 10:
            return False

        # checking if the file content is modified
        file_hash = utils.hash_file_content(file_content)

        if self.file_level_db.is_key_exists(file_path):
            if file_hash == self.file_level_db.get_data(file_path)["hash"]:
                need_indexing = False
            else:
                need_indexing = True
        else:
            need_indexing = True

        assert need_indexing is not None, f"{need_indexing=}"

        return need_indexing


    def get_file_obj_from_path(self, file_path: str) -> FileManager:

        file_obj = FileManager(file_path)
        file_obj.entities = utils.rag.get_entities(self.llm, self.embedding_model, file_obj.content)

        return file_obj


    def index_a_file(self, file_obj: FileManager) -> None:

        self.file_level_db.add_data(file_obj.path, {

            "path": file_obj.path,
            "name": file_obj.name,
            "ext": file_obj.ext,
            "content": file_obj.content,
            "hash": file_obj.hash,
            "entities": file_obj.entities,
            "last_modified": utils.get_now(),
        })

        self.file_level_db.write_content()

    def run(self):

        while True:
            project_files = utils.get_project_files(self.project_path, self.include_extensions, self.ignore_dirs)
            self.remove_old_project_indexes(project_files)

            t = tqdm(project_files)
            for i, file_path in enumerate(t):
                t.set_description_str(f"({i+1}/{len(project_files)}) - {file_path}")

                need_indexing = self.is_project_file_need_indexing(file_path)
                if need_indexing:
                    file_obj = self.get_file_obj_from_path(file_path)
                    self.index_a_file(file_obj)


            description = utils.rag.get_project_description(self.llm, list(self.file_level_db.get_content().values()))
            self.summary_indexer.update_content(description)
            self.summary_indexer.write_content()

            user_input = input("Enter your request (or 'q' to quit): ")
            if user_input == "q":
                break

            query_embedding = self.embedding_model.encode([user_input])
            relevant_data = utils.rag.retrieve_relevant_data(query_embedding, self.project_indexer.get_content(), topk=20)
            suggestions = utils.rag.respond_user(self.llm, user_input, self.summary_indexer.get_content(), relevant_data)

            sep = "\n***\n"
            txt = f"# Q: {user_input}{sep}# A:\n{suggestions}"
            self.history.append_content(txt, sep)
            self.history.write_content()

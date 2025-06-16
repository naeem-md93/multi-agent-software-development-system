from coding_assistant import ProjectManager

if __name__ == '__main__':

    # together.ai : [
    #   black-forest-labs/FLUX.1-schnell-Free,
    #   meta-llama/Llama-3.3-70B-Instruct-Turbo-Free,
    #   meta-llama/Llama-Vision-Free,
    #   lgai/exaone-3-5-32b-instruct,
    #   lgai/exaone-deep-32b,
    # ]

    # novita.ai : qwen/qwen2.5-7b-instruct
    
    runner = ProjectManager(
        llm_backend="together.ai",
        llm_model_name="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
        checkpoints_path="./.assistant_data",
        project_path="./coding_assistant",
        include_extensions=(".py", ),
        ignore_dirs=(
            ".assistant_data",
            ".idea",
            ".venv",
            ".git",
            ".vscode",
            "__pycache__",
        )
    )
    runner.run()

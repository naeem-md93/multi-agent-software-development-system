from masds.modules.masds import MultiAgentSoftwareDevelopmentSystem


def main():
    print("Multi-Agent Software Development System")
    print("=" * 50)

    project_dir = "coding_assistant"
    project_description = """
    I want you to write an AI based Coding assistant using Python.
    I want it to index every file (with the best strategy that you can think of) in the project so it understands the whole project.
    Also, I want it to request input from user for new features to implement, suggest fix for bugs and new features and improvements.
    your implementations should be compatible with the current codes.
    """

    system = MultiAgentSoftwareDevelopmentSystem()
    system.develop_a_project(project_dir=project_dir, project_description=project_description)


if __name__ == "__main__":
    main()
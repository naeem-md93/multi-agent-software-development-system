from masds import build_project



if __name__ == "__main__":

    project_description = """
    Write an AI-based coding assistant that has an understanding of the whole project and can wrire code, fix bugs, and suggest new features
    """

    build_project("calculator", project_description)

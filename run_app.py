from masds import build_project



if __name__ == "__main__":

    project_description = """
    Write an AI-based coding assistant that has an understanding of the whole project and can write code, fix bugs, and suggest new features. It ment to be used by senior software engineers. It should Support Python and JavaScript. It should use Azure OpenAI models.
    """

    build_project("calculator", project_description)

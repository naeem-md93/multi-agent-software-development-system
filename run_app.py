from masds import build_project



if __name__ == "__main__":

    project_description = """
    Write an AI-based coding assistant that has an understanding of the whole project and can write code, fix bugs, and suggest new features.
    It ment to be used by senior software engineers.
    It should Support Python and JavaScript.
    Do not train a model from scratch. Instead, try to use Azure OpenAI models. mark 'is_clear' as true and fill all the missing information with whatever you think is the best.
    """

    build_project("calculator", project_description)

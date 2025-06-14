from masds import MultiAgentDevelopmentSystem


def main():
    print("Multi-Agent Software Development System")
    print("=" * 50)

    project_name = "simple_calculator"
    project_description = """
    The purpose of this project is to develop a simple command-line calculator using Python that can perform basic arithmetic operations such as addition, subtraction, multiplication, and division. This tool will be used for educational purposes or lightweight local calculations.
    The calculator will be a terminal-based Python application that accepts user input for two numbers and an operation, then displays the result. It will support:
    - Addition (+)
    - Subtraction (-)
    - Multiplication (*)
    - Division (/)
    """

    system = MultiAgentDevelopmentSystem()
    system.develop(project_name=project_name, project_description=project_description)


if __name__ == "__main__":
    main()
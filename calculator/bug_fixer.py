import os
import openai

# Configuration: Use environment variables for sensitive data
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

def detect_and_fix_bugs(code):
    """Detect bugs in the provided code snippet, explain issues, and suggest fixes."""
    try:
        response = openai.ChatCompletion.create(
            engine="code-davinci-002",  # Replace with your engine name
            messages=[{
                "role": "system", "content": "You are a coding assistant specializing in bug detection and fixes."
            }, {
                "role": "user", "content": f"Analyze the following code for bugs, provide an explanation for each issue, and suggest fixes:\n{code}"
            }]
        )
        # Extract the reply text
        analysis = response[\'choices\'][0][\'message\'][\'content\']
        # Write the analysis to a file
        with open('bug_analysis.txt', 'w') as analysis_file:
            analysis_file.write(analysis)
        print("Bug analysis and fixes written to bug_analysis.txt")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == '__main__':
    sample_code = "def hello_world():\n    print(\'Hello, world!\'"
    detect_and_fix_bugs(sample_code)

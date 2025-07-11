import os
import openai
import glob

# Configuration: Use environment variables for sensitive data
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

def analyze_codebase(directory):
    """Analyze the entire codebase to provide contextual insights."""
    try:
        # Collect all code files in the directory (e.g., .py and .js files)
        file_paths = glob.glob(f"{directory}/**/*.*", recursive=True)
        relevant_files = [f for f in file_paths if f.endswith(('.py', '.js'))]
        codebase_content = ''
        for file_path in relevant_files:
            with open(file_path, 'r') as file:
                codebase_content += f'\n\n# File: {file_path}\n' + file.read()
        # Send the aggregated code to the OpenAI API for analysis
        response = openai.ChatCompletion.create(
            engine="code-davinci-002",  # Replace with your engine name
            messages=[{
                "role": "system", "content": "You are an assistant that provides codebase-wide insights for software development."
            }, {
                "role": "user", "content": f"Analyze the following codebase files and provide recommendations:\n{codebase_content}"
            }]
        )
        # Extract the reply text
        analysis_results = response['choices'][0]['message']['content']
        # Save the analysis to a file
        with open('codebase_insights.txt', 'w') as insights_file:
            insights_file.write(analysis_results)
        print("Codebase insights saved to codebase_insights.txt")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == '__main__':
    project_directory = '.'  # Analyze the current directory
    analyze_codebase(project_directory)

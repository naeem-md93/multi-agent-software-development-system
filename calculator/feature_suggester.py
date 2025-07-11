import os
import openai

# Configuration: Use environment variables for sensitive data
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

def suggest_features(project_context):
    """Analyze the project context and recommend innovative or necessary features."""
    try:
        response = openai.ChatCompletion.create(
            engine="code-davinci-002",  # Replace with your engine name
            messages=[{
                "role": "system", "content": "You are a coding assistant specializing in feature suggestions based on project context."
            }, {
                "role": "user", "content": f"Analyze the following project context and suggest features with reasoning:\n{project_context}"
            }]
        )
        # Extract the reply text
        suggestions = response['choices'][0]['message']['content']
        # Write the suggestions to a file
        with open('feature_suggestions.txt', 'w') as suggestions_file:
            suggestions_file.write(suggestions)
        print("Feature suggestions written to feature_suggestions.txt")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == '__main__':
    project_description = "A web-based project management tool designed to help teams collaborate effectively."
    suggest_features(project_description)

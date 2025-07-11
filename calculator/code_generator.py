import os
import openai

# Configuration: Use environment variables for sensitive data
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

def generate_code(prompt, language):
    """Generate code snippets based on the input prompt and language.
    prompt: User's text input describing the required code.
    language: Target programming language ('python' or 'javascript')."""
    try:
        response = openai.ChatCompletion.create(
            engine="code-davinci-002",  # Replace with your engine name
            messages=[{
                "role": "system", "content": "You are a helpful AI coding assistant."
            }, {
                "role": "user", "content": f"Generate a {language} code snippet for: {prompt}"
            }]
        )
        # Extract the reply text
        generated_code = response['choices'][0]['message']['content']
        # Save the generated code to an appropriate file
        filename = f'generated_code.{language}'
        with open(filename, 'w') as code_file:
            code_file.write(generated_code)
        print(f"Code successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == '__main__':
    user_prompt = "Create a simple HTTP server"
    target_language = "python"
    generate_code(user_prompt, target_language)

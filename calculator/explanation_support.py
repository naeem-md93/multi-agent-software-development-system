import os
import openai

# Configuration: Use environment variables for sensitive data
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

def explain_output(content_type, content):
    """Provide a concise explanation for the provided code outputs, bug analyses, or feature suggestions."""
    try:
        input_prompt = f"Provide a detailed and clear explanation for the following {content_type}:\n{content}"
        response = openai.ChatCompletion.create(
            engine="code-davinci-002",  # Replace with your engine name
            messages=[{
                "role": "system", "content": "You are an assistant specialized in providing concise explanations to improve software engineer trust and usability."
            }, {
                "role": "user", "content": input_prompt
            }]
        )
        # Extract the reply text
        explanation = response["choices"][0]["message"]["content"]
        # Save the explanation to a file
        with open('explanations.txt', 'w') as explanation_file:
            explanation_file.write(explanation)
        print("Explanation successfully saved to explanations.txt")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == '__main__':
    content_type = "bug analysis"
    content = "This function has a missing return statement."
    explain_output(content_type, content)

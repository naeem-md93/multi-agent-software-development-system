import os
import openai
import json
from contextual_codebase_analysis import analyze_codebase
from feature_suggester import suggest_features

# Configuration: Use environment variables for sensitive data
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

def integrate_features(directory):
    """Combine codebase analysis and feature suggestions into a single process."""
    try:
        print('Analyzing codebase...')
        insights = analyze_codebase(directory)
        print('Suggesting features...')
        features = suggest_features(insights)
        # Save results to JSON file
        output = {"insights": insights, "features": features}
        with open('advanced_features_output.json', 'w') as f:
            json.dump(output, f, indent=4)
        print('Advanced features output saved to advanced_features_output.json')
    except Exception as e:
        print(f'An error occurred: {e}')

# Example usage
if __name__ == '__main__':
    project_directory = '.'  # Analyze the current project directory
    integrate_features(project_directory)

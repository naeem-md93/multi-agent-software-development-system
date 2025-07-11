import azure_openai_config as config
import openai

# Apply OpenAI configuration
openai.api_key = config.OPENAI_API_KEY
openai.api_base = config.OPENAI_API_BASE
openai.api_type = config.OPENAI_API_TYPE
openai.api_version = config.OPENAI_API_VERSION

def test_openai_connection():
    try:
        response = openai.ChatCompletion.create(
            engine='code-davinci-002',
            messages=[{
                'role': 'system', 'content': 'Test if Azure OpenAI service is reachable.'
            }, {
                'role': 'user', 'content': 'Hello, AI!'
            }]
        )
        print('Response from Azure OpenAI:', response)
    except Exception as e:
        print('Error connecting to Azure OpenAI:', e)

if __name__ == '__main__':
    test_openai_connection()

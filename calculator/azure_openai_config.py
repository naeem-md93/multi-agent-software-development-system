import os

# Configuration for Azure OpenAI
OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('AZURE_OPENAI_API_BASE')
OPENAI_API_TYPE = 'azure'
OPENAI_API_VERSION = '2023-03-15-preview'

def get_openai_config():
    return {
        'api_key': OPENAI_API_KEY,
        'api_base': OPENAI_API_BASE,
        'api_type': OPENAI_API_TYPE,
        'api_version': OPENAI_API_VERSION
    }

if __name__ == '__main__':
    print('Azure OpenAI Configuration:', get_openai_config())

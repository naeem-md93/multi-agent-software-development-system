import os
import dotenv
import logging
from langchain_openai import AzureChatOpenAI

dotenv.load_dotenv()


LLM = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model=os.getenv("AZURE_OPENAI_MODEL_NAME")
)

# Configure logging to show debug messages from all devagents modules
logging.basicConfig(
    level=logging.INFO,  # Use DEBUG for more verbosity
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

LOGGER = logging.getLogger(__name__)

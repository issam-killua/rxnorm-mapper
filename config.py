import os
from dotenv import load_dotenv

# Try to load .env file, but don't fail if it doesn't work
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

class Config:
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4"
    OPENAI_TEMPERATURE = 0.2
    OPENAI_MAX_TOKENS = 800
    
    # Mistral API settings
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    MISTRAL_MODEL = "mistral-large-latest"
    MISTRAL_TEMPERATURE = 0.1
    MISTRAL_MAX_TOKENS = 500
    
    # RxNorm API settings
    RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    
    # Processing settings
    BATCH_SIZE = 10
    RATE_LIMIT_DELAY = 1
    OUTPUT_DIR = "output"
    
    # Data settings
    INPUT_FILE = "refdesmedicamentscnops.xlsx"
import os
from dotenv import load_dotenv

# Try to load .env file, but don't fail if it doesn't work
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Validate API key is loaded
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found. Please check your .env file or environment variables.")
    
    RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    BATCH_SIZE = 10
    RATE_LIMIT_DELAY = 1
    OUTPUT_DIR = "output"
    INPUT_FILE = "refdesmedicamentscnops.xlsx"
    
    OPENAI_MODEL = "gpt-4"
    OPENAI_TEMPERATURE = 0.2
    OPENAI_MAX_TOKENS = 800
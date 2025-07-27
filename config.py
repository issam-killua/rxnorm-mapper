import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = "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"
    RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    BATCH_SIZE = 10
    RATE_LIMIT_DELAY = 1  # seconds between API calls
    OUTPUT_DIR = "output"
    INPUT_FILE = "refdesmedicamentscnops.xlsx"
    
    # Prompt engineering settings
    OPENAI_MODEL = "gpt-4"
    OPENAI_TEMPERATURE = 0.2
    OPENAI_MAX_TOKENS = 800

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
    MISTRAL_MODEL = "mistral-large-latest"  # Use latest model available
    MISTRAL_TEMPERATURE = 0.1  # Low temperature for consistent translations
    MISTRAL_MAX_TOKENS = 100   # Reduced max tokens for translation tasks
    
    # RxNorm API settings
    RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    
    # Processing settings
    BATCH_SIZE = 50            # Increased batch size from 10 to 50
    RATE_LIMIT_DELAY = 0       # No delay between API calls
    MAX_WORKERS = 10           # Number of parallel workers for ThreadPoolExecutor
    OUTPUT_DIR = "output"
    
    # Translation Batch Settings
    TRANSLATION_BATCH_SIZE = 20 # Number of terms to translate in a single Mistral API call
    
    # Performance settings
    RXNORM_TIMEOUT = 3         # Reduced timeout for RxNorm API calls (seconds)
    MISTRAL_TIMEOUT = 10       # Timeout for Mistral API calls (seconds)
    
    # Data settings
    INPUT_FILE = "refdesmedicamentscnops.xlsx"
    
    # Form Column Translation Map - Common pharmaceutical forms (French → English)
    FORM_TRANSLATIONS = {
        "COMPRIME": "TABLET",
        "GELULE": "CAPSULE",
        "SOLUTION BUVABLE": "ORAL SOLUTION",
        "SOLUTION INJECTABLE": "INJECTION",
        "SOLUTION POUR PERFUSION": "INFUSION SOLUTION",
        "SOLUTION POUR IRRIGATION": "IRRIGATION SOLUTION",
        "POUDRE POUR SUSPENSION BUVABLE": "POWDER FOR ORAL SUSPENSION",
        "SUPPOSITOIRE": "SUPPOSITORY",
        "COMPRIME PELLICULE": "FILM-COATED TABLET",
        "COMPRIME ENROBE": "COATED TABLET",
        "COMPRIME DISPERSIBLE": "DISPERSIBLE TABLET",
        "COMPRIME SECABLE": "SCORED TABLET",
        "COMPRIME GASTRO-RESISTANT": "ENTERIC COATED TABLET",
        "GELULE GASTRO-RESISTANTE": "ENTERIC COATED CAPSULE",
        "POUDRE POUR SOLUTION INJECTABLE": "POWDER FOR INJECTION",
        "POMMADE": "OINTMENT"
    }
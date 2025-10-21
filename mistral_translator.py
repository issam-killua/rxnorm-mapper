import requests
import json
from typing import Dict, List, Optional
import time
from config import Config

class MistralTranslator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.form_translation_cache = {}  # Cache for pharmaceutical form translations
        self.presentation_translation_cache = {}  # Cache for presentation translations
        
        # Initialize cache with common forms from config
        for french, english in Config.FORM_TRANSLATIONS.items():
            self.form_translation_cache[french.upper()] = english
    
    def translate_terms_batch(self, terms: List[str], term_type: str = "pharmaceutical") -> Dict[str, str]:
        """Translate a batch of terms from French to English"""
        if not terms:
            return {}
            
        # Remove duplicates and empty terms
        unique_terms = list(set([t for t in terms if t and t.strip()]))
        
        # Check which terms need translation (not in cache)
        cache = self.form_translation_cache if term_type == "form" else self.presentation_translation_cache
        terms_to_translate = [t for t in unique_terms if t.upper() not in cache]
        
        if not terms_to_translate:
            # All terms are in cache, return cached translations
            return {t: cache.get(t.upper(), t) for t in unique_terms}
            
        try:
            # Prepare batch translation prompt
            terms_list = "\n".join([f"{i+1}. {term}" for i, term in enumerate(terms_to_translate)])
            
            prompt = f"""Translate these {term_type} terms from French to standardized English pharmaceutical terminology.
Respond ONLY with a JSON object mapping each French term to its English equivalent.

Terms to translate:
{terms_list}

Example response format:
{{
  "COMPRIME": "TABLET",
  "GELULE": "CAPSULE"
}}
"""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": Config.MISTRAL_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a professional pharmaceutical translator that responds only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": Config.MISTRAL_TEMPERATURE,
                "max_tokens": Config.MISTRAL_MAX_TOKENS,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=payload, 
                timeout=Config.MISTRAL_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON response
            translations = json.loads(content)
            
            # Update cache with new translations
            for french, english in translations.items():
                cache[french.upper()] = english.upper()
            
            # Return translations for all requested terms
            all_translations = {}
            for term in unique_terms:
                if term.upper() in cache:
                    all_translations[term] = cache[term.upper()]
                else:
                    # If translation failed, use original term
                    all_translations[term] = term
                    
            return all_translations
                
        except Exception as e:
            print(f"Batch translation error: {str(e)}")
            # Return original terms if translation failed
            return {t: t for t in unique_terms}
    
    def translate_product_forms(self, products: List[Dict]) -> List[Dict]:
        """Translate form field for a batch of products"""
        # Extract all unique forms
        all_forms = [p.get('form', '') for p in products if p.get('form')]
        
        # Batch translate all forms
        form_translations = self.translate_terms_batch(all_forms, "form")
        
        # Extract all unique presentations
        all_presentations = [p.get('presentation', '') for p in products if p.get('presentation')]
        
        # Batch translate all presentations
        presentation_translations = self.translate_terms_batch(all_presentations, "presentation")
        
        # Update products with translations
        translated_products = []
        for product in products:
            translated = product.copy()
            
            # Add form translation if available
            form = product.get('form', '')
            if form:
                translated['form_standardized'] = form_translations.get(form, form)
            
            # Add presentation translation if available
            presentation = product.get('presentation', '')
            if presentation:
                translated['presentation_english'] = presentation_translations.get(presentation, presentation)
            
            translated_products.append(translated)
        
        return translated_products
    
    def translate_product(self, product_context: Dict) -> Dict:
        """Translate a single product's form and presentation"""
        # Create a list with just this product
        products = [product_context]
        
        # Use batch translation method
        translated_products = self.translate_product_forms(products)
        
        # Return the translated product
        if translated_products:
            return translated_products[0]
        else:
            return product_context  # Return original if translation failed
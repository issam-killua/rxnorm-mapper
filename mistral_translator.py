import requests
import json
from typing import Dict, List, Optional
from config import Config

class MistralTranslator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        
    def translate_product(self, product_context: Dict) -> Dict:
        """Translate product information from French/Arabic to English"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = self._create_translation_prompt(product_context)
        
        payload = {
            "model": Config.MISTRAL_MODEL,
            "messages": [
                {"role": "system", "content": "You are a professional pharmaceutical translator. Translate the following medical product information from French/Arabic to English."},
                {"role": "user", "content": prompt}
            ],
            "temperature": Config.MISTRAL_TEMPERATURE,
            "max_tokens": Config.MISTRAL_MAX_TOKENS
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse the translated content
            translated_data = self._parse_translation_response(content, product_context)
            return translated_data
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return product_context  # Return original context if translation fails
    
    def _create_translation_prompt(self, product_context: Dict) -> str:
        """Create a prompt for translation"""
        
        prompt = f"""Translate the following pharmaceutical product information from French/Arabic to standardized English terminology:

Product Name: {product_context['product_name']}
Active Ingredient (DCI): {product_context['active_ingredient']}
Dosage: {product_context['dosage']} {product_context['dosage_unit']}
Pharmaceutical Form: {product_context['form']}
Presentation: {product_context['presentation']}

Respond with a JSON structure containing these translated fields:
- product_name_english
- active_ingredient_english
- dosage_standardized (with units in standardized format)
- form_standardized
- presentation_english
"""
        return prompt
    
    def _parse_translation_response(self, content: str, original_context: Dict) -> Dict:
        """Parse the translation response from Mistral"""
        try:
            # Clean up the response to ensure it's valid JSON
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            translated = json.loads(content)
            
            # Merge with original context
            result = original_context.copy()
            result['product_name_english'] = translated.get('product_name_english', '')
            result['active_ingredient_english'] = translated.get('active_ingredient_english', '')
            result['dosage_standardized'] = translated.get('dosage_standardized', '')
            result['form_standardized'] = translated.get('form_standardized', '')
            result['presentation_english'] = translated.get('presentation_english', '')
            
            return result
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract information through other means
            result = original_context.copy()
            lines = content.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    if 'product_name' in key:
                        result['product_name_english'] = value
                    elif 'active' in key or 'ingredient' in key:
                        result['active_ingredient_english'] = value
                    elif 'dosage' in key:
                        result['dosage_standardized'] = value
                    elif 'form' in key:
                        result['form_standardized'] = value
                    elif 'presentation' in key:
                        result['presentation_english'] = value
            
            return result
        except Exception as e:
            print(f"Error parsing translation: {str(e)}")
            return original_context
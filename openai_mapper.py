import openai
import json
import time
from typing import Dict, Optional
from config import Config
from prompt_engineer import PromptEngineer

class OpenAIMapper:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.prompt_engineer = PromptEngineer()
    
    def map_product(self, product_context: Dict) -> Optional[Dict]:
        """Map a single product using OpenAI"""
        try:
            prompt = self.prompt_engineer.create_mapping_prompt(product_context)
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a pharmaceutical expert specializing in RxNorm mapping. Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.OPENAI_TEMPERATURE,
                max_tokens=Config.OPENAI_MAX_TOKENS
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure it's valid JSON
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # Add metadata
            result['openai_response_raw'] = content
            result['tokens_used'] = response.usage.total_tokens
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {
                'primary_rxnorm_concept': None,
                'confidence_score': 0,
                'error': f"JSON parsing failed: {str(e)}",
                'openai_response_raw': content if 'content' in locals() else 'No response'
            }
        except Exception as e:
            print(f"OpenAI mapping error: {e}")
            return {
                'primary_rxnorm_concept': None,
                'confidence_score': 0,
                'error': str(e)
            }

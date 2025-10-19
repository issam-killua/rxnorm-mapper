import time
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from config import Config
from data_processor import DataProcessor
from mistral_translator import MistralTranslator
from direct_rxnorm_mapper import DirectRxNormMapper
from openai_mapper import OpenAIMapper
from rxnorm_validator import RxNormValidator

class HybridMappingEngine:
    def __init__(self, openai_api_key: str = None, mistral_api_key: str = None):
        # Initialize with available API keys
        self.mistral_api_key = mistral_api_key
        self.openai_api_key = openai_api_key
        
        # Initialize components based on available keys
        if mistral_api_key:
            self.translator = MistralTranslator(mistral_api_key)
            self.direct_mapper = DirectRxNormMapper()
        
        # Initialize OpenAI components only if key is provided
        if openai_api_key:
            self.ai_mapper = OpenAIMapper(openai_api_key)
        else:
            self.ai_mapper = None
            
        # Always initialize RxNorm validator (no API key needed)
        self.rxnorm_validator = RxNormValidator()
        
        # Connect components if available
        if hasattr(self, 'direct_mapper'):
            self.direct_mapper.set_validator(self.rxnorm_validator)
        
        # Results storage
        self.results = []
    
    def process_single_product(self, product_row: pd.Series, index: int) -> Dict:
        """Process a single product through the hybrid mapping pipeline"""
        
        # Ensure we have necessary components
        if not hasattr(self, 'translator') or not hasattr(self, 'direct_mapper'):
            raise ValueError("Mistral API key is required for hybrid processing")
        
        if not self.ai_mapper:
            raise ValueError("OpenAI API key is required for hybrid processing with fallback")
        
        # Prepare product context
        data_processor = DataProcessor("")
        product_context = data_processor.prepare_product_context(product_row)
        
        result = {
            'index': index,
            'original_data': product_context,
            'timestamp': pd.Timestamp.now(),
            'processing_status': 'started'
        }
        
        try:
            # Step 1: Translation with Mistral API
            print(f"Translating: {product_context['product_name']}")
            translated_product = self.translator.translate_product(product_context)
            result['translation'] = {
                'product_name_english': translated_product.get('product_name_english', ''),
                'active_ingredient_english': translated_product.get('active_ingredient_english', ''),
                'dosage_standardized': translated_product.get('dosage_standardized', ''),
                'form_standardized': translated_product.get('form_standardized', '')
            }
            result['processing_status'] = 'translated'
            
            # Step 2: Direct RxNorm Mapping
            print(f"Direct mapping: {translated_product.get('active_ingredient_english', '')}")
            direct_result = self.direct_mapper.map_product(translated_product)
            
            if direct_result.get('found'):
                # Direct mapping successful
                result['rxnorm_validation'] = direct_result
                result['final_status'] = 'success'
                result['mapping_method'] = 'direct'
                result['needs_review'] = False
                result['processing_status'] = 'completed'
                return result
            
            # Step 3: Fallback to OpenAI + RxNorm API approach
            print(f"Falling back to OpenAI for: {product_context['product_name']}")
            ai_result = self.ai_mapper.map_product(product_context)
            result['ai_mapping'] = ai_result
            result['processing_status'] = 'ai_completed'
            
            if ai_result and ai_result.get('primary_rxnorm_concept'):
                # Validate with RxNorm API
                concepts_to_try = [ai_result['primary_rxnorm_concept']]
                if ai_result.get('alternative_concepts'):
                    concepts_to_try.extend(ai_result['alternative_concepts'])
                
                rxnorm_result = self.rxnorm_validator.validate_multiple_concepts(concepts_to_try)
                result['rxnorm_validation'] = rxnorm_result
                result['mapping_method'] = 'openai'
                result['processing_status'] = 'completed'
                
                # Determine final status
                if rxnorm_result.get('found'):
                    result['final_status'] = 'success'
                    result['needs_review'] = ai_result.get('confidence_score', 0) < 7
                else:
                    result['final_status'] = 'failed'
                    result['needs_review'] = True
            else:
                result['final_status'] = 'failed'
                result['needs_review'] = True
                result['rxnorm_validation'] = {'found': False, 'error': 'Both mapping methods failed'}
            
        except Exception as e:
            result['final_status'] = 'error'
            result['error'] = str(e)
            result['processing_status'] = 'error'
            result['needs_review'] = True
            print(f"Error processing product {index}: {str(e)}")
        
        return result
    
    def process_with_mistral_only(self, product_row: pd.Series, index: int) -> Dict:
        """Process a product using only Mistral translation and direct mapping"""
        
        # Ensure we have necessary components
        if not hasattr(self, 'translator') or not hasattr(self, 'direct_mapper'):
            raise ValueError("Mistral API key is required for Mistral-only processing")
        
        # Prepare product context
        data_processor = DataProcessor("")
        product_context = data_processor.prepare_product_context(product_row)
        
        result = {
            'index': index,
            'original_data': product_context,
            'timestamp': pd.Timestamp.now(),
            'processing_status': 'started'
        }
        
        try:
            # Step 1: Translation with Mistral API
            print(f"Translating: {product_context['product_name']}")
            translated_product = self.translator.translate_product(product_context)
            result['translation'] = {
                'product_name_english': translated_product.get('product_name_english', ''),
                'active_ingredient_english': translated_product.get('active_ingredient_english', ''),
                'dosage_standardized': translated_product.get('dosage_standardized', ''),
                'form_standardized': translated_product.get('form_standardized', '')
            }
            result['processing_status'] = 'translated'
            
            # Step 2: Direct RxNorm Mapping
            print(f"Direct mapping: {translated_product.get('active_ingredient_english', '')}")
            direct_result = self.direct_mapper.map_product(translated_product)
            
            if direct_result.get('found'):
                # Direct mapping successful
                result['rxnorm_validation'] = direct_result
                result['final_status'] = 'success'
                result['mapping_method'] = 'direct'
                result['needs_review'] = False
                result['processing_status'] = 'completed'
            else:
                # Direct mapping failed - no fallback
                result['rxnorm_validation'] = direct_result
                result['final_status'] = 'failed'
                result['mapping_method'] = 'direct'
                result['needs_review'] = True
                result['processing_status'] = 'completed'
                result['error'] = direct_result.get('error', 'Direct mapping failed')
        
        except Exception as e:
            result['final_status'] = 'error'
            result['error'] = str(e)
            result['processing_status'] = 'error'
            result['needs_review'] = True
            print(f"Error processing product {index}: {str(e)}")
        
        return result
    
    def process_batch(self, products_df: pd.DataFrame, start_idx: int = 0, batch_size: int = None) -> List[Dict]:
        """Process a batch of products with hybrid approach (Mistral + OpenAI fallback)"""
        if batch_size is None:
            batch_size = Config.BATCH_SIZE
        
        end_idx = min(start_idx + batch_size, len(products_df))
        batch_results = []
        
        print(f"Processing batch: {start_idx} to {end_idx}")
        
        for idx in range(start_idx, end_idx):
            try:
                result = self.process_single_product(products_df.iloc[idx], idx)
                batch_results.append(result)
                self.results.append(result)
                
                # Rate limiting
                time.sleep(Config.RATE_LIMIT_DELAY)
                
            except Exception as e:
                print(f"Error in batch processing at index {idx}: {e}")
        
        return batch_results
    
    def process_batch_mistral_only(self, products_df: pd.DataFrame, start_idx: int = 0, batch_size: int = None) -> List[Dict]:
        """Process a batch of products with Mistral only (no OpenAI fallback)"""
        if batch_size is None:
            batch_size = Config.BATCH_SIZE
        
        end_idx = min(start_idx + batch_size, len(products_df))
        batch_results = []
        
        print(f"Processing batch with Mistral only: {start_idx} to {end_idx}")
        
        for idx in range(start_idx, end_idx):
            try:
                result = self.process_with_mistral_only(products_df.iloc[idx], idx)
                batch_results.append(result)
                self.results.append(result)
                
                # Rate limiting
                time.sleep(Config.RATE_LIMIT_DELAY)
                
            except Exception as e:
                print(f"Error in batch processing at index {idx}: {e}")
        
        return batch_results
    
    def get_statistics(self) -> Dict:
        """Calculate processing statistics"""
        if not self.results:
            return {}
        
        total = len(self.results)
        successful = len([r for r in self.results if r.get('final_status') == 'success'])
        failed = len([r for r in self.results if r.get('final_status') in ['failed', 'error']])
        needs_review = len([r for r in self.results if r.get('needs_review', False)])
        
        # Method statistics
        direct_method = len([r for r in self.results if r.get('mapping_method') == 'direct'])
        openai_method = len([r for r in self.results if r.get('mapping_method') == 'openai'])
        
        return {
            'total_processed': total,
            'successful_mappings': successful,
            'failed_mappings': failed,
            'needs_manual_review': needs_review,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'review_rate': (needs_review / total * 100) if total > 0 else 0,
            'direct_mapping_count': direct_method,
            'openai_mapping_count': openai_method,
            'direct_mapping_rate': (direct_method / total * 100) if total > 0 else 0
        }
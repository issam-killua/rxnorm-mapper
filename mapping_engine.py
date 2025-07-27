import time
from tqdm import tqdm
import pandas as pd
from typing import Dict, List
from config import Config
from data_processor import DataProcessor
from openai_mapper import OpenAIMapper
from rxnorm_validator import RxNormValidator

class MappingEngine:
    def __init__(self, openai_api_key: str):
        self.ai_mapper = OpenAIMapper(openai_api_key)
        self.rxnorm_validator = RxNormValidator()
        self.results = []
    
    def process_single_product(self, product_row: pd.Series, index: int) -> Dict:
        """Process a single product through the complete mapping pipeline"""
        
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
            # Step 1: AI Mapping
            print(f"Processing: {product_context['product_name']}")
            ai_result = self.ai_mapper.map_product(product_context)
            result['ai_mapping'] = ai_result
            result['processing_status'] = 'ai_completed'
            
            if ai_result and ai_result.get('primary_rxnorm_concept'):
                # Step 2: RxNorm Validation
                concepts_to_try = [ai_result['primary_rxnorm_concept']]
                if ai_result.get('alternative_concepts'):
                    concepts_to_try.extend(ai_result['alternative_concepts'])
                
                rxnorm_result = self.rxnorm_validator.validate_multiple_concepts(concepts_to_try)
                result['rxnorm_validation'] = rxnorm_result
                result['processing_status'] = 'completed'
                
                # Determine final status
                if rxnorm_result.get('found'):
                    result['final_status'] = 'success'
                    result['needs_review'] = ai_result.get('confidence_score', 0) < 7
                else:
                    result['final_status'] = 'failed'
                    result['needs_review'] = True
            else:
                result['final_status'] = 'ai_failed'
                result['needs_review'] = True
                result['rxnorm_validation'] = {'found': False, 'error': 'AI mapping failed'}
            
        except Exception as e:
            result['final_status'] = 'error'
            result['error'] = str(e)
            result['processing_status'] = 'error'
            result['needs_review'] = True
            print(f"Error processing product {index}: {str(e)}")
        
        return result
    
    def process_batch(self, products_df: pd.DataFrame, start_idx: int = 0, batch_size: int = None) -> List[Dict]:
        """Process a batch of products"""
        if batch_size is None:
            batch_size = Config.BATCH_SIZE
        
        end_idx = min(start_idx + batch_size, len(products_df))
        batch_results = []
        
        print(f"Processing batch: {start_idx} to {end_idx}")
        
        for idx in tqdm(range(start_idx, end_idx), desc="Processing products"):
            result = self.process_single_product(products_df.iloc[idx], idx)
            batch_results.append(result)
            self.results.append(result)
            
            # Rate limiting
            time.sleep(Config.RATE_LIMIT_DELAY)
        
        return batch_results
    
    def get_statistics(self) -> Dict:
        """Calculate processing statistics"""
        if not self.results:
            return {}
        
        total = len(self.results)
        successful = len([r for r in self.results if r.get('final_status') == 'success'])
        failed = len([r for r in self.results if r.get('final_status') in ['failed', 'ai_failed', 'error']])
        needs_review = len([r for r in self.results if r.get('needs_review', False)])
        
        return {
            'total_processed': total,
            'successful_mappings': successful,
            'failed_mappings': failed,
            'needs_manual_review': needs_review,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'review_rate': (needs_review / total * 100) if total > 0 else 0
        }

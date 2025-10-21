import time
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
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
        
        # Initialize direct RxNorm mapper with Mistral for form translation
        if mistral_api_key:
            self.direct_mapper = DirectRxNormMapper(mistral_api_key)
        else:
            self.direct_mapper = DirectRxNormMapper()
            
        # Initialize other components if needed for fallback
        if openai_api_key:
            self.ai_mapper = OpenAIMapper(openai_api_key)
        else:
            self.ai_mapper = None
            
        # Always initialize RxNorm validator for fallback strategies
        self.rxnorm_validator = RxNormValidator()
            
        # Results storage
        self.results = []
        
        # Statistics tracking
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "needs_review": 0,
            "direct_mapping_success": 0,
            "processing_time": 0,
            "start_time": None
        }
    
    def process_dataframe_direct(self, df: pd.DataFrame, batch_size: int = 50, max_workers: int = 10) -> List[Dict]:
        """Process entire dataframe using optimized direct mapping approach"""
        self.stats["start_time"] = time.time()
        print(f"Starting direct mapping of {len(df)} products with batch size {batch_size} and {max_workers} workers")
        
        # Process using the DirectRxNormMapper's batch processing
        all_results = self.direct_mapper.process_dataframe_batch(df, batch_size)
        
        # Store results and update statistics
        self.results = all_results
        
        # Update statistics
        self.stats["total_processed"] = len(all_results)
        self.stats["successful"] = sum(1 for r in all_results if r.get('final_status') == 'success')
        self.stats["failed"] = sum(1 for r in all_results if r.get('final_status') in ['failed', 'error'])
        self.stats["needs_review"] = sum(1 for r in all_results if r.get('needs_review', False))
        self.stats["direct_mapping_success"] = self.stats["successful"]
        self.stats["processing_time"] = time.time() - self.stats["start_time"]
        
        # Print final statistics
        print("\n" + "="*60)
        print("MAPPING STATISTICS")
        print("="*60)
        print(f"Total Products Processed: {self.stats['total_processed']}")
        print(f"Successful Mappings: {self.stats['successful']}")
        print(f"Failed Mappings: {self.stats['failed']}")
        print(f"Need Manual Review: {self.stats['needs_review']}")
        
        success_rate = (self.stats['successful'] / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
        print(f"Success Rate: {success_rate:.2f}%")
        
        review_rate = (self.stats['needs_review'] / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
        print(f"Review Rate: {review_rate:.2f}%")
        
        processing_time = self.stats['processing_time']
        print(f"Processing Time: {processing_time:.2f} seconds ({processing_time/60:.2f} minutes)")
        
        products_per_second = self.stats['total_processed'] / processing_time if processing_time > 0 else 0
        print(f"Processing Speed: {products_per_second:.2f} products per second")
        print("="*60)
        
        return all_results
    
    def process_with_fallback(self, df: pd.DataFrame, batch_size: int = 50, max_workers: int = 10) -> List[Dict]:
        """Process dataframe with direct mapping and OpenAI fallback for failed mappings"""
        self.stats["start_time"] = time.time()
        print(f"Starting direct mapping with fallback of {len(df)} products with batch size {batch_size}")
        
        # First attempt direct mapping for all products
        all_results = self.direct_mapper.process_dataframe_batch(df, batch_size)
        
        # Identify failed products for OpenAI fallback
        failed_indices = [i for i, r in enumerate(all_results) if r.get('final_status') != 'success']
        failed_count = len(failed_indices)
        
        print(f"Initial direct mapping complete: {len(all_results) - failed_count}/{len(all_results)} successful")
        
        # Only attempt fallback if OpenAI API is available and there are failed products
        if self.ai_mapper and failed_count > 0 and self.openai_api_key:
            print(f"Attempting OpenAI fallback for {failed_count} products")
            
            # Create a data processor for the fallback
            data_processor = DataProcessor("")
            
            # Process failed products with OpenAI in parallel batches
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                
                # Submit all failed products for OpenAI processing
                for idx in failed_indices:
                    product_row = df.iloc[idx]
                    product_context = data_processor.prepare_product_context(product_row)
                    
                    futures.append(executor.submit(self._process_with_openai_fallback, 
                                                 product_context, 
                                                 idx,
                                                 all_results[idx]))
                
                # Collect results
                for future in ThreadPoolExecutor.as_completed(futures):
                    try:
                        result = future.result()
                        # The result is already updated in all_results
                    except Exception as e:
                        print(f"Error in fallback processing: {e}")
        
        # Store results
        self.results = all_results
        
        # Update statistics
        self.stats["total_processed"] = len(all_results)
        self.stats["successful"] = sum(1 for r in all_results if r.get('final_status') == 'success')
        self.stats["failed"] = sum(1 for r in all_results if r.get('final_status') in ['failed', 'error'])
        self.stats["needs_review"] = sum(1 for r in all_results if r.get('needs_review', False))
        self.stats["direct_mapping_success"] = len(all_results) - failed_count
        self.stats["openai_success"] = self.stats["successful"] - self.stats["direct_mapping_success"]
        self.stats["processing_time"] = time.time() - self.stats["start_time"]
        
        # Print final statistics
        print("\n" + "="*60)
        print("HYBRID MAPPING STATISTICS")
        print("="*60)
        print(f"Total Products Processed: {self.stats['total_processed']}")
        print(f"Successful Mappings: {self.stats['successful']}")
        print(f"Failed Mappings: {self.stats['failed']}")
        print(f"Need Manual Review: {self.stats['needs_review']}")
        
        success_rate = (self.stats['successful'] / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
        print(f"Success Rate: {success_rate:.2f}%")
        
        direct_success_rate = (self.stats['direct_mapping_success'] / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
        print(f"Direct Mapping Success Rate: {direct_success_rate:.2f}%")
        
        if 'openai_success' in self.stats:
            openai_attempt_count = failed_count
            openai_success_rate = (self.stats['openai_success'] / openai_attempt_count * 100) if openai_attempt_count > 0 else 0
            print(f"OpenAI Fallback Success Rate: {openai_success_rate:.2f}% ({self.stats['openai_success']}/{openai_attempt_count})")
        
        review_rate = (self.stats['needs_review'] / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
        print(f"Review Rate: {review_rate:.2f}%")
        
        processing_time = self.stats['processing_time']
        print(f"Processing Time: {processing_time:.2f} seconds ({processing_time/60:.2f} minutes)")
        
        products_per_second = self.stats['total_processed'] / processing_time if processing_time > 0 else 0
        print(f"Processing Speed: {products_per_second:.2f} products per second")
        print("="*60)
        
        return all_results
    
    def _process_with_openai_fallback(self, product_context: Dict, index: int, existing_result: Dict) -> Dict:
        """Process a single product with OpenAI fallback"""
        try:
            # Use OpenAI mapper
            ai_result = self.ai_mapper.map_product(product_context)
            existing_result['ai_mapping'] = ai_result
            
            if ai_result and ai_result.get('primary_rxnorm_concept'):
                # Validate with RxNorm API
                concepts_to_try = [ai_result['primary_rxnorm_concept']]
                if ai_result.get('alternative_concepts'):
                    concepts_to_try.extend(ai_result['alternative_concepts'])
                
                rxnorm_result = self.rxnorm_validator.validate_multiple_concepts(concepts_to_try)
                existing_result['rxnorm_validation'] = rxnorm_result
                existing_result['mapping_method'] = 'openai_fallback'
                
                # Determine final status
                if rxnorm_result.get('found'):
                    existing_result['final_status'] = 'success'
                    existing_result['needs_review'] = ai_result.get('confidence_score', 0) < 7
                else:
                    existing_result['final_status'] = 'failed'
                    existing_result['needs_review'] = True
            else:
                existing_result['final_status'] = 'failed'
                existing_result['needs_review'] = True
                existing_result['error'] = "OpenAI fallback failed"
        
        except Exception as e:
            existing_result['error'] = f"OpenAI fallback error: {str(e)}"
            existing_result['final_status'] = 'error'
            existing_result['needs_review'] = True
            
        return existing_result
    
    def get_statistics(self) -> Dict:
        """Get processing statistics"""
        if not self.results:
            return {}
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('final_status') == 'success')
        failed = sum(1 for r in self.results if r.get('final_status') in ['failed', 'error'])
        needs_review = sum(1 for r in self.results if r.get('needs_review', False))
        
        # Method statistics
        direct_method = sum(1 for r in self.results if 
                          r.get('mapping_method', '') == 'direct_rxnorm' and 
                          r.get('final_status') == 'success')
        
        openai_method = sum(1 for r in self.results if 
                          r.get('mapping_method', '') == 'openai_fallback' and 
                          r.get('final_status') == 'success')
        
        return {
            'total_processed': total,
            'successful_mappings': successful,
            'failed_mappings': failed,
            'needs_manual_review': needs_review,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'review_rate': (needs_review / total * 100) if total > 0 else 0,
            'direct_mapping_count': direct_method,
            'openai_mapping_count': openai_method,
            'direct_mapping_rate': (direct_method / total * 100) if total > 0 else 0,
            'processing_time': self.stats.get('processing_time', 0)
        }
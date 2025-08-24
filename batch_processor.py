import json
import time
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI
import pandas as pd
from config import Config
from prompt_engineer import PromptEngineer
from data_processor import DataProcessor  # Added this import

@dataclass
class BatchStatus:
    batch_id: str
    status: str
    request_counts: Dict
    created_at: int
    completed_at: Optional[int] = None
    output_file_id: Optional[str] = None
    error_file_id: Optional[str] = None

class BatchProcessor:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.prompt_engineer = PromptEngineer()
    
    def create_batch_file(self, products_df: pd.DataFrame, output_path: str = "batch_input.jsonl") -> str:
        """Convert CSV products to JSONL format for Batch API"""
        
        data_processor = DataProcessor("")
        batch_requests = []
        
        print(f"Creating batch file for {len(products_df)} products...")
        
        for idx, row in products_df.iterrows():
            # Prepare product context (same as your current system)
            product_context = data_processor.prepare_product_context(row)
            
            # Create the prompt using your existing prompt engineering
            prompt = self.prompt_engineer.create_mapping_prompt(product_context)
            
            # Create batch request in required format
            batch_request = {
                "custom_id": f"product_{idx}",  # Unique identifier for each request
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": Config.OPENAI_MODEL,
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are a pharmaceutical expert specializing in RxNorm mapping. Always respond with valid JSON only."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": Config.OPENAI_TEMPERATURE,
                    "max_tokens": Config.OPENAI_MAX_TOKENS
                    # Removed unsupported response_format parameter
                }
            }
            
            batch_requests.append(batch_request)
        
        # Write to JSONL file
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for request in batch_requests:
                f.write(json.dumps(request, ensure_ascii=False) + '\n')
        
        print(f"Batch file created: {output_path}")
        return output_path
    
    def submit_batch(self, input_file_path: str, description: str = None) -> BatchStatus:
        """Submit batch file to OpenAI"""
        
        print(f"Uploading batch file: {input_file_path}")
        
        # Upload the file
        with open(input_file_path, 'rb') as f:
            batch_input_file = self.client.files.create(
                file=f,
                purpose="batch"
            )
        
        print(f"File uploaded with ID: {batch_input_file.id}")
        
        # Create the batch
        batch = self.client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": description or "Moroccan pharmaceutical products RxNorm mapping"
            }
        )
        
        print(f"Batch submitted with ID: {batch.id}")
        print(f"Status: {batch.status}")
        
        return BatchStatus(
            batch_id=batch.id,
            status=batch.status,
            request_counts=batch.request_counts.__dict__,
            created_at=batch.created_at
        )
    
    def check_batch_status(self, batch_id: str) -> BatchStatus:
        """Check the status of a batch"""
        
        batch = self.client.batches.retrieve(batch_id)
        
        return BatchStatus(
            batch_id=batch.id,
            status=batch.status,
            request_counts=batch.request_counts.__dict__,
            created_at=batch.created_at,
            completed_at=batch.completed_at,
            output_file_id=batch.output_file_id,
            error_file_id=batch.error_file_id
        )
    
    def wait_for_completion(self, batch_id: str, check_interval: int = 60) -> BatchStatus:
        """Wait for batch to complete with progress updates"""
        
        print(f"Waiting for batch {batch_id} to complete...")
        
        while True:
            status = self.check_batch_status(batch_id)
            
            print(f"Status: {status.status}")
            print(f"Request counts: {status.request_counts}")
            
            if status.status in ['completed', 'failed', 'cancelled']:
                break
            
            print(f"Checking again in {check_interval} seconds...")
            time.sleep(check_interval)
        
        if status.status == 'completed':
            print(f"✅ Batch completed successfully!")
        else:
            print(f"❌ Batch ended with status: {status.status}")
        
        return status
    
    def download_results(self, batch_status: BatchStatus, output_path: str = "batch_output.jsonl") -> str:
        """Download batch results"""
        
        if not batch_status.output_file_id:
            raise ValueError("No output file available")
        
        print(f"Downloading results...")
        
        # Download the result file
        file_response = self.client.files.content(batch_status.output_file_id)
        
        with open(output_path, 'wb') as f:
            f.write(file_response.content)
        
        print(f"Results downloaded to: {output_path}")
        return output_path
    
    def process_batch_results(self, results_file: str, products_df: pd.DataFrame) -> List[Dict]:
        """Process batch results and convert to your existing format"""
        
        results = []
        
        print(f"Processing batch results from: {results_file}")
        
        # Read batch results
        with open(results_file, 'r', encoding='utf-8') as f:
            for line in f:
                batch_result = json.loads(line.strip())
                results.append(batch_result)
        
        # Convert to your existing result format
        processed_results = []
        data_processor = DataProcessor("")
        
        for batch_result in results:
            custom_id = batch_result['custom_id']
            product_idx = int(custom_id.split('_')[1])  # Extract index from "product_123"
            
            # Prepare the product context with standardized field names
            product_row = products_df.iloc[product_idx]
            product_context = data_processor.prepare_product_context(product_row)
            
            result = {
                'index': product_idx,
                'original_data': product_context,  # Use prepared context instead of raw data
                'timestamp': pd.Timestamp.now(),
                'custom_id': custom_id
            }
            
            if batch_result.get('error'):
                # Handle API errors
                result['final_status'] = 'ai_failed'
                result['error'] = batch_result['error']
                result['needs_review'] = True
                result['ai_mapping'] = None
            else:
                # Parse successful response
                response = batch_result['response']
                message_content = response['body']['choices'][0]['message']['content']
                
                try:
                    ai_mapping = json.loads(message_content)
                    result['ai_mapping'] = ai_mapping
                    result['processing_status'] = 'ai_completed'
                    
                    # Determine if needs review based on confidence
                    confidence = ai_mapping.get('confidence_score', 0)
                    result['needs_review'] = confidence < 7
                    
                except json.JSONDecodeError as e:
                    result['final_status'] = 'ai_failed'
                    result['error'] = f"JSON parse error: {str(e)}"
                    result['needs_review'] = True
                    result['ai_mapping'] = None
            
            processed_results.append(result)
        
        # Sort by index to maintain original order
        processed_results.sort(key=lambda x: x['index'])
        
        print(f"Processed {len(processed_results)} results")
        return processed_results
    
    def full_batch_workflow(self, products_df: pd.DataFrame, description: str = None) -> List[Dict]:
        """Complete workflow: CSV → Batch API → Results"""
        
        print("🚀 Starting OpenAI Batch API workflow...")
        
        # Step 1: Create batch file
        batch_file = self.create_batch_file(products_df)
        
        # Step 2: Submit batch
        batch_status = self.submit_batch(batch_file, description)
        
        # Step 3: Wait for completion
        completed_status = self.wait_for_completion(batch_status.batch_id)
        
        if completed_status.status != 'completed':
            raise Exception(f"Batch failed with status: {completed_status.status}")
        
        # Step 4: Download results
        results_file = self.download_results(completed_status)
        
        # Step 5: Process results
        processed_results = self.process_batch_results(results_file, products_df)
        
        # Cleanup temporary files
        try:
            os.remove(batch_file)
            os.remove(results_file)
            print("Cleaned up temporary files")
        except:
            pass
        
        print("✅ Batch workflow completed successfully!")
        return processed_results

# Example usage and integration with existing system
class BatchMappingEngine:
    """Enhanced mapping engine that uses Batch API for AI processing"""
    
    def __init__(self, openai_api_key: str):
        self.batch_processor = BatchProcessor(openai_api_key)
        from rxnorm_validator import RxNormValidator
        self.rxnorm_validator = RxNormValidator()
        self.results = []
    
    def process_with_batch_api(self, products_df: pd.DataFrame) -> List[Dict]:
        """Process all products using Batch API, then validate with RxNorm"""
        
        print(f"Processing {len(products_df)} products with Batch API...")
        
        # Step 1: Get AI mappings using Batch API
        batch_results = self.batch_processor.full_batch_workflow(
            products_df,
            description=f"RxNorm mapping for {len(products_df)} Moroccan pharmaceutical products"
        )
        
        print("Now validating with RxNorm API...")
        
        # Step 2: Validate each result with RxNorm API
        final_results = []
        
        for i, result in enumerate(batch_results):
            print(f"Validating {i+1}/{len(batch_results)}: {result.get('original_data', {}).get('product_name', 'Unknown')}")
            
            if result.get('ai_mapping') and result['ai_mapping'].get('primary_rxnorm_concept'):
                # Validate with RxNorm
                ai_mapping = result['ai_mapping']
                concepts_to_try = [ai_mapping['primary_rxnorm_concept']]
                if ai_mapping.get('alternative_concepts'):
                    concepts_to_try.extend(ai_mapping['alternative_concepts'])
                
                rxnorm_result = self.rxnorm_validator.validate_multiple_concepts(concepts_to_try)
                result['rxnorm_validation'] = rxnorm_result
                
                # Determine final status
                if rxnorm_result.get('found'):
                    result['final_status'] = 'success'
                else:
                    result['final_status'] = 'failed'
                    result['needs_review'] = True
            else:
                result['final_status'] = 'ai_failed'
                result['rxnorm_validation'] = {'found': False, 'error': 'AI mapping failed'}
            
            final_results.append(result)
            
            # Rate limiting for RxNorm API
            time.sleep(Config.RATE_LIMIT_DELAY)
        
        self.results = final_results
        return final_results
    
    def get_statistics(self) -> Dict:
        """Calculate processing statistics (same as original)"""
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
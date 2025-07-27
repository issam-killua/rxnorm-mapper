import os
import pandas as pd
from datetime import datetime
from typing import List, Dict

class CSVExporter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_results(self, results: List[Dict], filename_prefix: str = "rxnorm_mapping") -> str:
        """Export mapping results to CSV"""
        
        # Prepare data for CSV
        csv_data = []
        
        for result in results:
            original = result.get('original_data', {})
            ai_mapping = result.get('ai_mapping', {})
            rxnorm_validation = result.get('rxnorm_validation', {})
            
            row = {
                # Original product data
                'original_code': original.get('code', ''),
                'original_name': original.get('product_name', ''),
                'original_dci': original.get('active_ingredient', ''),
                'original_dosage': original.get('full_dosage', ''),
                'original_form': original.get('form', ''),
                'original_presentation': original.get('presentation', ''),
                
                # AI mapping results
                'ai_primary_concept': ai_mapping.get('primary_rxnorm_concept', ''),
                'ai_confidence_score': ai_mapping.get('confidence_score', 0),
                'ai_dosage_standardized': ai_mapping.get('dosage_standardized', ''),
                'ai_form_standardized': ai_mapping.get('form_standardized', ''),
                'ai_active_ingredient_english': ai_mapping.get('active_ingredient_english', ''),
                'ai_mapping_strategy': ai_mapping.get('mapping_strategy', ''),
                'ai_reasoning': ai_mapping.get('reasoning', ''),
                'ai_alternatives': ', '.join(ai_mapping.get('alternative_concepts', [])),
                
                # RxNorm validation results
                'rxnorm_found': rxnorm_validation.get('found', False),
                'rxnorm_rxcui': rxnorm_validation.get('rxcui', ''),
                'rxnorm_name': rxnorm_validation.get('name', ''),
                'rxnorm_tty': rxnorm_validation.get('tty', ''),
                'rxnorm_match_type': rxnorm_validation.get('match_type', ''),
                'rxnorm_search_term': rxnorm_validation.get('search_term', ''),
                
                # Final status
                'final_status': result.get('final_status', ''),
                'needs_review': result.get('needs_review', False),
                'processing_status': result.get('processing_status', ''),
                'error_message': result.get('error', ''),
                'timestamp': result.get('timestamp', ''),
                
                # Additional metrics
                'tokens_used': ai_mapping.get('tokens_used', 0),
            }
            
            csv_data.append(row)
        
        # Create DataFrame and export
        df = pd.DataFrame(csv_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"Results exported to: {filepath}")
        return filepath

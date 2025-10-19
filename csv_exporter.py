import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from config import Config

class CSVExporter:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_results(self, results: List[Dict], filename_prefix: str = "rxnorm_mapping") -> str:
        """Export mapping results to CSV file"""
        
        if not results:
            raise ValueError("No results to export")
        
        # Prepare data for CSV
        csv_data = []
        
        for result in results:
            # Original product data
            original_data = result.get('original_data', {})
            
            # Translation data (for hybrid method)
            translation = result.get('translation', {})
            
            # AI mapping results
            ai_mapping = result.get('ai_mapping', {})
            
            # RxNorm validation results
            rxnorm_validation = result.get('rxnorm_validation', {})
            
            row = {
                # Original product information
                'original_code': original_data.get('code', ''),
                'original_product_name': original_data.get('product_name', ''),
                'original_dci': original_data.get('active_ingredient', ''),
                'original_dosage': original_data.get('dosage', ''),
                'original_form': original_data.get('form', ''),
                'original_presentation': original_data.get('presentation', ''),
                'original_full_dosage': original_data.get('full_dosage', ''),
                
                # Translation results (for hybrid method)
                'translated_product_name': translation.get('product_name_english', ''),
                'translated_dci': translation.get('active_ingredient_english', ''),
                'translated_dosage': translation.get('dosage_standardized', ''),
                'translated_form': translation.get('form_standardized', ''),
                
                # Mapping method
                'mapping_method': result.get('mapping_method', 'openai'),
                
                # AI mapping results (if applicable)
                'ai_primary_concept': ai_mapping.get('primary_rxnorm_concept', '') if ai_mapping else '',
                'ai_confidence_score': ai_mapping.get('confidence_score', 0) if ai_mapping else 0,
                'ai_alternative_concepts': str(ai_mapping.get('alternative_concepts', [])) if ai_mapping else '',
                'ai_mapping_strategy': ai_mapping.get('mapping_strategy', '') if ai_mapping else '',
                'ai_dosage_standardized': ai_mapping.get('dosage_standardized', '') if ai_mapping else '',
                'ai_form_standardized': ai_mapping.get('form_standardized', '') if ai_mapping else '',
                'ai_active_ingredient_english': ai_mapping.get('active_ingredient_english', '') if ai_mapping else '',
                'ai_reasoning': ai_mapping.get('reasoning', '') if ai_mapping else '',
                
                # RxNorm validation results
                'rxnorm_found': rxnorm_validation.get('found', False),
                'rxnorm_rxcui': rxnorm_validation.get('rxcui', '') if rxnorm_validation.get('found') else '',
                'rxnorm_name': rxnorm_validation.get('name', '') if rxnorm_validation.get('found') else '',
                'rxnorm_tty': rxnorm_validation.get('tty', '') if rxnorm_validation.get('found') else '',
                'rxnorm_match_type': rxnorm_validation.get('match_type', '') if rxnorm_validation.get('found') else '',
                'rxnorm_search_term': rxnorm_validation.get('search_term', '') if rxnorm_validation else '',
                'rxnorm_error': rxnorm_validation.get('error', '') if not rxnorm_validation.get('found') else '',
                
                # Processing metadata
                'final_status': result.get('final_status', ''),
                'needs_review': result.get('needs_review', False),
                'processing_status': result.get('processing_status', ''),
                'error_message': result.get('error', ''),
                'timestamp': result.get('timestamp', ''),
                'tokens_used': ai_mapping.get('tokens_used', 0) if ai_mapping else 0,
            }
            
            csv_data.append(row)
        
        # Create DataFrame and export
        df = pd.DataFrame(csv_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Export to CSV
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"Results exported to: {filepath}")
        return filepath
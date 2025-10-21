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
        
        # Convert to DataFrame directly
        df = pd.DataFrame(results)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Export to CSV
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"Results exported to: {filepath}")
        return filepath
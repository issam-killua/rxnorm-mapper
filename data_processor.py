import pandas as pd
import json
from typing import Dict, List, Optional

class DataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.products = None
        
    def load_data(self) -> pd.DataFrame:
        """Load and clean the Moroccan medical products data"""
        try:
            df = pd.read_excel(self.file_path)
            
            # Clean and standardize column names
            df.columns = df.columns.str.strip()
            
            # Fill NaN values
            df = df.fillna('')
            
            # Create a unique identifier
            df['unique_id'] = df.index
            
            self.products = df
            print(f"Loaded {len(df)} products from {self.file_path}")
            return df
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise
    
    def prepare_product_context(self, row: pd.Series) -> Dict:
        """Prepare product context for AI mapping"""
        context = {
            'product_name': str(row.get('NOM', '')).strip(),
            'active_ingredient': str(row.get('DCI1', '')).strip(),
            'dosage': str(row.get('DOSAGE1', '')).strip(),
            'dosage_unit': str(row.get('UNITE_DOSAGE1', '')).strip(),
            'form': str(row.get('FORME', '')).strip(),
            'presentation': str(row.get('PRESENTATION', '')).strip(),
            'code': str(row.get('CODE', '')).strip(),
            'full_dosage': f"{row.get('DOSAGE1', '')} {row.get('UNITE_DOSAGE1', '')}".strip()
        }
        return context

import requests
import urllib.parse
import json
import time
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from datetime import datetime

class DirectRxNormMapper:
    def __init__(self, mistral_api_key: Optional[str] = None):
        self.base_url = "https://rxnav.nlm.nih.gov/REST"
        self.session = requests.Session()
        self.mistral_api_key = mistral_api_key
        
        # Common form translations
        self.form_translations = {
            "COMPRIME": "TABLET",
            "GELULE": "CAPSULE",
            "SOLUTION BUVABLE": "ORAL SOLUTION",
            "SOLUTION INJECTABLE": "INJECTION",
            "SOLUTION POUR PERFUSION": "INFUSION SOLUTION",
            "SOLUTION POUR IRRIGATION": "IRRIGATION SOLUTION",
            "SOLUTION A DILUER POUR PERFUSION": "SOLUTION FOR INFUSION",
            "POUDRE POUR SUSPENSION BUVABLE": "POWDER FOR ORAL SUSPENSION",
            "SUPPOSITOIRE": "SUPPOSITORY",
            "COMPRIME PELLICULE": "FILM-COATED TABLET",
            "COMPRIME ENROBE": "COATED TABLET",
            "COMPRIME DISPERSIBLE": "DISPERSIBLE TABLET",
            "COMPRIME SECABLE": "SCORED TABLET",
            "COMPRIME GASTRO-RESISTANT": "ENTERIC COATED TABLET",
            "COMPRIME ENROBE GASTRO-RESISTANT": "ENTERIC COATED TABLET",
            "GELULE GASTRO-RESISTANTE": "ENTERIC COATED CAPSULE",
            "POUDRE POUR SOLUTION INJECTABLE": "POWDER FOR INJECTION",
            "SOLUTION POUR INHALATION PAR NEBULISEUR": "SOLUTION FOR NEBULIZER",
            "EMULSION INJECTABLE": "INJECTABLE EMULSION",
            "GRANULE LP": "EXTENDED RELEASE GRANULES",
            "POMMADE": "OINTMENT",
            "CREME": "CREAM",
            "GEL": "GEL",
            "COLLYRE": "EYE DROPS",
            "SIROP": "SYRUP",
            "OVULE": "VAGINAL SUPPOSITORY",
            "CREME VAGINALE": "VAGINAL CREAM",
            "SUSPENSION INJECTABLE INTERMEDIAIRE": "INTERMEDIATE ACTING INJECTABLE SUSPENSION",
            "PASTILLE A SUCER": "LOZENGE",
            "GRANULE POUR SUSPENSION BUVABLE": "GRANULES FOR ORAL SUSPENSION",
            "COMPRIME EFFERVESCENT": "EFFERVESCENT TABLET",
            "SOLUTION RECTALE": "RECTAL SOLUTION",
            "MOUSSE": "FOAM"
        }
        
        # Common presentation translations
        self.presentation_translations = {
            "FLACON": "VIAL",
            "BOITE": "BOX",
            "AMPOULE": "AMPOULE",
            "TUBE": "TUBE",
            "POCHE": "POUCH",
            "COMPRIME": "TABLET",
            "GELULE": "CAPSULE",
            "SUPPOSITOIRE": "SUPPOSITORY",
            "SACHET": "SACHET",
            "SERINGUE PREREMPLIE": "PREFILLED SYRINGE",
            "RECIPIENT": "CONTAINER"
        }
    
    def translate_form(self, form: str) -> str:
        """Translate pharmaceutical form using predefined mappings"""
        if not form:
            return ""
        
        form_upper = form.upper()
        if form_upper in self.form_translations:
            return self.form_translations[form_upper]
        
        # If no translation found, return original
        return form
    
    def translate_presentation(self, presentation: str) -> str:
        """Translate presentation using predefined mappings"""
        if not presentation:
            return ""
        
        # This is a simple approach that looks for keywords in the presentation string
        result = presentation
        for french, english in self.presentation_translations.items():
            if french in presentation.upper():
                result = result.replace(french, english)
        
        return result
    
    def process_dataframe(self, df: pd.DataFrame, batch_size: int = 10) -> List[Dict]:
        """Process entire dataframe with optimized batching"""
        print("Starting direct RxNorm mapping process...")
        
        # Process in batches
        all_results = []
        total_rows = len(df)
        
        for start_idx in range(0, total_rows, batch_size):
            end_idx = min(start_idx + batch_size, total_rows)
            print(f"Processing batch {start_idx//batch_size + 1}: rows {start_idx} to {end_idx}")
            
            # Process batch
            batch_df = df.iloc[start_idx:end_idx]
            batch_results = []
            
            for _, row in batch_df.iterrows():
                # Create product data
                product = {
                    'code': str(row.get('CODE', '')),
                    'product_name': str(row.get('NOM', '')),
                    'active_ingredient': str(row.get('DCI1', '')),
                    'dosage': str(row.get('DOSAGE1', '')),
                    'dosage_unit': str(row.get('UNITE_DOSAGE1', '')),
                    'form': str(row.get('FORME', '')),
                    'presentation': str(row.get('PRESENTATION', '')),
                }
                
                # Map to RxNorm
                result = self.map_product(product)
                batch_results.append(result)
            
            # Add batch to overall results
            all_results.extend(batch_results)
            
            # Process batch
            success_count = sum(1 for r in batch_results if r.get('final_status') == 'success')
            print(f"Batch complete: {success_count}/{len(batch_results)} successful ({success_count/len(batch_results)*100:.1f}%)")
            
            # Small delay between batches
            time.sleep(0.2)
        
        return all_results
    
    def map_product(self, product: Dict) -> Dict:
        """Map a product to RxNorm"""
        # Get original values
        dci = product.get('active_ingredient', '')
        dosage = product.get('dosage', '')
        dosage_unit = product.get('dosage_unit', '')
        original_form = product.get('form', '')
        original_presentation = product.get('presentation', '')
        
        # Translate form and presentation to English
        translated_form = self.translate_form(original_form)
        translated_presentation = self.translate_presentation(original_presentation)
        
        # Basic structure with all needed fields (removing unused translation fields)
        result = {
            # Original data
            'original_code': product.get('code', ''),
            'original_product_name': product.get('product_name', ''),
            'original_dci': dci,
            'original_dosage': dosage,
            'original_form': original_form,
            'original_presentation': original_presentation,
            'original_full_dosage': f"{dosage} {dosage_unit}".strip(),
            
            # Translations (only what we're actually translating)
            'translated_form': translated_form,
            'translated_presentation': translated_presentation,
            
            # Method
            'mapping_method': 'direct_rxnorm',
            
            # Default RxNorm values
            'rxnorm_found': False,
            'rxnorm_rxcui': '',
            'rxnorm_name': '',
            'rxnorm_tty': '',
            'rxnorm_match_type': '',
            'rxnorm_search_term': '',
            
            # Status
            'final_status': 'processing',
            'needs_review': False,
            'error_message': ''
        }
        
        try:
            if not dci or dci.strip() == '':
                result['final_status'] = 'failed'
                result['needs_review'] = True
                result['error_message'] = 'Empty active ingredient'
                return result
            
            # Strategy 1: DCI + Dosage + Form (USE TRANSLATED FORM)
            if dosage and dosage_unit and translated_form:
                search_term = f"{dci} {dosage} {dosage_unit} {translated_form}"
                rxnorm_result = self._search_rxnorm(search_term)
                if rxnorm_result.get('found'):
                    result['rxnorm_found'] = True
                    result['rxnorm_rxcui'] = rxnorm_result.get('rxcui', '')
                    result['rxnorm_name'] = rxnorm_result.get('name', '')
                    result['rxnorm_tty'] = rxnorm_result.get('tty', '')
                    result['rxnorm_match_type'] = rxnorm_result.get('match_type', '')
                    result['rxnorm_search_term'] = search_term
                    result['final_status'] = 'success'
                    return result
            
            # Strategy 2: DCI + Dosage
            if dosage and dosage_unit:
                search_term = f"{dci} {dosage} {dosage_unit}"
                rxnorm_result = self._search_rxnorm(search_term)
                if rxnorm_result.get('found'):
                    result['rxnorm_found'] = True
                    result['rxnorm_rxcui'] = rxnorm_result.get('rxcui', '')
                    result['rxnorm_name'] = rxnorm_result.get('name', '')
                    result['rxnorm_tty'] = rxnorm_result.get('tty', '')
                    result['rxnorm_match_type'] = rxnorm_result.get('match_type', '')
                    result['rxnorm_search_term'] = search_term
                    result['final_status'] = 'success'
                    return result
            
            # Strategy 3: DCI + Form (USE TRANSLATED FORM)
            if translated_form:
                search_term = f"{dci} {translated_form}"
                rxnorm_result = self._search_rxnorm(search_term)
                if rxnorm_result.get('found'):
                    result['rxnorm_found'] = True
                    result['rxnorm_rxcui'] = rxnorm_result.get('rxcui', '')
                    result['rxnorm_name'] = rxnorm_result.get('name', '')
                    result['rxnorm_tty'] = rxnorm_result.get('tty', '')
                    result['rxnorm_match_type'] = rxnorm_result.get('match_type', '')
                    result['rxnorm_search_term'] = search_term
                    result['final_status'] = 'success'
                    return result
            
            # Strategy 4: DCI Only
            search_term = dci
            rxnorm_result = self._search_rxnorm(search_term)
            if rxnorm_result.get('found'):
                result['rxnorm_found'] = True
                result['rxnorm_rxcui'] = rxnorm_result.get('rxcui', '')
                result['rxnorm_name'] = rxnorm_result.get('name', '')
                result['rxnorm_tty'] = rxnorm_result.get('tty', '')
                result['rxnorm_match_type'] = rxnorm_result.get('match_type', '')
                result['rxnorm_search_term'] = search_term
                result['final_status'] = 'success'
                return result
            
            # All strategies failed
            result['final_status'] = 'failed'
            result['needs_review'] = True
            result['error_message'] = 'No RxNorm concept found with any search strategy'
        
        except Exception as e:
            result['final_status'] = 'error'
            result['needs_review'] = True
            result['error_message'] = str(e)
        
        return result
    
    def _search_rxnorm(self, search_term: str) -> Dict:
        """Search RxNorm API"""
        try:
            # Clean and encode term
            clean_term = search_term.strip()
            encoded_term = urllib.parse.quote(clean_term)
            
            # First try exact search
            url = f"{self.base_url}/drugs.json?name={encoded_term}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                result = self._parse_rxnorm_response(data, clean_term)
                if result.get('found'):
                    return result
            
            # Then try approximate search
            url = f"{self.base_url}/approximateTerm.json?term={encoded_term}&maxEntries=5"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_approximate_response(data, clean_term)
            
            return {'found': False}
        
        except Exception as e:
            return {'found': False, 'error': str(e)}
    
    def _parse_rxnorm_response(self, data: Dict, search_term: str) -> Dict:
        """Parse standard RxNorm API response"""
        try:
            drug_group = data.get('drugGroup', {})
            concept_groups = drug_group.get('conceptGroup', [])
            
            if not concept_groups:
                return {'found': False}
            
            # Preferred concept types
            preferred_types = ['SCD', 'GPCK', 'SCDC', 'BN', 'IN', 'MIN']
            
            for tty in preferred_types:
                for group in concept_groups:
                    if group.get('tty') == tty:
                        concepts = group.get('conceptProperties', [])
                        if concepts:
                            best_concept = concepts[0]
                            return {
                                'found': True,
                                'rxcui': best_concept.get('rxcui'),
                                'name': best_concept.get('name'),
                                'tty': best_concept.get('tty'),
                                'search_term': search_term,
                                'match_type': 'exact'
                            }
            
            # If no preferred type found, take the first available
            for group in concept_groups:
                concepts = group.get('conceptProperties', [])
                if concepts:
                    best_concept = concepts[0]
                    return {
                        'found': True,
                        'rxcui': best_concept.get('rxcui'),
                        'name': best_concept.get('name'),
                        'tty': best_concept.get('tty'),
                        'search_term': search_term,
                        'match_type': 'exact'
                    }
            
            return {'found': False}
            
        except Exception as e:
            return {'found': False, 'error': str(e)}
    
    def _parse_approximate_response(self, data: Dict, search_term: str) -> Dict:
        """Parse approximate search response"""
        try:
            approximate_group = data.get('approximateGroup', {})
            candidates = approximate_group.get('candidate', [])
            
            if not candidates:
                return {'found': False}
            
            # Take the first candidate with a good score
            best_candidate = candidates[0]
            score = float(best_candidate.get('score', 0))
            
            if score < 70:  # Minimum score threshold
                return {'found': False}
            
            return {
                'found': True,
                'rxcui': best_candidate.get('rxcui'),
                'name': best_candidate.get('name'),
                'tty': best_candidate.get('tty') or 'APPROX',
                'search_term': search_term,
                'match_type': 'approximate',
                'score': score
            }
            
        except Exception as e:
            return {'found': False, 'error': str(e)}
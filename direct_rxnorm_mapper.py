import requests
import urllib.parse
from typing import Dict, List, Optional
import time
from config import Config

class DirectRxNormMapper:
    def __init__(self):
        self.base_url = Config.RXNORM_BASE_URL
        self.session = requests.Session()
        self.rxnorm_validator = None
    
    def set_validator(self, validator):
        """Set the RxNorm validator for fallback"""
        self.rxnorm_validator = validator
    
    def map_product(self, translated_product: Dict) -> Dict:
        """Map a translated product directly to RxNorm using multiple strategies"""
        
        result = {
            'found': False,
            'mapping_method': 'direct_rxnorm',
            'searched_terms': [],
            'original_data': translated_product
        }
        
        # Strategy 1: Try with active ingredient and dosage
        if translated_product.get('active_ingredient_english') and translated_product.get('dosage_standardized'):
            search_term = f"{translated_product['active_ingredient_english']} {translated_product['dosage_standardized']}"
            result['searched_terms'].append(search_term)
            
            rxnorm_result = self._search_rxnorm(search_term)
            if rxnorm_result.get('found'):
                result.update(rxnorm_result)
                result['search_strategy'] = 'active_ingredient_with_dosage'
                return result
        
        # Strategy 2: Try with product name (if translated)
        if translated_product.get('product_name_english'):
            search_term = translated_product['product_name_english']
            result['searched_terms'].append(search_term)
            
            rxnorm_result = self._search_rxnorm(search_term)
            if rxnorm_result.get('found'):
                result.update(rxnorm_result)
                result['search_strategy'] = 'product_name'
                return result
        
        # Strategy 3: Try with active ingredient only
        if translated_product.get('active_ingredient_english'):
            search_term = translated_product['active_ingredient_english']
            result['searched_terms'].append(search_term)
            
            rxnorm_result = self._search_rxnorm(search_term)
            if rxnorm_result.get('found'):
                result.update(rxnorm_result)
                result['search_strategy'] = 'active_ingredient_only'
                return result
        
        # Strategy 4: Try normalized form with ingredient and standardized form
        if translated_product.get('active_ingredient_english') and translated_product.get('form_standardized'):
            search_term = f"{translated_product['active_ingredient_english']} {translated_product['form_standardized']}"
            result['searched_terms'].append(search_term)
            
            rxnorm_result = self._search_rxnorm(search_term)
            if rxnorm_result.get('found'):
                result.update(rxnorm_result)
                result['search_strategy'] = 'ingredient_with_form'
                return result
        
        result['error'] = "Could not find matching RxNorm concept with direct mapping"
        return result
    
    def _search_rxnorm(self, search_term: str) -> Dict:
        """Search for a term in RxNorm API"""
        if not search_term or search_term.strip() == '':
            return {'found': False, 'error': 'Empty search term'}
        
        try:
            # Clean and encode search term
            clean_term = search_term.strip()
            encoded_term = urllib.parse.quote(clean_term)
            
            # First try exact search
            url = f"{self.base_url}/drugs.json?name={encoded_term}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = self._parse_rxnorm_response(data, clean_term)
                if result['found']:
                    return result
            
            # If exact search fails, try approximate search
            url = f"{self.base_url}/approximateTerm.json?term={encoded_term}&maxEntries=5"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_approximate_response(data, clean_term)
            
            return {
                'found': False,
                'error': f'No results found for: {clean_term}',
                'search_term': clean_term
            }
            
        except Exception as e:
            return {
                'found': False,
                'error': str(e),
                'search_term': search_term
            }
    
    def _parse_rxnorm_response(self, data: Dict, search_term: str) -> Dict:
        """Parse standard RxNorm API response"""
        try:
            drug_group = data.get('drugGroup', {})
            concept_groups = drug_group.get('conceptGroup', [])
            
            if not concept_groups:
                return {'found': False}
            
            # Look for the best concept type (SCD, GPCK, etc.)
            preferred_types = ['SCD', 'GPCK', 'SCDC', 'BN']
            
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
            
            # Take the first candidate with highest score
            best_candidate = candidates[0]
            
            return {
                'found': True,
                'rxcui': best_candidate.get('rxcui'),
                'name': best_candidate.get('name'),
                'tty': 'APPROX',
                'search_term': search_term,
                'match_type': 'approximate',
                'score': best_candidate.get('score')
            }
            
        except Exception as e:
            return {'found': False, 'error': str(e)}
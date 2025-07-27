import requests
import urllib.parse
from typing import Dict, List, Optional
from config import Config

class RxNormValidator:
    def __init__(self):
        self.base_url = Config.RXNORM_BASE_URL
        self.session = requests.Session()
    
    def search_concept(self, concept_name: str) -> Dict:
        """Search for a concept in RxNorm"""
        if not concept_name or concept_name.strip() == '':
            return {'found': False, 'error': 'Empty concept name'}
        
        try:
            # Clean the concept name
            clean_name = concept_name.strip()
            encoded_name = urllib.parse.quote(clean_name)
            
            # Try exact search first
            url = f"{self.base_url}/drugs.json?name={encoded_name}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = self._parse_rxnorm_response(data, clean_name)
                if result['found']:
                    return result
            
            # If exact search fails, try approximate search
            url = f"{self.base_url}/approximateTerm.json?term={encoded_name}&maxEntries=5"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_approximate_response(data, clean_name)
            
            return {
                'found': False,
                'error': f'No results found for: {clean_name}',
                'search_term': clean_name
            }
            
        except Exception as e:
            return {
                'found': False,
                'error': str(e),
                'search_term': concept_name
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
    
    def validate_multiple_concepts(self, concepts: List[str]) -> Dict:
        """Try multiple concepts and return the best match"""
        best_result = {'found': False}
        
        for concept in concepts:
            if not concept:
                continue
                
            result = self.search_concept(concept)
            if result.get('found'):
                return result
            elif not best_result.get('found'):
                best_result = result
        
        return best_result

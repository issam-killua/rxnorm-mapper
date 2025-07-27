class PromptEngineer:
    
    @staticmethod
    def create_mapping_prompt(product_context: dict) -> str:
        """Create an optimized prompt for RxNorm mapping"""
        
        prompt = f"""You are a pharmaceutical expert specializing in drug standardization and RxNorm mapping. Your task is to map a Moroccan medical product to the most appropriate RxNorm concept.

PRODUCT INFORMATION:
- Product Name: {product_context['product_name']}
- Active Ingredient (DCI): {product_context['active_ingredient']}
- Dosage: {product_context['full_dosage']}
- Pharmaceutical Form: {product_context['form']}
- Presentation: {product_context['presentation']}
- Product Code: {product_context['code']}

INSTRUCTIONS:
1. Analyze the product information carefully
2. Consider standard pharmaceutical naming conventions
3. Account for French/Arabic to English translation needs
4. Map to the most specific appropriate RxNorm concept level (preferably SCD - Semantic Clinical Drug)
5. Provide confidence based on how well the mapping matches

RESPONSE FORMAT (JSON only):
{{
    "primary_rxnorm_concept": "exact concept name for RxNorm search",
    "confidence_score": <1-10>,
    "alternative_concepts": [
        "alternative concept 1",
        "alternative concept 2"
    ],
    "mapping_strategy": "brief explanation of mapping approach",
    "dosage_standardized": "standardized dosage format",
    "form_standardized": "standardized form",
    "active_ingredient_english": "English name of active ingredient",
    "reasoning": "detailed reasoning for this mapping"
}}

Focus on creating searchable terms that will work with RxNorm API. Consider:
- Generic vs brand name preferences
- Standard dosage unit conversions (mg, ml, etc.)
- Common pharmaceutical form terminology
- Active ingredient standard names (INN/generic names)

Respond only with valid JSON."""

        return prompt

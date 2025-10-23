# RxNorm Mapping Project

![RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/docs/images/rxnorm_logo.gif)

## Overview

This project implements and evaluates two different approaches for mapping pharmaceutical products to standard RxNorm concepts:

1. **OpenAI GPT-based approach** - Leveraging large language model capabilities for natural language understanding of pharmaceutical terms
2. **Direct (Mistral) approach** - Using the Mistral language model for direct mapping of pharmaceutical products

The project includes a comprehensive dashboard for analyzing mapping performance, comparing methodologies, and visualizing hierarchical relationships within RxNorm mappings.

## 🔍 Key Findings

Our analysis of 1,500 pharmaceutical products revealed:

- **OpenAI approach achieved 100% success rate** vs. 68.8% for the Direct approach
- **No exact RxCUI matches (0%)** between the two methods for the same products
- **33% of products showed hierarchy differences** - same medication mapped at different hierarchy levels
- **67% of products mapped to different concepts** by the two methods

The primary pattern observed was that the Direct approach tended to map to generic concepts (SCD - Semantic Clinical Drug), while the OpenAI approach more frequently mapped to brand-specific concepts (SBD - Semantic Branded Drug).

## 📊 Dashboard Features

The interactive Streamlit dashboard provides:

1. **📈 Results Analysis** - Overview of individual method performance
2. **📊 Method Comparison** - Direct comparison of both methods
3. **📋 Statistical Tests** - Significance testing and confidence intervals
4. **📑 Dataset Comparison** - Analysis of dataset overlap and characteristics
5. **🔍 Matched Products Analysis** - Product-by-product comparison
6. **🧩 Hierarchy Analysis** - Analysis of RxNorm hierarchical relationships
7. **🛠️ File Diagnostics** - Tools for diagnosing data format issues

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run rxnorm_dashboard_fixed.py
```

### Data Format

The dashboard expects CSV files with the following columns:
- `original_code` - Product identifier
- `original_product_name` - Product name
- `original_form` - Pharmaceutical form
- `original_dci` - Active ingredient(s)
- `rxnorm_rxcui` - RxNorm concept unique identifier
- `rxnorm_name` - RxNorm concept name
- `rxnorm_tty` - RxNorm term type
- `success` - Boolean indicating mapping success

## 📋 RxNorm Hierarchy

The project highlights the importance of understanding RxNorm's hierarchical structure:

| Term Type | Description | Example |
|-----------|-------------|---------|
| SCD | Semantic Clinical Drug (generic) | "Metformin 500 MG Oral Tablet" |
| SBD | Semantic Branded Drug | "Metformin 500 MG Oral Tablet [Glucophage]" |
| GPCK | Generic Pack | "Metformin 24 HR Extended Release Oral Tablet 500 MG / Metformin 24 HR Extended Release Oral Tablet 1000 MG Pack" |
| BPCK | Brand Name Pack | "Glucophage XR 24 HR Extended Release Oral Tablet 500 MG / Glucophage XR 24 HR Extended Release Oral Tablet 1000 MG Pack" |
| IN | Ingredient | "Metformin" |
| BN | Brand Name | "Glucophage" |

## 📝 Example Mapping Differences

```
Product: "Oxaliplatin 200mg solution for injection"
Direct (Mistral): RxCUI 1736776 - TTY: SCD - "10 ML oxaliplatin 5 MG/ML Injection"
OpenAI: RxCUI 1797528 - TTY: SBD - "200 MG oxaliplatin 5 MG/ML Injection [Eloxatin]"
```

Both mappings correctly identify the same active ingredient (oxaliplatin) but represent it at different levels of the RxNorm hierarchy - the Direct approach maps to the generic concept while the OpenAI approach maps to a branded concept.

## 💡 Recommendations

Based on our analysis, we recommend:

1. **Hybrid Approach** - Combining both methods for more comprehensive coverage
2. **Hierarchy-Aware Evaluation** - Considering hierarchical relationships instead of binary correct/incorrect evaluation
3. **Form-Specific Optimization** - Tailoring approach based on pharmaceutical form
4. **Enhanced Preprocessing** - Standardizing descriptions to reduce ambiguity
5. **Manual Review Process** - Creating a gold standard dataset through expert review

## 🧪 Project Structure

```
.
├── data/
│   ├── direct_results.csv        # Results from Direct (Mistral) approach
│   └── openai_results.csv        # Results from OpenAI approach
├── dashboard/
│   ├── rxnorm_dashboard.py       # Original dashboard
│   └── rxnorm_dashboard_fixed.py # Enhanced dashboard with error handling
├── notebooks/
│   ├── data_exploration.ipynb    # Data exploration notebook
│   └── mapping_analysis.ipynb    # Detailed mapping analysis
├── scripts/
│   ├── direct_mapping.py         # Direct mapping implementation
│   └── openai_mapping.py         # OpenAI mapping implementation
├── README.md                     # This file
└── requirements.txt              # Project dependencies
```

## 📚 Resources

- [RxNorm Overview](https://www.nlm.nih.gov/research/umls/rxnorm/overview.html)
- [RxNorm API](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html)
- [RxNorm Term Types](https://www.nlm.nih.gov/research/umls/rxnorm/docs/2015/appendix1.html)
- [Full Project Report](./RxNorm_Mapping_Project_Report.md)

## 🔄 Latest Updates

- **October 2023**:
  - Added new Hierarchy Analysis tab for understanding RxNorm hierarchy differences
  - Fixed column mapping issues and data type handling
  - Enhanced error reporting for better debugging
  - Added standardization for column names to handle different naming conventions
  - Improved product matching between different datasets
  - Added comprehensive documentation and project report

## 📝 Citation

If you use this project in your work, please cite:

```
[Your Name]. (2023). RxNorm Mapping Project [Computer software].
https://github.com/yourusername/rxnorm-mapping-project
```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

Moroccan Medical Products to RxNorm Mapper
An intelligent automated system for mapping Moroccan pharmaceutical products to RxNorm standardized concepts using advanced AI and comprehensive API validation with OpenAI Batch API integration for maximum cost efficiency.
🎯 Overview
This project processes 5,918+ Moroccan pharmaceutical products and maps them to internationally standardized RxNorm concepts. The system combines OpenAI GPT-4 artificial intelligence with official RxNorm API validation to ensure accurate and reliable pharmaceutical data standardization, achieving up to 100% success rates with intelligent batch processing.
✨ Key Features

🤖 AI-Powered Mapping: Advanced prompt engineering with OpenAI GPT-4/GPT-3.5-turbo
⚡ Batch API Integration: OpenAI Batch API for 50% cost reduction and efficient large-scale processing
✅ Dual Validation: RxNorm API verification of all mappings with fallback strategies
📊 Enhanced Interactive Dashboard: Real-time analytics, filtering, and professional visualizations
🎯 Smart Processing Modes: Individual processing for testing, batch processing for production
📈 Quality Assurance: Confidence scoring (1-10) with automated review flagging
📋 Comprehensive Export: Detailed CSV results with complete mapping traceability
🔄 Resume Capability: Continue processing from any point with robust error recovery
🔒 Security-First: Proper API key management and .gitignore protection
🔠 Mistral Translation: New approach using Mistral AI for translation and direct RxNorm mapping

🆕 New Feature: Mistral Translation with Direct RxNorm Mapping (October 2025)
Direct Translation Approach
The system now offers a new approach that uses Mistral AI for translation and direct RxNorm API mapping:

🤖 Mistral AI Translation: Fast and efficient translation of French/Arabic pharmaceutical terms to standardized English
⚡ Direct RxNorm Mapping: Maps translated terms directly to RxNorm concepts without additional AI processing
💰 Cost Efficiency: Eliminates dependency on OpenAI for simpler mapping cases
🚀 Streamlined Pipeline: Two-step process (translate → map) with no fallback complexity

Usage
bash# Test with small batch (Mistral-only approach)
python main.py --mode mistral --max-products 10

# Process all products with Mistral
python main.py --mode mistral

# Resume from specific index
python main.py --mode mistral --start-index 100

# Process with custom batch size
python main.py --mode mistral --batch-size 15
🏗️ System Architecture
Three-Stage Pipeline:

Data Extraction: Moroccan pharmaceutical data preprocessing from Excel
AI Mapping Stage:

Option 1: OpenAI GPT-4 analyzes product context and suggests RxNorm concepts
Option 2: Mistral AI translates product information for direct RxNorm mapping


Validation Stage: Official RxNorm API confirms concept existence and extracts standardized data

Processing Modes:

Individual Mode: Real-time processing with immediate results
Batch Mode: Cost-efficient batch processing for large datasets (recommended for 100+ products)
Mistral Mode: Translation-based approach with direct RxNorm mapping
Dashboard Mode: Analytics and monitoring interface

📋 Prerequisites

Python 3.8+
OpenAI API Key (with GPT-4 or GPT-3.5-turbo access) - for OpenAI modes
Mistral API Key - for Mistral mode
Internet Connection (for API access)
Excel File with pharmaceutical data (refdesmedicamentscnops.xlsx)

🚀 Quick Start
1. Clone Repository
bashgit clone https://github.com/issam-killua/rxnorm-mapper.git
cd rxnorm-mapper
2. Set Up Environment
bash# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
3. Install Dependencies
bashpip install -r requirements.txt
4. Configure API Keys
Create a .env file in the project root:
envOPENAI_API_KEY=your_openai_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
⚠️ Important: Replace with your actual API keys. The .env file is automatically ignored by git for security.
5. Add Data File
Place your Excel file (refdesmedicamentscnops.xlsx) in the project root directory.
6. Test Installation
bash# Quick test with Mistral approach
python main.py --mode mistral --max-products 3

# Quick test with OpenAI batch processing
python main.py --mode batch --max-products 3
💻 Usage
🔠 Mistral Mode (New)
Translation-based direct mapping
bash# Test with small batch
python main.py --mode mistral --max-products 10

# Medium batch for validation
python main.py --mode mistral --max-products 100

# Process all products
python main.py --mode mistral
🚀 Batch Processing (OpenAI)
Cost-efficient processing with OpenAI Batch API (50% cost savings)
bash# Test with small batch
python main.py --mode batch --max-products 10

# Medium batch for validation
python main.py --mode batch --max-products 100

# Process all products (production run)
python main.py --mode batch
⚙️ Individual Processing (OpenAI)
Real-time processing for testing and small batches
bash# Process 3 products individually (testing)
python main.py --mode process --max-products 3 --batch-size 1

# Process 50 products with batch size 10
python main.py --mode process --max-products 50 --batch-size 10
```

## 📊 Output & Results

Results are automatically saved to `output/rxnorm_mapping_[timestamp].csv` with comprehensive data including original product information, mapping results, validation status, and processing metadata.

## 🛠️ Technical Details

### Project Structure
```
rxnorm-mapper/
├── main.py                    # Application entry point with enhanced modes
├── config.py                  # Configuration settings and API parameters
├── data_processor.py          # Excel data processing with French column support
├── prompt_engineer.py         # Advanced AI prompt optimization
├── openai_mapper.py           # OpenAI GPT integration
├── batch_processor.py         # Batch API integration for cost efficiency
├── rxnorm_validator.py        # RxNorm API validation with fallback strategies
├── mapping_engine.py          # Processing orchestration
├── mistral_translator.py      # Mistral AI translation implementation
├── direct_rxnorm_mapper.py    # Direct RxNorm mapping implementation
├── hybrid_mapping_engine.py   # Mistral processing orchestration
├── csv_exporter.py            # Comprehensive results export
├── enhanced_dashboard.py      # Streamlit dashboard with analytics
├── requirements.txt           # Python dependencies
├── .env.example              # API key template
├── .gitignore                # Security protection
└── output/                   # Results directory
🔧 Configuration Options
Command Line Arguments
bash--mode {process,batch,mistral,dashboard}  # Operation mode
--input-file FILE                # Custom input Excel file path
--batch-size N                   # Products per batch for processing
--start-index N                  # Resume from specific index
--max-products N                 # Limit total products processed
Environment Variables
envOPENAI_API_KEY=sk-...           # OpenAI API key (for OpenAI modes)
MISTRAL_API_KEY=...             # Mistral API key (for Mistral mode)
📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

Project Status: ✅ Production Ready & Actively Maintained
Last Updated: October 2025
Current Version: 1.3.0
Success Rate: 🎯 Up to 100% in testing

Built with ❤️ for the healthcare and pharmaceutical industry
</artifact>
I've created an artifact with the updated README that includes the Mistral translation and direct RxNorm mapping approach. The README highlights the new functionality while maintaining information about the original approaches.

# Moroccan Medical Products to RxNorm Mapper

An intelligent automated system for mapping Moroccan pharmaceutical products to RxNorm standardized concepts using advanced AI and comprehensive API validation.

## 🎯 Overview

This project processes 5,918+ Moroccan pharmaceutical products and maps them to internationally standardized RxNorm concepts. The system combines OpenAI GPT-4 artificial intelligence with official RxNorm API validation to ensure accurate and reliable pharmaceutical data standardization.

## ✨ Key Features

- **🤖 AI-Powered Mapping**: Advanced prompt engineering with OpenAI GPT-4
- **✅ Dual Validation**: RxNorm API verification of all mappings
- **📊 Interactive Dashboard**: Real-time analytics and visualization
- **⚡ Batch Processing**: Configurable processing with rate limiting
- **📈 Quality Assurance**: Confidence scoring and manual review flagging
- **📋 Comprehensive Export**: Detailed CSV results with mapping metadata
- **🔄 Resume Capability**: Continue processing from any point

## 🏗️ System Architecture

**Two-Stage Pipeline:**
1. **AI Mapping Stage**: OpenAI GPT-4 analyzes product context and suggests RxNorm concepts
2. **Validation Stage**: Official RxNorm API confirms concept existence and extracts standardized data

## 📋 Prerequisites

- **Python 3.8+**
- **OpenAI API Key** (with GPT-4 access)
- **Internet Connection** (for API access)
- **Excel File** with pharmaceutical data

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/issam-killua/rxnorm-mapper.git
cd rxnorm-mapper
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```
**⚠️ Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 5. Add Data File
Place your Excel file (`refdesmedicamentscnops.xlsx`) in the project root directory.

### 6. Test Installation
```bash
# Quick test with 3 products
python main.py --mode process --max-products 3 --batch-size 1
```

## 💻 Usage

### Processing Commands

#### Test Processing
```bash
# Process 3 products (quick test)
python main.py --mode process --max-products 3 --batch-size 1

# Process 10 products
python main.py --mode process --max-products 10 --batch-size 5

# Process 50 products
python main.py --mode process --max-products 50 --batch-size 10
```

#### Full Processing
```bash
# Process all products (5,918+ products)
python main.py --mode process

# Process with custom batch size (recommended for speed)
python main.py --mode process --batch-size 20

# Resume from specific index
python main.py --mode process --start-index 1000 --batch-size 15
```

### Dashboard & Analytics
```bash
# Launch interactive dashboard
streamlit run main.py -- --mode dashboard
```

**Dashboard Features:**
- 📊 Real-time success rate metrics
- 📈 Confidence score distribution charts
- 📋 Interactive results table
- 🔍 Search and filter capabilities
- 📁 CSV file upload and analysis

## 📊 Output & Results

### CSV Export
Results are automatically saved to `output/rxnorm_mapping_[timestamp].csv` with:

**Original Product Data:**
- Product code, name, DCI (active ingredient)
- Dosage, form, presentation details

**AI Mapping Results:**
- Primary RxNorm concept suggestion
- Confidence score (1-10)
- Alternative concepts
- Mapping strategy and reasoning

**RxNorm Validation:**
- Validation status (success/failed)
- Official RXCUI identifier
- Standardized RxNorm name
- Term type (SCD, GPCK, etc.)

**Quality Metrics:**
- Final status classification
- Manual review flags
- Processing timestamps
- Token usage statistics

### Expected Performance
- **Success Rate**: 70-90% typical
- **Processing Speed**: 10-15 seconds per product
- **High Confidence Rate**: 80%+ with confidence ≥7/10
- **Review Rate**: 10-25% flagged for manual review

## 🛠️ Technical Details

### Project Structure
```
rxnorm-mapper/
├── main.py                 # Application entry point
├── config.py               # Configuration settings
├── data_processor.py       # Excel data processing
├── prompt_engineer.py      # AI prompt optimization
├── openai_mapper.py        # OpenAI GPT-4 integration
├── rxnorm_validator.py     # RxNorm API validation
├── mapping_engine.py       # Processing orchestration
├── csv_exporter.py         # Results export
├── dashboard.py            # Streamlit dashboard
├── requirements.txt        # Python dependencies
└── output/                 # Results directory
```

### API Integration
- **OpenAI GPT-4**: Intelligent pharmaceutical mapping
- **RxNorm REST API**: Official concept validation
- **Rate Limiting**: Automatic delays to prevent throttling
- **Error Handling**: Robust retry and recovery mechanisms

### Data Flow
```
Excel Input → Data Cleaning → AI Mapping → RxNorm Validation → CSV Export
```

## 🔧 Configuration Options

### Command Line Arguments
```bash
--mode {process,dashboard}     # Operation mode
--input-file FILE             # Custom input Excel file
--batch-size N                # Products per batch (default: 10)
--start-index N               # Resume from specific index
--max-products N              # Limit total products processed
```

### Environment Variables
```env
OPENAI_API_KEY=sk-...         # OpenAI API key (required)
```

### Config Settings
Customize in `config.py`:
- Batch sizes and rate limits
- OpenAI model parameters
- Output directories
- Processing timeouts

## 🚨 Troubleshooting

### Common Issues

**"API Key not found"**
- Check `.env` file exists and contains valid key
- Ensure `.env` is in project root directory
- Verify API key starts with `sk-`

**"Module not found"**
- Activate virtual environment: `venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

**"Excel file not found"**
- Place `refdesmedicamentscnops.xlsx` in project root
- Check file name spelling and extension

**Rate Limiting Errors**
- Reduce batch size: `--batch-size 5`
- Increase delays in `config.py`

### Performance Optimization
- **Increase batch size** for faster processing (if no rate limits)
- **Use SSD storage** for better I/O performance
- **Stable internet** connection for API reliability

## 📈 Monitoring Progress

### Real-time Statistics
- Total products processed
- Current success rate
- Review rate percentage
- Processing speed (products/minute)

### Progress Indicators
- Batch completion progress bars
- Time estimates for completion
- Live success/failure counts

## 🔐 Security Notes

- **API Key Protection**: Never commit `.env` file to version control
- **Rate Limiting**: Automatic compliance with OpenAI usage policies
- **Error Logging**: Secure logging without exposing sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** - GPT-4 artificial intelligence platform
- **National Library of Medicine** - RxNorm database and API
- **Python Community** - Open-source libraries and frameworks

## 📞 Support

For issues, questions, or contributions:
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Submit enhancement proposals

---

**Project Status**: ✅ Production Ready
**Last Updated**: July 2025
**Version**: 1.0.0

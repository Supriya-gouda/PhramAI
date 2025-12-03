<div align="center">

![PharmAI](FrontPage.png)

# 💊 PharmAI - AI Medical Prescription Safety System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![IBM Granite](https://img.shields.io/badge/IBM_Granite-3.2--2B-purple.svg)](https://huggingface.co/ibm-granite/granite-3.2-2b-instruct)

**An intelligent AI-powered prescription validation and medical safety platform**

[Features](#-key-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

**PharmAI** is a comprehensive end-to-end AI-powered prescription validation and medical safety platform that combines advanced medical datasets, natural language processing, clinical rules, risk analytics, and accessibility features to ensure medication safety and optimize treatment outcomes.

The system leverages **IBM Granite 3.2-2B Instruct** AI model for intelligent prescription text extraction, coupled with extensive medical databases including DrugBank, WHO standards, and regional medicine datasets to provide real-time safety analysis and clinical decision support.

---

## 🎯 Key Features

### 🔍 **Intelligent Drug Extraction**
- **AI-Powered NLP**: Utilizes IBM Granite 3.2-2B Instruct model for advanced prescription text parsing
- **Smart Extraction**: Automatically identifies drug name, dosage, frequency, and administration route
- **Name Normalization**: Standardizes drug names using canonical vocabulary from DrugBank
- **Fallback Mechanism**: Regex-based extraction as backup for enhanced reliability

### ⚠️ **Drug-Drug Interaction Detection**
- **Comprehensive Database**: Scans 53,755+ drug interactions from DrugBank
- **Severity Classification**: Categorizes interactions as Major, Moderate, or Minor
- **Clinical Recommendations**: Provides actionable guidance for detected interactions
- **Real-time Analysis**: Instant validation across multiple medications

### 💊 **Dosage Verification & Validation**
- **Age-Specific Guidelines**: Tailored validation for Pediatric, Adult, and Geriatric populations
- **WHO Standards**: Compares against WHO ATC/DDD (Defined Daily Dose) recommendations
- **Safety Alerts**: Flags subtherapeutic and potentially toxic doses
- **Weight-Based Calculations**: Personalized dosing recommendations

### 🔄 **Alternative Medicine Recommendations**
- **Smart Alternatives**: Suggests safer and cost-effective medication options
- **ATC Classification**: Uses Anatomical Therapeutic Chemical classification system
- **WHO Essential Medicines**: Prioritizes medications from WHO Essential Medicines List
- **Regional Database**: Includes 194+ Indian medicines for localized recommendations

### 📊 **Personalized Risk Prediction**
- **Intelligent Scoring**: Comprehensive 0-100 risk score combining multiple factors
  - Drug Interactions (60% weight)
  - Dosage Deviation (30% weight)
  - Polypharmacy Risk (10% weight)
- **Risk Stratification**: SAFE → LOW → MODERATE → HIGH → DANGEROUS
- **Clinical Context**: Considers patient age, weight, and medical conditions

### 🔊 **Accessibility Features**
- **Speech-to-Text**: OpenAI Whisper integration for voice-based prescriptions
- **Text-to-Speech**: Coqui TTS for audio feedback and instructions
- **Inclusive Design**: Supports visually impaired and low-literacy users
- **Multi-modal Input**: Text, voice, and image-based prescription entry

---

## 🏗️ System Architecture

```
PharmAI/
├── backend/                          # FastAPI Backend Server
│   ├── main.py                      # Application entry point
│   ├── config.py                    # Configuration management
│   │
│   ├── routers/                     # API Route Handlers
│   │   ├── extraction.py           # Drug extraction endpoints
│   │   ├── interactions.py         # Interaction checking
│   │   ├── dosage.py               # Dosage verification
│   │   ├── alternatives.py         # Alternative suggestions
│   │   ├── risk.py                 # Risk prediction
│   │   └── tts.py                  # Text-to-speech services
│   │
│   ├── services/                    # Core Business Logic
│   │   ├── granite_processor.py    # IBM Granite AI integration
│   │   ├── interaction_checker.py  # Interaction detection engine
│   │   ├── dosage_engine.py        # Dosage validation logic
│   │   ├── alternative_engine.py   # Alternative recommendation engine
│   │   ├── risk_predictor.py       # Risk scoring algorithm
│   │   ├── nlp_extractor.py        # NLP processing
│   │   ├── stt_service.py          # Speech-to-text (Whisper)
│   │   └── tts_service.py          # Text-to-speech (Coqui)
│   │
│   ├── models/                      # Data Models
│   │   └── schemas.py              # Pydantic validation schemas
│   │
│   ├── utils/                       # Utility Functions
│   │   ├── normalizer.py           # Drug name normalization
│   │   └── preprocessor.py         # Text preprocessing
│   │
│   ├── data/                        # Medical Datasets
│   │   ├── raw/                    # Original datasets
│   │   │   ├── db_drug_interactions.csv
│   │   │   ├── drugbank_vocabulary.csv
│   │   │   ├── who_atc_ddd.csv
│   │   │   └── A_Z_medicines_dataset_of_India.csv
│   │   │
│   │   ├── processed/              # Preprocessed data
│   │   │   ├── interactions.parquet
│   │   │   ├── vocabulary.parquet
│   │   │   └── canonical_drugs.json
│   │   │
│   │   ├── download_datasets.py    # Dataset acquisition
│   │   ├── generate_datasets.py    # Sample data generation
│   │   └── preprocess_datasets.py  # Data preprocessing pipeline
│   │
│   └── requirements.txt             # Python dependencies
│
├── frontend/                        # Streamlit Frontend
│   ├── app.py                      # Main dashboard
│   ├── pages/                      # Multi-page application
│   │   ├── 1_Interactions.py      # Interaction checker UI
│   │   ├── 2_Dosage_Checker.py    # Dosage verification UI
│   │   ├── 3_Alternative_Medicines.py
│   │   └── 4_Text_Extraction.py   # Prescription extraction UI
│   │
│   └── assets/                     # Static assets
│       ├── css/                    # Custom styling
│       └── logo.png                # Application logo
│
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── start_app.ps1                    # Application launcher
└── README.md                        # This file
```

---

## 📦 Installation

### Prerequisites

- **Python**: 3.10 or higher (Python 3.10.11 recommended)
- **RAM**: 8GB+ (for AI model loading)
- **Disk Space**: 10GB+ (for models and datasets)
- **Internet**: Required for initial model download
- **Hugging Face Account**: For IBM Granite model access

### Step 1: Clone Repository

```bash
git clone https://github.com/Supriya-gouda/PhramAI.git
cd PhramAI
```

### Step 2: Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

**Key Dependencies:**
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `streamlit` - Frontend framework
- `transformers` - Hugging Face transformers
- `torch` - PyTorch for AI models
- `pandas` - Data manipulation
- `pydantic` - Data validation
- `pyarrow` - Fast data serialization
- `openai-whisper` - Speech-to-text (optional)
- `TTS` - Coqui text-to-speech (optional)

### Step 3: Configure Environment

1. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Get Hugging Face Token:**
   - Visit [Hugging Face Tokens](https://huggingface.co/settings/tokens)
   - Create a new token with `read` permission
   - Copy the token (starts with `hf_`)

3. **Accept Model License:**
   - Go to [IBM Granite Model](https://huggingface.co/ibm-granite/granite-3.2-2b-instruct)
   - Click **"Agree and access repository"**

4. **Edit `.env` file:**
   ```env
   HF_TOKEN=hf_your_actual_token_here
   MODEL_NAME=ibm-granite/granite-3.2-2b-instruct
   DEVICE=auto
   BACKEND_PORT=8000
   FRONTEND_PORT=8501
   ```

### Step 4: Prepare Medical Datasets

```bash
# Navigate to data directory
cd backend/data

# Generate sample datasets for testing
python generate_datasets.py

# Preprocess datasets
python preprocess_datasets.py
```

**For Production Use:**
Replace sample datasets in `backend/data/raw/` with authentic medical data:
- DrugBank interaction database
- WHO ATC/DDD standards
- Regional medicine databases
- Essential Medicines List (EML)

---

## 🚀 Quick Start

### Method 1: Automated Launcher (Recommended)

```powershell
.\start_app.ps1
```

This script will:
- ✅ Verify Python installation
- ✅ Check all dependencies
- ✅ Validate data files
- ✅ Start backend server
- ✅ Launch frontend application
- ✅ Open application in browser

### Method 2: Manual Start

**Terminal 1 - Backend Server:**
```bash
cd "d:\AI Medical Prescription\project"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend Application:**
```bash
cd "d:\AI Medical Prescription\project\frontend"
streamlit run app.py --server.port 8501
```

### Access Points

- **Frontend**: [http://localhost:8501](http://localhost:8501)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📖 Usage Guide

### 1. Drug Extraction & Risk Analysis

1. Navigate to **"Text Extraction"** page
2. Input prescription text (typed or pasted)
3. Enter patient details:
   - Age (years)
   - Weight (kg)
4. Click **"Extract & Analyze"**
5. Review comprehensive analysis:
   - Extracted medication details
   - Overall risk score (0-100)
   - Clinical recommendations
   - Safety alerts

### 2. Drug Interaction Check

1. Go to **"Interactions"** page
2. Enter medications (one per line):
   ```
   Aspirin
   Warfarin
   Metformin
   ```
3. Click **"Check Interactions"**
4. Review results:
   - Interaction pairs
   - Severity levels
   - Clinical significance
   - Recommendations

### 3. Dosage Verification

1. Navigate to **"Dosage Checker"**
2. Enter patient information:
   - Age: `45 years`
   - Weight: `70 kg`
3. Input medication details:
   - Drug: `Aspirin`
   - Dose: `100 mg`
   - Frequency: `Once daily`
4. Click **"Verify Dosage"**
5. Compare against WHO DDD standards
6. View age-specific recommendations

### 4. Find Alternative Medicines

1. Go to **"Alternative Medicines"**
2. Enter current medication name
3. Select reason for alternative:
   - Drug interaction
   - Allergy/Intolerance
   - Cost reduction
   - Unavailability
4. View alternative options:
   - WHO Essential Medicines (priority)
   - Therapeutic equivalents
   - Cost-effective options
   - Regional alternatives

---

## 🔧 API Documentation

### REST API Endpoints

#### 1. Extract Medications

**Endpoint:** `POST /extraction/extract`

**Request:**
```json
{
  "text": "Aspirin 100mg once daily, Metformin 500mg twice daily",
  "patient_age": 45,
  "patient_weight_kg": 70
}
```

**Response:**
```json
{
  "medications": [
    {
      "name": "Aspirin",
      "dose": 100,
      "unit": "mg",
      "frequency": "once daily",
      "route": "oral"
    },
    {
      "name": "Metformin",
      "dose": 500,
      "unit": "mg",
      "frequency": "twice daily",
      "route": "oral"
    }
  ],
  "confidence": 0.95
}
```

#### 2. Check Drug Interactions

**Endpoint:** `POST /interactions/check`

**Request:**
```json
{
  "medications": ["Aspirin", "Warfarin", "Clopidogrel"]
}
```

**Response:**
```json
{
  "interactions": [
    {
      "drug_a": "Aspirin",
      "drug_b": "Warfarin",
      "severity": "MAJOR",
      "description": "Increased bleeding risk",
      "recommendation": "Monitor INR closely, consider alternative"
    }
  ],
  "total_interactions": 2,
  "highest_severity": "MAJOR"
}
```

#### 3. Verify Dosage

**Endpoint:** `POST /dosage/verify`

**Request:**
```json
{
  "medication": "Aspirin",
  "prescribed_dose": 100,
  "dose_unit": "mg",
  "frequency": "once daily",
  "patient_age": 45,
  "patient_weight_kg": 70
}
```

**Response:**
```json
{
  "status": "SAFE",
  "who_ddd": 150,
  "prescribed_daily_dose": 100,
  "deviation_percentage": -33.3,
  "age_appropriate": true,
  "recommendation": "Dose within safe range for adult patient"
}
```

#### 4. Get Alternative Medicines

**Endpoint:** `POST /alternatives/suggest`

**Request:**
```json
{
  "medication": "Aspirin",
  "reason": "interaction",
  "patient_age": 45
}
```

**Response:**
```json
{
  "alternatives": [
    {
      "name": "Clopidogrel",
      "atc_class": "B01AC",
      "who_essential": true,
      "cost_ratio": 1.2,
      "recommendation": "First-line alternative antiplatelet"
    }
  ],
  "total_alternatives": 3
}
```

#### 5. Predict Risk Score

**Endpoint:** `POST /risk/predict`

**Request:**
```json
{
  "medications": [
    {"name": "Aspirin", "dose": 100, "unit": "mg"},
    {"name": "Warfarin", "dose": 5, "unit": "mg"}
  ],
  "patient_info": {
    "patient_age": 65,
    "patient_weight_kg": 75,
    "comorbidities": ["hypertension", "diabetes"]
  }
}
```

**Response:**
```json
{
  "risk_score": 72,
  "risk_level": "HIGH",
  "factors": {
    "interaction_risk": 85,
    "dosage_risk": 40,
    "polypharmacy_risk": 60
  },
  "recommendations": [
    "Major drug interaction detected",
    "Close monitoring required",
    "Consider alternative antiplatelet therapy"
  ]
}
```

### Interactive API Documentation

Access comprehensive interactive API documentation at:
**[http://localhost:8000/docs](http://localhost:8000/docs)**

Features:
- Live API testing
- Request/response schemas
- Authentication details
- Code examples in multiple languages

---

## 📊 Medical Datasets

| Dataset | Records | Purpose | Source |
|---------|---------|---------|--------|
| **DrugBank Interactions** | 53,755+ | Drug-drug interaction detection | [DrugBank](https://www.drugbank.ca/) |
| **DrugBank Vocabulary** | 15,000+ | Drug name normalization & mapping | DrugBank |
| **WHO ATC/DDD** | 6,000+ | Anatomical classification & dosing | [WHO](https://www.who.int/tools/atc-ddd-toolkit) |
| **Essential Medicines List** | 500+ | Preferred medication alternatives | WHO EML |
| **Indian Medicines Database** | 194+ | Regional drug information | Public datasets |
| **Drug Use by Age** | 1,000+ | Age-specific utilization patterns | Medical literature |

---

## 🔒 Security & Privacy

- **Data Protection**: All patient data processed locally
- **No Cloud Storage**: Medical information never leaves your infrastructure
- **HIPAA Compliance**: Architecture designed for healthcare compliance
- **Token Security**: Hugging Face tokens stored in `.env` (gitignored)
- **API Authentication**: Ready for OAuth/JWT integration

---

## ⚠️ Important Disclaimer

> **PharmAI is designed for educational, research, and clinical decision support purposes only.**

- ❌ **NOT a substitute** for professional medical advice
- ✅ **Always consult** licensed healthcare professionals
- ✅ **Verify all recommendations** with current medical guidelines
- ❌ **Not FDA approved** for clinical diagnostic use
- ✅ **Use as supplementary tool** in clinical workflow

**Users assume all responsibility for medical decisions based on system outputs.**

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Areas for Contribution

- 🔬 **Medical Datasets**: Expand interaction databases
- 🧠 **AI Models**: Improve NLP extraction accuracy
- 🌍 **Internationalization**: Add multi-language support
- 🎨 **UI/UX**: Enhance user interface design
- 📚 **Documentation**: Improve guides and tutorials
- 🧪 **Testing**: Add unit and integration tests
- 🔧 **Features**: Implement new functionality

### Contribution Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Add docstrings to all functions
- Include type hints
- Write unit tests for new features
- Update documentation

---

## 🛠️ Troubleshooting

### Common Issues

**Issue: Model download fails**
```
Solution: Check internet connection and HF_TOKEN validity
Verify: Visit https://huggingface.co/ibm-granite/granite-3.2-2b-instruct
```

**Issue: Import errors**
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall
```

**Issue: Port already in use**
```bash
# Change ports in .env file
BACKEND_PORT=8001
FRONTEND_PORT=8502
```

**Issue: Slow AI model loading**
```
First run downloads ~4.5GB model - this is normal
Subsequent runs use cached model (faster)
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Technology Partners

- **[IBM Research](https://www.ibm.com/granite)** - Granite AI language model
- **[Hugging Face](https://huggingface.co/)** - Model hosting and transformers library
- **[OpenAI](https://openai.com/)** - Whisper speech recognition
- **[Coqui AI](https://coqui.ai/)** - Text-to-speech synthesis

### Medical Data Sources

- **[World Health Organization (WHO)](https://www.who.int/)** - ATC/DDD standards, Essential Medicines List
- **[DrugBank](https://www.drugbank.ca/)** - Comprehensive pharmaceutical database
- **Public Health Datasets** - Regional medicine information

### Open Source Libraries

- FastAPI, Streamlit, PyTorch, Pandas, Transformers, and many more

---

## 📧 Contact & Support

- **Developer**: Supriya Gouda
- **Repository**: [github.com/Supriya-gouda/PhramAI](https://github.com/Supriya-gouda/PhramAI)
- **Issues**: [Report a bug](https://github.com/Supriya-gouda/PhramAI/issues)
- **Discussions**: [Community forum](https://github.com/Supriya-gouda/PhramAI/discussions)

---

## 🌟 Star History

If you find PharmAI useful, please consider giving it a star ⭐ on GitHub!

---

<div align="center">

**Built with ❤️ for safer prescriptions and better healthcare outcomes**

[![GitHub stars](https://img.shields.io/github/stars/Supriya-gouda/PhramAI?style=social)](https://github.com/Supriya-gouda/PhramAI)
[![GitHub forks](https://img.shields.io/github/forks/Supriya-gouda/PhramAI?style=social)](https://github.com/Supriya-gouda/PhramAI)

</div>

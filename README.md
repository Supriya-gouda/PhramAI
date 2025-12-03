<div align="center">

# PharmAI
### AI-Powered Medical Prescription Safety System

![PharmAI](FrontPage.png)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![IBM Granite](https://img.shields.io/badge/IBM_Granite-3.2--2B-purple.svg)](https://huggingface.co/ibm-granite/granite-3.2-2b-instruct)

**Intelligent prescription validation platform combining AI, medical datasets, and clinical decision support**

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [API](#api-endpoints) • [Contributing](#contributing)

</div>

---

## Overview

PharmAI is an AI-powered prescription safety platform that validates medications, detects drug interactions, verifies dosages, and predicts clinical risks using IBM Granite AI and comprehensive medical databases.

---

## Features

### AI Drug Extraction
- IBM Granite 3.2-2B AI model for intelligent prescription parsing
- Extracts drug name, dosage, frequency, and route of administration
- Drug name normalization using DrugBank vocabulary
- Automatic fallback to regex-based extraction for reliability

### Drug Interaction Detection
- Database of 53,755+ drug-drug interactions from DrugBank
- Severity classification: Major, Moderate, Minor
- Real-time interaction analysis for multiple medications
- Clinical recommendations based on interaction severity

### Dosage Verification
- Validation against WHO ATC/DDD (Defined Daily Dose) standards
- Age-specific dosage recommendations
- Support for Pediatric, Adult, and Geriatric populations
- Automated safety alerts for subtherapeutic or toxic doses

### Alternative Medicine Recommendations
- Suggests safer and cost-effective medication alternatives
- Based on ATC (Anatomical Therapeutic Chemical) classification
- Prioritizes WHO Essential Medicines List
- Includes regional database with 194+ Indian medicines

### Personalized Risk Prediction
- Comprehensive risk scoring from 0-100
- Weighted algorithm: Interactions (60%), Dosage (30%), Polypharmacy (10%)
- Five risk levels: Safe, Low Risk, Moderate Risk, High Risk, Dangerous
- Personalized assessment based on patient age and weight

### Accessibility Features
- Speech-to-Text using OpenAI Whisper for voice prescriptions
- Text-to-Speech using Coqui TTS for audio feedback
- Multi-modal input support (text, voice)
- Designed for visually impaired and low-literacy users

---

## 🏗️ Architecture

```
PharmAI/
├── backend/                     # FastAPI Backend
│   ├── main.py                 # API entry point
│   ├── routers/                # API endpoints
│   ├── services/               # Business logic (AI, interaction checker, etc.)
│   ├── models/                 # Pydantic schemas
│   ├── utils/                  # Utilities (normalizer, preprocessor)
│   └── data/
│       ├── raw/                # Source datasets
│       └── processed/          # Preprocessed data
│
├── frontend/                    # Streamlit UI
│   ├── app.py                  # Main dashboard
│   └── pages/                  # Multi-page app
│
├── .env.example                # Environment template
├── start_app.ps1               # Application launcher
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- 8GB RAM minimum (for AI models)
- Hugging Face account

### Setup Instructions

```bash
# Clone repository
git clone https://github.com/Supriya-gouda/PhramAI.git
cd PhramAI

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add: HF_TOKEN=hf_your_token_here
```

Get your Hugging Face token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

Accept the IBM Granite model license at [IBM Granite Model](https://huggingface.co/ibm-granite/granite-3.2-2b-instruct)

### Data Preparation

```bash
cd backend/data
python preprocess_datasets.py    # Process datasets
```

**Note**: The files `db_drug_interactions.csv` (8MB) and `full database.xml` are excluded from the repository due to size and licensing restrictions. For production use, obtain a DrugBank license and add these files to `backend/data/raw/`

---

## Quick Start
## 🚀 Quick Start

### Launch Application

```powershell
.\start_app.ps1
```

This automated script will:
- Verify Python installation and dependencies
- Check for required data files
- Start backend server at http://127.0.0.1:8000
- Launch frontend application at http://localhost:8501

### Manual Start

**Terminal 1 - Backend:**
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```

### Access Points
- Frontend Application: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## Usage

### Extract and Analyze Prescriptions
1. Navigate to Text Extraction page
2. Enter prescription text and patient information (age, weight)
3. Click Extract and Analyze
4. Review extracted medications, risk score, and recommendations

### Check Drug Interactions
1. Go to Interactions page
2. Enter medications (one per line)
3. Review interaction severity levels and clinical recommendations

### Verify Dosage
1. Open Dosage Checker page
2. Enter patient information and medication details
3. Compare prescribed dose against WHO DDD standards

### Find Alternative Medicines
1. Visit Alternative Medicines page
2. Enter current medication name and reason for alternative
3. Review safer or more cost-effective options

---

## API Endpoints

### Extract Medications
```http
POST /extraction/extract
{
  "text": "Aspirin 100mg once daily",
  "patient_age": 45,
  "patient_weight_kg": 70
}
```

### Check Interactions
```http
POST /interactions/check
{
  "medications": ["Aspirin", "Warfarin"]
}
```

### Verify Dosage
```http
POST /dosage/verify
{
  "medication": "Aspirin",
  "prescribed_dose": 100,
  "dose_unit": "mg",
  "patient_age": 45
}
```

### Predict Risk
```http
POST /risk/predict
{
  "medications": [{"name": "Aspirin", "dose": 100, "unit": "mg"}],
  "patient_info": {"patient_age": 45, "patient_weight_kg": 70}
}
```

Full interactive API documentation available at: http://localhost:8000/docs

---

## Datasets

| Dataset | Records | Purpose |
|---------|---------|---------|
| DrugBank Interactions* | 53,755+ | Drug interaction detection |
| DrugBank Vocabulary | 15,000+ | Drug name normalization |
| WHO ATC/DDD | 6,000+ | Dosage standards |
| Essential Medicines List | 500+ | Alternative recommendations |
| Indian Medicines | 194+ | Regional drug database |

Note: DrugBank interaction data requires a separate license and is not included in this repository.

---

## Disclaimer

This software is for educational and research purposes only.

- Not a substitute for professional medical advice
- Always consult licensed healthcare professionals
- Not FDA approved for clinical use
- Users assume all responsibility for decisions based on system outputs

---

## Contributing
Contributions are welcome. Areas for improvement include:
- Expanding medical datasets
- Improving NLP extraction accuracy
- Adding multi-language support
- Enhancing user interface and experience
- Increasing test coverage

---

## License

MIT License - see LICENSE file for details

---

## Acknowledgments

- IBM Research - Granite AI language model
- Hugging Face - Model hosting and transformers library
- World Health Organization - Medical standards and datasets
- DrugBank - Pharmaceutical interaction database
- OpenAI - Whisper speech recognition
- Coqui AI - Text-to-speech engine

---

## Contact

**Developer**: Supriya Gouda

**Repository**: [github.com/Supriya-gouda/PhramAI](https://github.com/Supriya-gouda/PhramAI)

**Report Issues**: [github.com/Supriya-gouda/PhramAI/issues](https://github.com/Supriya-gouda/PhramAI/issues)

---

<div align="center">

Built for safer prescriptions and better healthcare outcomes

[![GitHub stars](https://img.shields.io/github/stars/Supriya-gouda/PhramAI?style=social)](https://github.com/Supriya-gouda/PhramAI)
[![GitHub forks](https://img.shields.io/github/forks/Supriya-gouda/PhramAI?style=social)](https://github.com/Supriya-gouda/PhramAI)

</div>
</div>

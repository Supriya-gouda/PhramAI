# 💊 PharmAI - AI Medical Prescription Safety System

**PharmAI** is an end-to-end AI-powered prescription validation and medical safety platform that combines medical datasets, AI NLP, clinical rules, risk analytics, and accessibility features.

## 🎯 Key Features

### 1. **NLP-Based Drug Extraction** 🔍
- Extracts drug name, dosage, frequency, and route from prescription text
- Powered by **IBM Granite 3.2-2B Instruct** model
- Normalizes drug names using canonical vocabulary

### 2. **Drug-Drug Interaction Detection** ⚠️
- Detects harmful interactions between medications
- Severity classification: **Major**, **Moderate**, **Minor**
- Uses DrugBank interaction database

### 3. **Dosage Verification** 💊
- Age-specific dosage validation (Pediatric, Adult, Geriatric)
- Compares against WHO ATC/DDD (Defined Daily Dose) standards
- Flags subtherapeutic or toxic doses

### 4. **Alternative Medicine Recommendations** 🔄
- Suggests safer/cost-effective alternatives
- Based on ATC therapeutic classification
- Prioritizes WHO Essential Medicines List (EML)

### 5. **Personalized Risk Prediction** 📊
- **Innovative 0-100 risk score** combining:
  - Interaction risk (60% weight)
  - Dosage deviation (30% weight)
  - Polypharmacy risk (10% weight)
- Risk levels: SAFE → LOW → MODERATE → HIGH → DANGEROUS

### 6. **Accessibility Features** 🔊
- **Speech-to-Text**: OpenAI Whisper for voice prescriptions
- **Text-to-Speech**: Coqui TTS for audio feedback
- Supports visually impaired and low-literacy users

---

## 🏗️ Architecture

```
├── backend/                  # FastAPI Backend
│   ├── main.py              # API server
│   ├── routers/             # API endpoints
│   │   ├── extraction.py    # Drug extraction
│   │   ├── interactions.py  # Interaction checker
│   │   ├── dosage.py        # Dosage verification
│   │   ├── alternatives.py  # Alternative suggestions
│   │   ├── risk.py          # Risk prediction
│   │   └── tts.py           # Text-to-speech
│   ├── services/            # Core logic
│   │   ├── granite_processor.py    # IBM Granite AI
│   │   ├── interaction_checker.py  # Interaction detection
│   │   ├── dosage_engine.py        # Dosage validation
│   │   ├── alternative_engine.py   # Alternatives
│   │   ├── risk_predictor.py       # Risk calculation
│   │   ├── stt_service.py          # Whisper STT
│   │   └── tts_service.py          # Coqui TTS
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── utils/
│   │   ├── normalizer.py    # Drug name normalization
│   │   └── preprocessor.py  # Text preprocessing
│   ├── data/
│   │   ├── raw/             # Raw datasets
│   │   ├── processed/       # Processed datasets
│   │   ├── download_datasets.py
│   │   └── preprocess_datasets.py
│   └── config.py            # Configuration
│
├── frontend/                # Streamlit Frontend
│   ├── app.py              # Main page
│   └── pages/
│       ├── 1_Interactions.py
│       ├── 2_Dosage_Checker.py
│       ├── 3_Alternative_Medicines.py
│       └── 4_Text_Extraction.py
│
├── .env                    # Environment variables (DO NOT COMMIT)
├── .env.example           # Template for .env
└── requirements.txt       # Python dependencies
```

---

## 📦 Installation

### Prerequisites
- Python 3.10.11 (recommended)
- 8GB+ RAM (for AI models)
- Internet connection (first run to download models)

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd "AI Medical Prescription/project"
```

### Step 2: Install Dependencies
```bash
# Install all requirements
pip install -r backend/requirements.txt

# Key packages:
# - fastapi, uvicorn (backend)
# - streamlit (frontend)
# - transformers, torch (AI models)
# - pandas, openpyxl, pyarrow (data processing)
# - whisper (STT - optional)
# - TTS (Coqui TTS - optional)
```

### Step 3: Setup Environment
```bash
# Copy .env.example to .env
copy .env.example .env

# Edit .env and add your Hugging Face token:
HF_TOKEN=your_huggingface_token_here
```

**Get HF Token:** https://huggingface.co/settings/tokens

### Step 4: Prepare Datasets
```bash
# Create sample datasets (for testing)
python backend/data/download_datasets.py --create-samples

# Preprocess datasets
python backend/data/preprocess_datasets.py
```

**For production:** Replace sample datasets in `backend/data/raw/` with real medical datasets:
- `db_drug_interactions.csv`
- `drugbank_vocabulary.csv`
- `who_atc_ddd.csv`
- `EML export.xlsx`
- `A_Z_medicines_dataset_of_India.csv`
- etc.

---

## 🚀 Running the Application

### Start Backend (Terminal 1)
```bash
python backend/main.py
```
Backend will run on: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

### Start Frontend (Terminal 2)
```bash
streamlit run frontend/app.py
```
Frontend will run on: **http://localhost:8501**

---

## 📖 Usage Guide

### 1. **Drug Extraction & Risk Analysis**
1. Navigate to **"Text Extraction"** page
2. Paste prescription text
3. Enter patient age & weight (optional)
4. Click **"Extract & Analyze"**
5. View:
   - Extracted medications
   - Risk score (0-100)
   - Clinical recommendations

### 2. **Interaction Check**
1. Go to **"Interactions"** page
2. Enter medications (one per line)
3. Click **"Check Interactions"**
4. Review severity levels & recommendations

### 3. **Dosage Verification**
1. Go to **"Dosage Checker"**
2. Enter patient info & medication details
3. Click **"Verify Dosage"**
4. Compare against WHO DDD standards

### 4. **Find Alternatives**
1. Go to **"Alternative Medicines"**
2. Enter medication name
3. Select reason (interaction/allergy/cost)
4. View alternative options with EML priority

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Hugging Face Token
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Model Configuration
MODEL_NAME=ibm-granite/granite-3.2-2b-instruct
DEVICE=auto  # auto, cuda, or cpu

# API Ports
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

### Optional Features

#### Enable OpenAI Whisper (STT)
```bash
pip install openai-whisper
```

#### Enable Coqui TTS
```bash
pip install TTS
```

---

## 📊 Datasets

| Dataset | Purpose | Source |
|---------|---------|--------|
| DrugBank Interactions | Drug-drug interactions | DrugBank |
| DrugBank Vocabulary | Drug name normalization | DrugBank |
| WHO ATC/DDD | Dosage standards | WHO |
| Essential Medicines List | Preferred alternatives | WHO |
| Indian Medicines | Regional drug database | Public datasets |
| Drug Use by Age | Age-specific patterns | Medical literature |

---

## 🧪 API Endpoints

### Extraction
```http
POST /extraction/extract
{
  "text": "Aspirin 100mg once daily..."
}
```

### Interactions
```http
POST /interactions/check
{
  "medications": ["Aspirin", "Warfarin"]
}
```

### Dosage
```http
POST /dosage/check
{
  "patient_age": 45,
  "patient_weight_kg": 70,
  "medication": "Aspirin",
  "prescribed_dose": 100,
  "dose_unit": "mg"
}
```

### Risk Prediction
```http
POST /risk/predict
{
  "medications": [
    {"name": "Aspirin", "dose": 100, "unit": "mg"}
  ],
  "patient_info": {"patient_age": 45, "patient_weight_kg": 70}
}
```

Full API docs: **http://localhost:8000/docs**

---

## ⚠️ Disclaimer

**PharmAI is for educational and research purposes only.**

- Not a substitute for professional medical advice
- Always consult licensed healthcare professionals
- Verify all recommendations with current medical guidelines
- Not FDA approved for clinical use

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Expand medical datasets
- Add more interaction rules
- Improve NLP extraction accuracy
- Add multi-language support
- Enhance UI/UX

---

## 📄 License

[Specify your license here]

---

## 🙏 Acknowledgments

- **IBM Granite** - AI language model
- **Hugging Face** - Model hosting
- **OpenAI Whisper** - Speech recognition
- **Coqui TTS** - Text-to-speech
- **WHO** - Medical standards & datasets
- **DrugBank** - Pharmaceutical database

---

## 📧 Contact

For questions or support: [Your contact information]

---

**Built with ❤️ for safer prescriptions**

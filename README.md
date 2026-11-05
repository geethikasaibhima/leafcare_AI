# 🌿 LeafCare AI – Intelligent Plant Disease Detection System

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-MobileNetV2-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

> **LeafCare AI** is a full-stack Computer Vision web application for automatic detection and classification of crop foliage diseases. Combining **OpenCV image preprocessing** and a **MobileNetV2 Deep Convolutional Neural Network**, it supports both file uploads and live camera streaming to diagnose 38 crop pathology conditions across 14 plant species with immediate organic and chemical remedy recommendations.

---

## 📸 Key Features

- **🎯 Dual-Mode AI Scanner:**
  - **File Upload:** Drag-and-drop or browse high-resolution images (`.jpg`, `.png`, `.webp`, `.bmp`).
  - **Live Camera Stream:** Mobile and laptop camera capture with HTML5 `getUserMedia`, camera flip controls (front/rear), and real-time viewfinder reticle.
- **🧠 MobileNetV2 Deep Learning Backbone:**
  - Pretrained on ImageNet and fine-tuned on the canonical **PlantVillage** dataset.
  - Multi-class probabilistic softmax classification across **38 classes**.
  - Top-5 alternative probability distributions displayed for diagnostic transparency.
- **🔬 OpenCV Computer Vision Preprocessing:**
  - Corrupt image decoding checks.
  - Resolution threshold validation (minimum 64×64px).
  - Foliage color ratio and HSV threshold checks (green/yellow/brown hues).
  - Laplacian variance sharpness / blur scoring.
- **🌱 Comprehensive Botanical Knowledge Base:**
  - Detailed symptom descriptions.
  - Organic and biological remedies (neem oil, Bacillus subtilis, Trichoderma, etc.).
  - Approved chemical fungicides and bactericides.
  - Preventative cultural practices (crop rotation, canopy ventilation, drip irrigation).
- **📊 Real-Time Analytics Dashboard:**
  - Total scans counter, healthy vs diseased ratio.
  - Interactive **Chart.js** doughnut charts and crop species distribution bar charts.
  - Recent scan logs.
- **🔐 User Authentication & Persistent History:**
  - Secure user registration, password hashing (`pbkdf2:sha256`), session management.
  - Complete scan history stored in **SQLite** with instant keyword search and status filters.
- **🎨 Premium Botanical Design:**
  - Responsive mobile-first layout with Bootstrap 5.3 and FontAwesome 6 icons.
  - Forest emerald color scheme, smooth card animations, and laser scanning effects.
- **🚀 Production Ready:**
  - Pre-configured for **GitHub** and **Render** cloud deployment (`Procfile`, `render.yaml`, `runtime.txt`).

---

## 🗂️ System Architecture

```
                                  [ User Interface ]
                       (HTML5 + Bootstrap 5.3 + FontAwesome 6)
                         /                               \
               [ File Upload ]                    [ Live Webcam ]
                         \                               /
                          v                             v
                   [ Flask REST Controller (app.py) ]
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
         [ OpenCV Preprocessing ]          [ User Session / Auth ]
         - Decode & sanity check           - Registration & Login
         - Blur / Sharpness score          - SQLite database
         - Foliage ratio (HSV)
                    |
                    v
       [ TensorFlow MobileNetV2 ]
       - 224x224x3 Input Batch
       - Convolutional Feature Extraction
       - Softmax 38-class Probabilities
                    |
                    v
       [ Botanical Diagnostic Engine ]
       - Disease Info Profile Mapping
       - Organic / Chemical Treatments
       - Preventative Guidelines
                    |
                    v
    [ Result Report & Dashboard Analytics ]
```

---

## 🌾 Supported Crops & Diseases (38 PlantVillage Classes)

| Crop | Disease Conditions Covered |
| :--- | :--- |
| **Apple** | Apple Scab, Black Rot, Cedar Apple Rust, Healthy |
| **Blueberry** | Healthy |
| **Cherry** | Powdery Mildew, Healthy |
| **Corn (Maize)** | Cercospora Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy |
| **Grape** | Black Rot, Esca (Black Measles), Leaf Blight (Isariopsis), Healthy |
| **Orange** | Huanglongbing (Citrus Greening) |
| **Peach** | Bacterial Spot, Healthy |
| **Bell Pepper** | Bacterial Spot, Healthy |
| **Potato** | Early Blight, Late Blight, Healthy |
| **Raspberry** | Healthy |
| **Soybean** | Healthy |
| **Squash** | Powdery Mildew |
| **Strawberry** | Leaf Scorch, Healthy |
| **Tomato** | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy |

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/LeafCare-AI.git
cd LeafCare-AI
```

### 2. Create and Activate Virtual Environment
```bash
# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# On Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python app.py
```
Open your browser at **`http://127.0.0.1:5000`**.

> **Demo Credentials:**
> - **Username:** `demo`
> - **Password:** `demo123`

---

## 🧠 Model Training & Fine-Tuning

The model uses MobileNetV2 transfer learning with ImageNet feature weights. To train or fine-tune with your own PlantVillage dataset:

```bash
# Fine-tune on your local PlantVillage directory:
python model/train_mobilenetv2.py --dataset_path /path/to/PlantVillage --epochs 10 --batch_size 32
```

The script automatically preserves class indices, compiles metrics, and outputs the trained `.keras` model directly to `model/plant_disease_model.keras`.

---

## 🌐 Cloud Deployment (Render)

This repository includes turnkey configuration for [Render](https://render.com):

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of LeafCare AI"
   git remote add origin https://github.com/your-username/LeafCare-AI.git
   git push -u origin main
   ```
2. **Deploy on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and click **New + > Web Service**.
   - Connect your `LeafCare-AI` GitHub repository.
   - Settings:
     - **Environment:** `Python`
     - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - Click **Deploy Web Service**!

---

## 🛠️ Project Structure

```
LeafCare-AI/
├── app.py                      # Flask main entry point (routes, auth, prediction API)
├── config.py                   # Central application configuration
├── database.py                 # SQLite database models and queries
├── Procfile                    # Render / Heroku process declaration
├── render.yaml                 # Infrastructure as Code blueprint for Render
├── runtime.txt                 # Python runtime version
├── requirements.txt            # Production Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # Full documentation
│
├── model/
│   ├── plant_disease_model.keras  # Trained MobileNetV2 neural network
│   ├── class_indices.json      # 38 PlantVillage class mappings
│   ├── disease_info.json       # Detailed botanical remedies & symptoms
│   └── train_mobilenetv2.py    # Training & fine-tuning pipeline
│
├── utils/
│   ├── image_processor.py      # OpenCV filtering, validation & normalization
│   └── predictor.py            # Model inference, confidence scoring & top-5
│
├── static/
│   ├── css/style.css           # Premium botanical green stylesheet
│   ├── js/
│   │   ├── scanner.js          # Webcam capture & drag-and-drop handler
│   │   ├── dashboard.js        # Chart.js analytics engine
│   │   └── main.js             # UI animations & flash auto-dismiss
│   ├── images/sample_leaves/   # Demo leaf specimens (Tomato, Corn, Apple)
│   └── uploads/                # Processed diagnostic uploads
│
└── templates/
    ├── base.html               # Master layout with navigation and footer
    ├── index.html              # Hero landing page & 1-click test showcase
    ├── scanner.html            # AI Scanner (Upload + Live Webcam)
    ├── result.html             # Diagnostic report & treatment guide
    ├── dashboard.html          # Pathology statistics & charts
    ├── history.html            # Searchable scan history archive
    ├── login.html              # Authentication sign in
    ├── register.html           # User registration
    └── 404.html                # Custom error page
```

---

## 📜 License & Acknowledgments

- **Dataset:** PlantVillage Dataset by David Hughes & Marcel Salathé.
- **Neural Network:** MobileNetV2 by Google Research.
- **License:** MIT License. Free for academic, educational, and commercial agricultural technology use.

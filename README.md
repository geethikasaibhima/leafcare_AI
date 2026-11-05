# 🌿 LeafCare AI – Intelligent Plant Disease Detection System

[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)


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


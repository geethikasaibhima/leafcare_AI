import os
import json
import numpy as np
from config import Config
from utils.image_processor import preprocess_image, validate_image, get_image_diagnostics

_model = None
_class_indices = None
_disease_info = None

def load_class_indices():
    global _class_indices
    if _class_indices is None:
        if os.path.exists(Config.CLASS_INDICES_PATH):
            with open(Config.CLASS_INDICES_PATH, 'r', encoding='utf-8') as f:
                _class_indices = json.load(f)
        else:
            _class_indices = {}
    return _class_indices

def load_disease_info():
    global _disease_info
    if _disease_info is None:
        if os.path.exists(Config.DISEASE_INFO_PATH):
            with open(Config.DISEASE_INFO_PATH, 'r', encoding='utf-8') as f:
                _disease_info = json.load(f)
        else:
            _disease_info = {}
    return _disease_info

def get_model():
    global _model
    if _model is None:
        if os.path.exists(Config.MODEL_PATH):
            import tensorflow as tf
            try:
                # Load Keras MobileNetV2 model
                _model = tf.keras.models.load_model(Config.MODEL_PATH)
            except Exception as e:
                print(f"[LeafCare AI] Error loading model from {Config.MODEL_PATH}: {e}")
                _model = None
        else:
            print(f"[LeafCare AI] Model file not yet found at {Config.MODEL_PATH}")
            _model = None
    return _model

def format_class_name(raw_name):
    """
    Transforms raw PlantVillage class names into human-readable plant and condition.
    Example: 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot'
    -> ('Corn (Maize)', 'Gray Leaf Spot')
    """
    parts = raw_name.split('___')
    if len(parts) == 2:
        plant_raw, disease_raw = parts
        plant = plant_raw.replace('_', ' ').strip()
        disease = disease_raw.replace('_', ' ').strip()
        if 'healthy' in disease.lower():
            disease = 'Healthy'
        return plant, disease
    return raw_name, "Unknown Condition"

def predict_plant_disease(image_input):
    """
    End-to-end diagnosis pipeline:
    1. Validates image using OpenCV heuristics (dimension, decode, foliage presence)
    2. Gathers visual diagnostics (resolution, sharpness, foliage ratio)
    3. Normalizes and runs inference through MobileNetV2 model
    4. Compiles top prediction, top-5 probabilities, and botanical treatment guide
    
    Returns: (success: bool, result_dict: dict, error_message: str or None)
    """
    is_valid, err_msg, cv_img = validate_image(image_input)
    if not is_valid:
        return False, None, err_msg
        
    diagnostics = get_image_diagnostics(cv_img)
    batch = preprocess_image(cv_img, target_size=Config.IMAGE_SIZE)
    
    model = get_model()
    class_map = load_class_indices()
    disease_info = load_disease_info()
    
    if model is None:
        return False, None, "The plant disease detection model is currently not loaded. Please ensure the model file is generated."
        
    # Model inference
    raw_preds = model.predict(batch, verbose=0)[0]
    predicted_idx = int(np.argmax(raw_preds))
    confidence = float(raw_preds[predicted_idx])
    
    raw_class_name = class_map.get(str(predicted_idx), f"Class_{predicted_idx}")
    
    # Retrieve botanical profile
    info = disease_info.get(raw_class_name, {})
    default_plant, default_disease = format_class_name(raw_class_name)
    
    plant_name = info.get('plant', default_plant)
    disease_name = info.get('disease', default_disease)
    is_healthy = info.get('is_healthy', 'healthy' in raw_class_name.lower())
    severity = info.get('severity', 'None' if is_healthy else 'Moderate')
    pathogen = info.get('pathogen', 'None' if is_healthy else 'Unknown')
    symptoms = info.get('symptoms', 'No detailed symptom record registered for this condition.')
    treatment_organic = info.get('treatment_organic', 'Maintain good organic hygiene, airflow, and soil nutrition.')
    treatment_chemical = info.get('treatment_chemical', 'Consult local agricultural extension service for targeted chemical controls.')
    prevention = info.get('prevention', 'Ensure good canopy airflow, certified seeds, crop rotation, and avoid overhead watering.')
    
    # Extract top 5 predictions for probability distribution
    top5_indices = np.argsort(raw_preds)[-5:][::-1]
    top_alternatives = []
    for idx in top5_indices:
        c_name = class_map.get(str(idx), f"Class_{idx}")
        c_p, c_d = format_class_name(c_name)
        top_alternatives.append({
            'class': c_name,
            'label': f"{c_p} - {c_d}",
            'confidence': round(float(raw_preds[idx]) * 100, 2)
        })
        
    result = {
        'plant_name': plant_name,
        'disease_name': disease_name,
        'raw_class': raw_class_name,
        'confidence': round(confidence * 100, 2),
        'confidence_raw': confidence,
        'is_healthy': is_healthy,
        'severity': severity,
        'pathogen': pathogen,
        'symptoms': symptoms,
        'treatment_organic': treatment_organic,
        'treatment_chemical': treatment_chemical,
        'prevention': prevention,
        'diagnostics': diagnostics,
        'top_alternatives': top_alternatives
    }
    
    return True, result, None

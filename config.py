import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'leafcare-ai-super-secret-botanical-key-2026'
    DATABASE = os.path.join(BASE_DIR, 'leafcare.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
    
    # Model configuration
    MODEL_PATH = os.path.join(BASE_DIR, 'model', 'plant_disease_model.keras')
    CLASS_INDICES_PATH = os.path.join(BASE_DIR, 'model', 'class_indices.json')
    DISEASE_INFO_PATH = os.path.join(BASE_DIR, 'model', 'disease_info.json')
    
    # Input shape for MobileNetV2
    IMAGE_SIZE = (224, 224)

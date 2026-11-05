"""
LeafCare AI - Comprehensive Automated Test Suite
================================================
Tests model inference, OpenCV validation, database operations,
and Flask HTTP endpoints.
"""

import os
import io
import json
import unittest
import base64
import numpy as np
import cv2

# Set test environment
os.environ['SECRET_KEY'] = 'test-secret-key'

from app import app
from database import (
    init_db, create_user, verify_user, save_prediction,
    get_prediction_by_id, get_user_predictions, delete_prediction,
    get_dashboard_stats
)
from utils.image_processor import validate_image, preprocess_image, get_image_diagnostics
from utils.predictor import predict_plant_disease, get_model, load_class_indices

class LeafCareAITestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()

    def setUp(self):
        init_db()

    # 1. Model & Class Indices Verification
    def test_01_model_and_classes(self):
        model = get_model()
        self.assertIsNotNone(model, "Model should be loaded successfully")
        classes = load_class_indices()
        self.assertEqual(len(classes), 38, "Should have all 38 PlantVillage classes mapped")
        self.assertIn("Tomato___Early_blight", classes.values())
        self.assertIn("Corn_(maize)___Common_rust_", classes.values())

    # 2. OpenCV Image Validation
    def test_02_image_validation(self):
        # Test valid botanical image
        sample_path = 'static/images/sample_leaves/tomato_healthy.jpg'
        self.assertTrue(os.path.exists(sample_path), "Sample test image must exist")
        
        is_valid, err, img = validate_image(sample_path)
        self.assertTrue(is_valid, "Valid sample leaf should pass validation")
        self.assertIsNone(err)
        self.assertIsNotNone(img)

        # Test diagnostics
        diag = get_image_diagnostics(img)
        self.assertIn('sharpness', diag)
        self.assertIn('foliage_coverage', diag)

        # Test blank image rejection
        blank = np.zeros((200, 200, 3), dtype=np.uint8)
        is_valid_blank, err_blank, _ = validate_image(blank)
        self.assertFalse(is_valid_blank, "Solid black image should be rejected")

    # 3. Model Inference Pipeline
    def test_03_prediction_pipeline(self):
        sample_path = 'static/images/sample_leaves/tomato_early_blight.jpg'
        success, result, err = predict_plant_disease(sample_path)
        
        self.assertTrue(success, f"Prediction failed with error: {err}")
        self.assertIn('plant_name', result)
        self.assertIn('disease_name', result)
        self.assertIn('confidence', result)
        self.assertIn('treatment_organic', result)
        self.assertIn('treatment_chemical', result)
        self.assertIn('prevention', result)
        self.assertIn('top_alternatives', result)
        self.assertGreater(len(result['top_alternatives']), 0)

    # 4. Database User Authentication
    def test_04_user_auth_database(self):
        test_username = f"tester_{os.urandom(4).hex()}"
        test_email = f"{test_username}@example.com"
        test_pass = "securepass123"

        user = create_user(test_username, test_email, test_pass)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], test_username)

        # Verify password
        verified = verify_user(test_username, test_pass)
        self.assertIsNotNone(verified)
        self.assertEqual(verified['id'], user['id'])

        # Verify wrong password
        wrong = verify_user(test_username, "wrongpass")
        self.assertIsNone(wrong)

    # 5. Database Prediction Operations & Stats
    def test_05_prediction_database_crud(self):
        pred_id = save_prediction(
            user_id=None,
            image_filename="test_scan.jpg",
            plant_name="Tomato",
            disease_name="Early Blight",
            raw_class="Tomato___Early_blight",
            confidence=0.912,
            is_healthy=0,
            symptoms="Target spots",
            treatment="Copper spray",
            prevention="Crop rotation"
        )
        self.assertIsNotNone(pred_id)
        
        pred = get_prediction_by_id(pred_id)
        self.assertIsNotNone(pred)
        self.assertEqual(pred['plant_name'], "Tomato")
        self.assertEqual(pred['disease_name'], "Early Blight")

        stats = get_dashboard_stats()
        self.assertGreaterEqual(stats['total_scans'], 1)

        # Delete
        deleted = delete_prediction(pred_id)
        self.assertTrue(deleted)

    # 6. HTTP Web Endpoints
    def test_06_http_routes(self):
        # Home
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'LeafCare', res.data)

        # Scanner
        res = self.client.get('/scanner')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Intelligent Leaf Scanner', res.data)

        # Dashboard
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Pathology Dashboard', res.data)

        # History
        res = self.client.get('/history')
        self.assertEqual(res.status_code, 200)

        # Health
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'healthy')

        # API Stats
        res = self.client.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('total_scans', data)

    # 7. Prediction Endpoint (Upload)
    def test_07_predict_upload_endpoint(self):
        with open('static/images/sample_leaves/tomato_healthy.jpg', 'rb') as f:
            img_data = f.read()

        data = {
            'image': (io.BytesIO(img_data), 'test_tomato.jpg')
        }
        res = self.client.post('/predict', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        json_res = json.loads(res.data)
        self.assertTrue(json_res['success'])
        self.assertIn('redirect_url', json_res)
        self.assertIn('data', json_res)
        self.assertIn('confidence', json_res['data'])

    # 8. Prediction Endpoint (Live Camera Base64)
    def test_08_predict_camera_endpoint(self):
        with open('static/images/sample_leaves/corn_common_rust.jpg', 'rb') as f:
            img_data = f.read()
        b64_str = "data:image/jpeg;base64," + base64.b64encode(img_data).decode('utf-8')

        res = self.client.post('/predict', data={'camera_image': b64_str})
        self.assertEqual(res.status_code, 200)
        json_res = json.loads(res.data)
        self.assertTrue(json_res['success'])
        self.assertIn('data', json_res)

    # 9. Quick Sample Route
    def test_09_sample_scan_route(self):
        res = self.client.get('/scan_sample/apple_scab.jpg')
        self.assertEqual(res.status_code, 302) # Redirects to result_view

if __name__ == '__main__':
    unittest.main()

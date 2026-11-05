import os
import uuid
import base64
from datetime import datetime, timezone
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)
from werkzeug.utils import secure_filename

from config import Config
from database import (
    init_db, create_user, verify_user, get_user_by_id,
    save_prediction, get_prediction_by_id, get_user_predictions,
    delete_prediction, get_dashboard_stats
)
from utils.predictor import predict_plant_disease, load_disease_info

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database schema on startup
with app.app_context():
    init_db()

# ----------------- Authentication Helpers ----------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    return dict(current_user=user)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ----------------- Routes ----------------- #

@app.route('/')
def index():
    stats = get_dashboard_stats()
    return render_template('index.html', stats=stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
            
        user = create_user(username, email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Registration successful! Welcome to LeafCare AI.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username or Email already registered. Please log in.', 'danger')
            return render_template('register.html')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = verify_user(username_or_email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')
            return render_template('login.html')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Accepts image file upload OR base64 data URI from live camera.
    Processes with OpenCV, runs inference through MobileNetV2,
    saves record in SQLite, and returns JSON response.
    """
    image_bytes = None
    filename = None
    
    # 1. Check for live camera base64 data
    camera_data = request.form.get('camera_image')
    if camera_data and ',' in camera_data:
        try:
            header, encoded = camera_data.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            filename = f"cam_{uuid.uuid4().hex[:10]}.jpg"
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to decode camera capture: {str(e)}'}), 400

    # 2. Check for uploaded file
    if image_bytes is None:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file uploaded.'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image selected.'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file format. Allowed types: PNG, JPG, JPEG, WEBP, BMP.'}), 400
            
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"scan_{uuid.uuid4().hex[:10]}.{ext}"
        image_bytes = file.read()

    # 3. Run prediction pipeline
    success, result, error_msg = predict_plant_disease(image_bytes)
    if not success:
        return jsonify({'success': False, 'error': error_msg}), 422

    # 4. Save image to static/uploads/
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(save_path, 'wb') as f:
        f.write(image_bytes)

    # 5. Save prediction in database
    user_id = session.get('user_id')
    pred_id = save_prediction(
        user_id=user_id,
        image_filename=filename,
        plant_name=result['plant_name'],
        disease_name=result['disease_name'],
        raw_class=result['raw_class'],
        confidence=result['confidence_raw'],
        is_healthy=1 if result['is_healthy'] else 0,
        symptoms=result['symptoms'],
        treatment=f"Organic: {result['treatment_organic']}\nChemical: {result['treatment_chemical']}",
        prevention=result['prevention']
    )

    result['prediction_id'] = pred_id
    result['image_url'] = url_for('static', filename=f'uploads/{filename}')
    result['result_url'] = url_for('result_view', pred_id=pred_id)
    
    return jsonify({
        'success': True,
        'data': result,
        'redirect_url': url_for('result_view', pred_id=pred_id)
    })

@app.route('/result/<int:pred_id>')
def result_view(pred_id):
    pred = get_prediction_by_id(pred_id)
    if not pred:
        flash('Prediction record not found.', 'danger')
        return redirect(url_for('scanner'))
        
    disease_info = load_disease_info()
    info = disease_info.get(pred['raw_class'], {})
    
    return render_template(
        'result.html',
        pred=pred,
        info=info,
        image_url=url_for('static', filename=f'uploads/{pred["image_filename"]}')
    )

@app.route('/scan_sample/<sample_name>')
def scan_sample(sample_name):
    """
    Quick test helper: runs prediction on preloaded demo leaf samples.
    """
    safe_name = secure_filename(sample_name)
    sample_path = os.path.join(app.root_path, 'static', 'images', 'sample_leaves', safe_name)
    if not os.path.exists(sample_path):
        flash('Sample leaf not found.', 'danger')
        return redirect(url_for('scanner'))
        
    with open(sample_path, 'rb') as f:
        img_bytes = f.read()
        
    success, result, err = predict_plant_disease(img_bytes)
    if not success:
        flash(f'Failed to process sample: {err}', 'danger')
        return redirect(url_for('scanner'))
        
    filename = f"sample_{uuid.uuid4().hex[:8]}_{safe_name}"
    dst = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(dst, 'wb') as f:
        f.write(img_bytes)
        
    user_id = session.get('user_id')
    pred_id = save_prediction(
        user_id=user_id,
        image_filename=filename,
        plant_name=result['plant_name'],
        disease_name=result['disease_name'],
        raw_class=result['raw_class'],
        confidence=result['confidence_raw'],
        is_healthy=1 if result['is_healthy'] else 0,
        symptoms=result['symptoms'],
        treatment=f"Organic: {result['treatment_organic']}\nChemical: {result['treatment_chemical']}",
        prevention=result['prevention']
    )
    
    flash(f"Quick diagnostic completed for {result['plant_name']} sample!", 'success')
    return redirect(url_for('result_view', pred_id=pred_id))

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    stats = get_dashboard_stats(user_id=user_id)
    return render_template('dashboard.html', stats=stats)

@app.route('/history')
def history():
    user_id = session.get('user_id')
    predictions = get_user_predictions(user_id=user_id, limit=100)
    return render_template('history.html', predictions=predictions)

@app.route('/delete_prediction/<int:pred_id>', methods=['POST'])
def delete_pred(pred_id):
    user_id = session.get('user_id')
    deleted = delete_prediction(pred_id, user_id=user_id)
    if deleted:
        flash('Diagnostic record removed.', 'info')
    else:
        flash('Could not delete record.', 'danger')
    return redirect(request.referrer or url_for('history'))

@app.route('/api/stats')
def api_stats():
    user_id = session.get('user_id')
    stats = get_dashboard_stats(user_id=user_id)
    # Filter out sqlite3.Row for JSON serialization
    serialized = {
        'total_scans': stats['total_scans'],
        'healthy_scans': stats['healthy_scans'],
        'diseased_scans': stats['diseased_scans'],
        'avg_confidence': stats['avg_confidence'],
        'plants_breakdown': stats['plants_breakdown'],
        'top_diseases': stats['top_diseases']
    }
    return jsonify(serialized)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'app': 'LeafCare AI',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200

# ----------------- Error Handlers ----------------- #
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(413)
def request_entity_too_large(e):
    flash('File too large! Maximum allowed upload size is 16MB.', 'danger')
    return redirect(url_for('scanner'))

@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', content="<div class='container py-5 text-center'><h2>Internal Server Error</h2><p>Something went wrong on our end.</p></div>"), 500

if __name__ == '__main__':
    # Local development server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

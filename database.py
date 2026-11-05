import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_filename TEXT NOT NULL,
            plant_name TEXT NOT NULL,
            disease_name TEXT NOT NULL,
            raw_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            is_healthy INTEGER DEFAULT 0,
            symptoms TEXT,
            treatment TEXT,
            prevention TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# User management functions
def create_user(username, email, password):
    conn = get_db()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username.strip(), email.strip().lower(), password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {'id': user_id, 'username': username, 'email': email}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? COLLATE NOCASE', (username.strip(),))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? COLLATE NOCASE', (email.strip().lower(),))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_user(username, password):
    user = get_user_by_username(username)
    if not user:
        user = get_user_by_email(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

# Prediction management functions
def save_prediction(user_id, image_filename, plant_name, disease_name, raw_class, confidence, is_healthy, symptoms="", treatment="", prevention=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (
            user_id, image_filename, plant_name, disease_name, raw_class, confidence, is_healthy, symptoms, treatment, prevention
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, image_filename, plant_name, disease_name, raw_class, float(confidence), int(is_healthy), symptoms, treatment, prevention))
    conn.commit()
    pred_id = cursor.lastrowid
    conn.close()
    return pred_id

def get_prediction_by_id(pred_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions WHERE id = ?', (pred_id,))
    pred = cursor.fetchone()
    conn.close()
    return pred

def get_user_predictions(user_id=None, limit=50, offset=0):
    conn = get_db()
    cursor = conn.cursor()
    if user_id:
        cursor.execute('''
            SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?
        ''', (user_id, limit, offset))
    else:
        cursor.execute('''
            SELECT * FROM predictions ORDER BY created_at DESC LIMIT ? OFFSET ?
        ''', (limit, offset))
    preds = cursor.fetchall()
    conn.close()
    return preds

def delete_prediction(pred_id, user_id=None):
    conn = get_db()
    cursor = conn.cursor()
    if user_id:
        cursor.execute('DELETE FROM predictions WHERE id = ? AND user_id = ?', (pred_id, user_id))
    else:
        cursor.execute('DELETE FROM predictions WHERE id = ?', (pred_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_dashboard_stats(user_id=None):
    conn = get_db()
    cursor = conn.cursor()
    
    where_clause = "WHERE user_id = ?" if user_id else ""
    params = (user_id,) if user_id else ()
    
    # Total scans
    cursor.execute(f"SELECT COUNT(*) FROM predictions {where_clause}", params)
    total_scans = cursor.fetchone()[0]
    
    # Healthy vs diseased
    healthy_clause = f"WHERE is_healthy = 1 {'AND user_id = ?' if user_id else ''}"
    cursor.execute(f"SELECT COUNT(*) FROM predictions {healthy_clause}", params)
    healthy_scans = cursor.fetchone()[0]
    diseased_scans = total_scans - healthy_scans
    
    # Average confidence
    cursor.execute(f"SELECT AVG(confidence) FROM predictions {where_clause}", params)
    avg_conf = cursor.fetchone()[0]
    avg_confidence = round(float(avg_conf) * 100, 1) if avg_conf else 0.0
    
    # Plant distribution
    cursor.execute(f'''
        SELECT plant_name, COUNT(*) as count 
        FROM predictions {where_clause}
        GROUP BY plant_name 
        ORDER BY count DESC 
        LIMIT 6
    ''', params)
    plants_breakdown = [{'name': r['plant_name'], 'count': r['count']} for r in cursor.fetchall()]
    
    # Top detected diseases (excluding healthy)
    disease_filter = f"WHERE is_healthy = 0 {'AND user_id = ?' if user_id else ''}"
    cursor.execute(f'''
        SELECT disease_name, plant_name, COUNT(*) as count 
        FROM predictions {disease_filter}
        GROUP BY disease_name, plant_name 
        ORDER BY count DESC 
        LIMIT 5
    ''', params)
    top_diseases = [{'name': f"{r['plant_name']} - {r['disease_name']}", 'count': r['count']} for r in cursor.fetchall()]
    
    # Recent scans
    cursor.execute(f'''
        SELECT * FROM predictions {where_clause}
        ORDER BY created_at DESC 
        LIMIT 5
    ''', params)
    recent_scans = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_scans': total_scans,
        'healthy_scans': healthy_scans,
        'diseased_scans': diseased_scans,
        'avg_confidence': avg_confidence,
        'plants_breakdown': plants_breakdown,
        'top_diseases': top_diseases,
        'recent_scans': recent_scans
    }

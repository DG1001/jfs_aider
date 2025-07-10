from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import threading
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

def cleanup_old_images():
    while True:
        time.sleep(2)  # Check every 2 seconds
        data = load_data()
        now = datetime.now()
        updated = False
        
        for image in data[:]:
            upload_time = datetime.fromisoformat(image['timestamp'])
            elapsed = (now - upload_time).total_seconds()
            if elapsed > 15:  # 5s visible + 10s fadeout
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image['filename']))
                except FileNotFoundError:
                    pass
                data.remove(image)
                updated = True
        
        if updated:
            save_data(data)

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_images, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    comment = request.form.get('comment', '')[:100]  # Limit to 100 chars
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        timestamp = datetime.now().isoformat()
        filename = secure_filename(f"{timestamp}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        data = load_data()
        data.append({
            'filename': filename,
            'comment': comment,
            'timestamp': timestamp
        })
        
        # Keep only last 10 images
        if len(data) > 10:
            data = data[-10:]
        
        save_data(data)
    
    return redirect(url_for('gallery'))

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/images')
def api_images():
    data = load_data()
    now = datetime.now()
    
    for image in data:
        upload_time = datetime.fromisoformat(image['timestamp'])
        elapsed = (now - upload_time).total_seconds()
        image['status'] = 'visible' if elapsed < 5 else 'fading' if elapsed < 15 else 'expired'
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000)

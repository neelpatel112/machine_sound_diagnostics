from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import librosa
import soundfile as sf
from sklearn.preprocessing import StandardScaler
import pickle
import os
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'ogg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route 1: Serve the homepage
@app.route('/')
def home():
    try:
        return send_file('index.html')
    except:
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>Machine Sound Diagnostics</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>🔊 Machine Sound Diagnostics</h1>
            <p>ML Backend is running successfully!</p>
            <p>Try the <a href="/health">health check</a> or use the API endpoints.</p>
        </body>
        </html>
        '''

# Route 2: Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Try to load models to verify they work
        scaler_path = 'scaler.pkl'
        model_path = 'model.pkl'
        
        health_status = {
            "status": "healthy",
            "message": "API is running",
            "endpoints": {
                "GET /health": "Health check",
                "POST /predict": "Audio analysis",
                "GET /": "Homepage"
            },
            "models": {
                "scaler": "Found" if os.path.exists(scaler_path) else "Not found",
                "model": "Found" if os.path.exists(model_path) else "Not found"
            }
        }
        return jsonify(health_status)
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "error": str(e),
            "message": "API is running but some components may have issues"
        }), 500

# Route 3: Main prediction endpoint (YOUR EXISTING CODE - KEEP THIS)
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed. Use WAV, MP3, FLAC"}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > MAX_FILE_SIZE:
            return jsonify({"error": "File too large. Max 16MB"}), 400
        
        # Save temporary file
        filename = secure_filename(file.filename)
        temp_path = os.path.join('/tmp', filename)
        file.save(temp_path)
        
        # YOUR EXISTING AUDIO PROCESSING CODE HERE
        # Load audio file
        audio, sample_rate = librosa.load(temp_path, sr=None)
        
        # Extract features (example - use your actual feature extraction)
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
        mfccs_mean = np.mean(mfccs.T, axis=0)
        
        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        chroma_mean = np.mean(chroma.T, axis=0)
        
        mel = librosa.feature.melspectrogram(y=audio, sr=sample_rate)
        mel_mean = np.mean(mel.T, axis=0)
        
        # Combine features
        features = np.concatenate([mfccs_mean, chroma_mean, mel_mean])
        features = features.reshape(1, -1)
        
        # Load scaler and model
        try:
            with open('scaler.pkl', 'rb') as f:
                scaler = pickle.load(f)
            features_scaled = scaler.transform(features)
            
            with open('model.pkl', 'rb') as f:
                model = pickle.load(f)
            
            prediction = model.predict(features_scaled)
            probabilities = model.predict_proba(features_scaled)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Return result
            result = {
                "status": "success",
                "prediction": str(prediction[0]),
                "confidence": float(np.max(probabilities)),
                "probabilities": probabilities[0].tolist(),
                "message": "Analysis complete"
            }
            return jsonify(result)
            
        except FileNotFoundError as e:
            # Models not found - return demo response
            return jsonify({
                "status": "demo_mode",
                "prediction": "normal_operation",
                "confidence": 0.85,
                "message": "Using demo mode - models not loaded",
                "note": "Upload model.pkl and scaler.pkl for real predictions"
            })
            
    except Exception as e:
        error_details = traceback.format_exc()
        return jsonify({
            "error": "Processing failed",
            "details": str(e),
            "message": "Check audio format and try again"
        }), 500

# Route 4: Serve static files (if needed)
@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_file(path)
    except:
        return jsonify({"error": "File not found"}), 404

# For Vercel deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 
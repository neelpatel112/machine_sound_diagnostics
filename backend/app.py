from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import librosa
import soundfile as sf
import pickle
import os
from werkzeug.utils import secure_filename
import traceback
import io

app = Flask(__name__)
CORS(app)  # Allow requests from your Vercel frontend

# Configuration
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_features(audio_path):
    """Extract audio features for ML model"""
    try:
        # Load audio
        audio, sr = librosa.load(audio_path, sr=22050)
        
        # Extract features (same as your training)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        mfccs_scaled = np.mean(mfccs.T, axis=0)
        
        # Add more features
        chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
        chroma_scaled = np.mean(chroma.T, axis=0)
        
        mel = librosa.feature.melspectrogram(y=audio, sr=sr)
        mel_scaled = np.mean(mel.T, axis=0)
        
        # Combine features
        features = np.hstack([mfccs_scaled, chroma_scaled, mel_scaled])
        return features.reshape(1, -1)
        
    except Exception as e:
        raise Exception(f"Feature extraction failed: {str(e)}")

@app.route('/')
def home():
    return jsonify({
        "service": "Machine Sound Diagnostics API",
        "status": "running",
        "endpoints": {
            "POST /predict": "Analyze audio file",
            "GET /health": "Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Machine Sound Diagnostics ML Backend"
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if audio file is provided
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": "File type not supported",
                "supported": list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = f"/tmp/{filename}"
        file.save(temp_path)
        
        # Extract features
        features = extract_features(temp_path)
        
        # Load models
        try:
            # Load scaler
            with open('ML_Model/scaler.pkl', 'rb') as f:
                scaler = pickle.load(f)
            
            # Load model
            with open('ML_Model/model.pkl', 'rb') as f:
                model = pickle.load(f)
            
            # Scale features and predict
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)
            probabilities = model.predict_proba(features_scaled)
            
            # Get confidence
            confidence = float(np.max(probabilities))
            
            # Map prediction to human-readable label
            class_labels = {
                0: "Normal Operation",
                1: "Bearing Fault",
                2: "Misalignment",
                3: "Looseness",
                4: "Wear"
            }
            
            prediction_label = class_labels.get(prediction[0], f"Class {prediction[0]}")
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify({
                "status": "success",
                "prediction": prediction_label,
                "confidence": round(confidence * 100, 2),
                "class_id": int(prediction[0]),
                "probabilities": probabilities[0].tolist(),
                "message": "Analysis complete"
            })
            
        except FileNotFoundError as e:
            # Models not found - demo mode
            return jsonify({
                "status": "demo_mode",
                "prediction": "Normal Operation",
                "confidence": 85.5,
                "message": "Running in demo mode (models not loaded)",
                "note": "Upload model.pkl and scaler.pkl to ML_Model folder"
            })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")
        return jsonify({
            "error": "Processing failed",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 
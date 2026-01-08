
import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from src import config, preprocess
import tempfile
import uuid

app = Flask(__name__)

# Load Model
MODEL_PATH = config.MODEL_SAVE_PATH
# Fallback if model in config doesn't exist but local checks do
# Fallback if model in config doesn't exist but local checks do
if not os.path.exists(MODEL_PATH):
    if os.path.exists("model.h5"):
        MODEL_PATH = "model.h5"
    elif os.path.exists("final_model.h5"):
        MODEL_PATH = "final_model.h5"
    elif os.path.exists("finalminorproject/final_model.h5"):
        MODEL_PATH = "finalminorproject/final_model.h5"
    elif os.path.exists("finalminorproject/model.h5"):
        MODEL_PATH = "finalminorproject/model.h5"

print(f"Loading model from {MODEL_PATH}...")
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# =======================================================
# NEW: In-App Update API
# =======================================================
@app.route('/api/version', methods=['GET'])
def get_version():
    """
    Returns the latest version info.
    Mobile App checks this to decide if it needs to update.
    """
    return jsonify({
        # UPDATE THIS NUMBER when you upload a new APK.
        # It must be higher than the version on the user's phone.
        "version_code": 2,          
        
        # Display name shown to the user
        "version_name": "1.1.0",    
        
        # Direct link to the APK file in the 'static' folder
        # Replace 'rudragamerz-mechanic-fault-detector' with your actual space name if different
        "apk_url": "https://rudragamerz-mechanic-fault-detector.hf.space/static/app-release.apk",
        
        "force_update": False
    })

# =======================================================
# SHARED LOGIC
# =======================================================
def run_prediction_logic():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Use System Temp Dir (Compatible with Cloud & Local)
    temp_path = os.path.join(tempfile.gettempdir(), f"temp_{uuid.uuid4()}.wav")
    
    try:
        file.save(temp_path)
        
        # Preprocess
        audio = preprocess.load_audio(temp_path)
        if audio is None:
             return jsonify({"error": "Could not load audio"}), 400

        features = preprocess.extract_features(audio)
        features = np.expand_dims(features, axis=0) # Add batch dimension

        # Resize if needed (Matching inference.py logic)
        if features.shape[1:3] != config.INPUT_SHAPE[0:2]:
            features = tf.image.resize(features, (config.INPUT_SHAPE[0], config.INPUT_SHAPE[1])).numpy()

        # Predict
        prediction = model.predict(features, verbose=0)
        score = float(prediction[0][0]) # Convert to float for JSON serialization logic

        if score > 0.5:
            confidence = score * 100
            label = "FAULT DETECTED"
            is_fault = True
        else:
            confidence = (1 - score) * 100
            label = "NORMAL"
            is_fault = False

        result = {
            "label": label,
            "confidence": confidence,
            "score": score,
            "is_fault": is_fault
        }
        
        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        # Safe delete attempt
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Warning: Could not remove temp file {temp_path}: {e}")

# =======================================================
# ROUTES
# =======================================================

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    print("DEBUG: /predict Handling Request")
    return run_prediction_logic()

@app.route('/', methods=['GET', 'POST'])
def root():
    print(f"DEBUG: Root Route Request. Method: {request.method}")
    if request.method == 'POST':
        # If the App sends data to the root URL, handle it as a prediction!
        return run_prediction_logic()
    else:
        # If accessed via Browser, show status
        return jsonify({
            "status": "Running",
            "message": "Mechanic Fault Detector Server is Online",
            "usage": "Send POST request to /predict (or this root URL) with 'file' parameter."
        })

if __name__ == '__main__':
    # Clean up temp file on startup if exists
    if os.path.exists("temp_upload.wav"):
        try:
            os.remove("temp_upload.wav")
        except:
            pass

    # Start ngrok tunnel
    try:
        from pyngrok import ngrok
        # Open a HTTP tunnel on the default port 5000
        public_url = ngrok.connect(5000).public_url
        print("\n" + "="*50)
        print(f"🌍 PUBLIC URL: {public_url}")
        print("Copy this URL into your Android App to connect from ANYWHERE!")
        print("="*50 + "\n")
    except Exception as e:
        print(f"\n⚠️ Ngrok error: {e}")
        print("Could not start public tunnel. You will need to use Local IP.")

    # Host 0.0.0.0 allows access from external IPs (like Android on same WiFi)
    app.run(host='0.0.0.0', port=5000)

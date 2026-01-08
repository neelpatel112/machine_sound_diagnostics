from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "service": "Machine Sound Diagnostics API",
        "status": "running",
        "endpoints": ["GET /", "GET /health", "POST /predict"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "API is working"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 400
        
        # For now, just acknowledge receipt
        return jsonify({
            "status": "success",
            "message": "Audio received (ML coming soon)",
            "prediction": "demo_mode"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Railway specific - use PORT from environment
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import traceback

app = Flask(__name__)
CORS(app)

# ========== ROUTE 1: Homepage ==========
@app.route('/')
def home():
    try:
        # Try to serve the index.html file
        return send_file('index.html')
    except:
        # Fallback if index.html doesn't exist
        return '''
        <html>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1>Machine Sound Diagnostics</h1>
            <p>Backend is running!</p>
            <p>Use <a href="/health">/health</a> to check API status</p>
        </body>
        </html>
        '''

# ========== ROUTE 2: Health Check ==========
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "running",
        "message": "Machine Sound Diagnostics API",
        "endpoints": {
            "GET /": "Homepage",
            "GET /health": "Health check",
            "POST /predict": "Analyze audio file"
        }
    })

# ========== ROUTE 3: Predict ==========
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if file was uploaded
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # YOUR ML CODE GOES HERE
        # For now, return a demo response
        return jsonify({
            "status": "success",
            "message": "Audio received (ML processing placeholder)",
            "prediction": "normal_operation",
            "confidence": 0.92,
            "note": "Add your ML model code here"
        })
        
    except Exception as e:
        return jsonify({
            "error": "Processing failed",
            "details": str(e)
        }), 500

# ========== For Vercel ==========
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, jsonify, send_file
import os

app = Flask(__name__)

# SIMPLE ROUTE 1: Homepage
@app.route('/')
def home():
    try:
        # Try to send index.html
        return send_file('index.html')
    except Exception as e:
        # If error, show simple HTML
        return f'''
        <html>
        <head><title>Machine Sound Diagnostics</title></head>
        <body style="font-family: Arial; padding: 50px;">
            <h1>Machine Sound Diagnostics</h1>
            <p>Backend is starting up...</p>
            <p>Debug: {str(e)}</p>
            <p>Check <a href="/health">/health</a></p>
        </body>
        </html>
        '''

# SIMPLE ROUTE 2: Health check
@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "service": "Machine Sound Diagnostics",
        "version": "1.0"
    })

# SIMPLE ROUTE 3: Echo test
@app.route('/test')
def test():
    return jsonify({"message": "API is working!"})

# Vercel needs this
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
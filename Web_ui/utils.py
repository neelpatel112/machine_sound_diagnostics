"""
Utility functions for Machine Sound Diagnostics Web UI
"""

import streamlit as st
from datetime import datetime
import json
import os

def save_analysis_result(result, save_dir="results"):
    """Save analysis result to JSON file"""
    os.makedirs(save_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{save_dir}/analysis_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    return filename

def load_recent_results(limit=10, save_dir="results"):
    """Load recent analysis results"""
    if not os.path.exists(save_dir):
        return []
    
    files = sorted(os.listdir(save_dir), reverse=True)
    results = []
    
    for file in files[:limit]:
        if file.endswith('.json'):
            try:
                with open(os.path.join(save_dir, file), 'r') as f:
                    results.append(json.load(f))
            except:
                continue
    
    return results

def validate_audio_file(file_bytes, filename):
    """Basic audio file validation"""
    if not filename.lower().endswith('.wav'):
        return False, "File must be .wav format"
    
    # Check file size (max 10MB)
    if len(file_bytes) > 10 * 1024 * 1024:
        return False, "File too large (max 10MB)"
    
    # Check minimum size (at least 1KB)
    if len(file_bytes) < 1024:
        return False, "File too small"
    
    return True, "Valid audio file"

def get_api_status(api_url):
    """Check if backend API is available"""
    try:
        import requests
        response = requests.get(f"{api_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False 
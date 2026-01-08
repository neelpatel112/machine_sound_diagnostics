import gradio as gr
import requests
import io
import time
from datetime import datetime
import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ========== CONFIGURATION ==========
BACKEND_URL = "http://localhost:8000"  # Change to your backend URL
# ===================================

# Custom CSS for better UI
custom_css = """
<style>
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}
.container {
    padding: 20px !important;
}
.card {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    border-left: 5px solid #4CAF50;
}
.header {
    text-align: center;
    margin-bottom: 30px;
}
.upload-area {
    border: 3px dashed #4CAF50;
    border-radius: 15px;
    padding: 40px;
    text-align: center;
    background: #f0f8f0;
}
.result-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.success { color: #4CAF50; font-weight: bold; }
.warning { color: #FF9800; font-weight: bold; }
.danger { color: #f44336; font-weight: bold; }
.metric-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    margin: 10px;
}
</style>
"""

# ========== ANALYSIS FUNCTION ==========
def analyze_audio(audio_file):
    """Process uploaded audio file"""
    if audio_file is None:
        return None, None, "Please upload an audio file first."
    
    # Get file info
    filename = audio_file.name if hasattr(audio_file, 'name') else "recording.wav"
    
    try:
        # Simulate API call (replace with actual)
        # For now, return simulated results
        time.sleep(2)  # Simulate processing
        
        # Simulated response (replace with: requests.post(BACKEND_URL, files=files))
        simulated_response = {
            "status": "success",
            "prediction": "FAULT DETECTED",
            "confidence": 0.87,
            "fault_type": "Bearing Wear",
            "severity": "Medium",
            "recommendation": "Schedule maintenance within 2 weeks. Monitor vibration levels.",
            "timestamp": datetime.now().isoformat()
        }
        
        # Create visualization
        fig = create_visualization(simulated_response)
        
        # Format results
        results_html = format_results(simulated_response)
        
        return results_html, fig, "Analysis complete!"
        
    except Exception as e:
        error_msg = f"Error analyzing audio: {str(e)}"
        return None, None, error_msg

def create_visualization(results):
    """Create Plotly visualization"""
    confidence = results.get("confidence", 0) * 100
    
    fig = go.Figure()
    
    # Gauge chart
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=confidence,
        title={'text': "Confidence Level"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4CAF50"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"},
                {'range': [80, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "black"}
    )
    
    return fig

def format_results(results):
    """Format results as HTML"""
    prediction = results.get("prediction", "UNKNOWN")
    confidence = results.get("confidence", 0) * 100
    fault_type = results.get("fault_type", "N/A")
    severity = results.get("severity", "N/A")
    recommendation = results.get("recommendation", "")
    
    # Color based on prediction
    if "FAULT" in prediction.upper():
        status_color = "danger"
        status_icon = "⚠️"
    else:
        status_color = "success"
        status_icon = "✅"
    
    # Color based on severity
    if severity.upper() == "HIGH":
        severity_color = "danger"
    elif severity.upper() == "MEDIUM":
        severity_color = "warning"
    else:
        severity_color = "success"
    
    html = f"""
    <div class="result-card">
        <h2>{status_icon} Analysis Results</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
            <div class="metric-box">
                <h3>Status</h3>
                <h2 class="{status_color}">{prediction}</h2>
            </div>
            
            <div class="metric-box">
                <h3>Confidence</h3>
                <h2>{confidence:.1f}%</h2>
            </div>
            
            <div class="metric-box">
                <h3>Fault Type</h3>
                <h3>{fault_type}</h3>
            </div>
            
            <div class="metric-box">
                <h3>Severity</h3>
                <h2 class="{severity_color}">{severity}</h2>
            </div>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <h3>📋 Recommendation</h3>
            <p>{recommendation}</p>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 8px;">
            <h4>⚡ Recommended Actions:</h4>
            <ul>
                {"<li><strong>Stop machine</strong> if safe to do so</li>" if severity.upper() == "HIGH" else ""}
                <li>Schedule maintenance{" <strong>immediately</strong>" if severity.upper() == "HIGH" else " within 1 week"}</li>
                <li>Monitor machine performance</li>
                <li>Document this analysis</li>
            </ul>
        </div>
    </div>
    """
    
    return html

# ========== GRADIO UI ==========
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div class="header">
        <h1 style="color: #4CAF50;">🔊 Machine Sound Diagnostics</h1>
        <p style="color: #666; font-size: 1.2em;">AI-Powered Machine Fault Detection from Audio</p>
        <hr style="border: 2px solid #4CAF50; width: 80px;">
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("""
            <div class="card">
                <h3>📋 How to Use</h3>
                <ol>
                    <li><strong>Record</strong> machine sound (10-30 seconds)</li>
                    <li><strong>Save</strong> as .wav file (16kHz recommended)</li>
                    <li><strong>Upload</strong> using the uploader</li>
                    <li><strong>Analyze</strong> for faults</li>
                    <li><strong>Review</strong> detailed results</li>
                </ol>
                
                <h3>📝 Requirements</h3>
                <ul>
                    <li>.wav format only</li>
                    <li>1-60 seconds duration</li>
                    <li>Clear audio (minimal noise)</li>
                    <li>Max file size: 10MB</li>
                </ul>
            </div>
            """)
            
            # Connection status
            status_box = gr.Textbox(
                label="🔗 Backend Status",
                value="Using simulated data. Connect to your backend in code.",
                interactive=False
            )
            
            # Backend URL input
            backend_url = gr.Textbox(
                label="Backend API URL",
                value=BACKEND_URL,
                interactive=True
            )
            
            # Test connection button
            test_btn = gr.Button("Test Connection", variant="secondary")
            
        with gr.Column(scale=2):
            # Upload section
            gr.HTML('<div class="upload-area"><h2>📤 Upload Audio File</h2><p>Drag & drop or click to browse</p></div>')
            
            audio_input = gr.Audio(
                label="Machine Sound Recording",
                type="filepath",
                sources=["upload"],
                interactive=True
            )
            
            # Analyze button
            analyze_btn = gr.Button(
                "🔬 Analyze for Faults",
                variant="primary",
                size="lg"
            )
    
    # Results section
    with gr.Row():
        results_html = gr.HTML(label="Analysis Results")
    
    with gr.Row():
        plot_output = gr.Plot(label="Confidence Visualization")
    
    # Status message
    status_output = gr.Textbox(label="Status", interactive=False)
    
    # Footer
    gr.HTML(f"""
    <div style="text-align: center; margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
        <p>🕒 Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>🔧 Machine Sound Diagnostics v1.0 • Built with Gradio</p>
        <p>⚠️ <strong>Note:</strong> This is a UI demo. Connect to your ML backend by updating the API endpoint in the code.</p>
    </div>
    """)
    
    # Event handlers
    analyze_btn.click(
        fn=analyze_audio,
        inputs=[audio_input],
        outputs=[results_html, plot_output, status_output]
    )
    
    def test_connection(url):
        try:
            # Test if URL is reachable
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return f"✅ Connected to {url}"
            else:
                return f"❌ Connection failed: {response.status_code}"
        except Exception as e:
            return f"❌ Cannot connect: {str(e)}"
    
    test_btn.click(
        fn=test_connection,
        inputs=[backend_url],
        outputs=[status_output]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(debug=True, share=False)
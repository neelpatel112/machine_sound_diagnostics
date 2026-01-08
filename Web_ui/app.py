import streamlit as st
import requests
import io
import time
from datetime import datetime
import plotly.graph_objects as go
import base64
import json

# ========== CONFIGURATION ==========
# SET THIS TO YOUR BACKEND URL
BACKEND_URL = "http://localhost:8000"  # Default for local FastAPI
# For Hugging Face: "https://yourusername-api.hf.space"
# ===================================

# Page setup
st.set_page_config(
    page_title="Machine Sound Diagnostics",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 1rem;
    }
    
    /* Cards */
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #45a049, #3d8b40);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Upload area */
    .uploadedFile {
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f0f8f0;
        margin: 1rem 0;
    }
    
    /* Metrics */
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-top: 4px solid #4CAF50;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'api_status' not in st.session_state:
    st.session_state.api_status = "Not checked"

# ========== HEADER ==========
st.title("🔊 Machine Sound Diagnostics")
st.markdown("### AI-Powered Machine Fault Detection from Audio")
st.markdown("---")

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("⚙️ Configuration")
    
    # Backend URL input
    backend_url = st.text_input(
        "Backend API URL",
        value=BACKEND_URL,
        help="URL of your ML backend server"
    )
    
    # Test connection
    if st.button("🔗 Test Connection", use_container_width=True):
        with st.spinner("Testing connection..."):
            try:
                response = requests.get(f"{backend_url}/health", timeout=5)
                if response.status_code == 200:
                    st.session_state.api_status = "Connected ✅"
                    st.success("Backend connected successfully!")
                else:
                    st.session_state.api_status = f"Error: {response.status_code}"
                    st.error(f"Connection failed: {response.status_code}")
            except Exception as e:
                st.session_state.api_status = f"Failed: {str(e)}"
                st.error(f"Cannot connect: {str(e)}")
    
    st.caption(f"Status: {st.session_state.api_status}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📋 Instructions")
    st.markdown("""
    1. **Record** machine sound (10-30 seconds)
    2. **Save** as .wav file (16kHz recommended)
    3. **Upload** using the button below
    4. **Analyze** for faults
    5. **Review** detailed report
    """)
    
    st.info("""
    **Supported:**
    • WAV format
    • 1-60 seconds audio
    • All machine types
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== MAIN CONTENT ==========
tab1, tab2, tab3 = st.tabs(["🎤 Upload & Analyze", "📊 Results", "📜 History"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📤 Upload Audio")
        
        # Upload section
        audio_file = st.file_uploader(
            "Choose a WAV file",
            type=["wav"],
            help="Upload machine sound recording in WAV format"
        )
        
        if audio_file is not None:
            st.markdown('<div class="uploadedFile">', unsafe_allow_html=True)
            
            # Audio player
            st.audio(audio_file)
            
            # File info
            file_size = len(audio_file.getvalue()) / 1024
            st.caption(f"**File:** {audio_file.name}")
            st.caption(f"**Size:** {file_size:.1f} KB")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Analyze button
            analyze_btn = st.button(
                "🔬 Analyze for Faults",
                type="primary",
                use_container_width=True,
                disabled=(st.session_state.api_status != "Connected ✅")
            )
        else:
            st.info("👆 Upload a .wav file to begin analysis")
            analyze_btn = False
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Quick Guide")
        
        st.markdown("""
        **Best Practices:**
        
        🔊 **Recording Tips:**
        - Place microphone close to machine
        - Record for 10+ seconds
        - Minimize background noise
        - Include normal operation sounds
        
        ⚠️ **Common Fault Sounds:**
        - Grinding → Bearing wear
        - Knocking → Valve issues
        - Squealing → Belt problems
        - Hissing → Leaks
        
        📈 **Accuracy:**
        - Model trained on valve sounds
        - Expanding to other components
        - More data = better results
        """)
        
        # Quick actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Sample Report", use_container_width=True):
                st.session_state.demo_mode = True
        with col_b:
            if st.button("🔄 Clear All", use_container_width=True):
                st.session_state.analysis_history = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if 'analysis_results' in st.session_state and st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("📋 Analysis Report")
        
        # Status banner
        if results.get("prediction") == "FAULT":
            st.error("## ⚠️ FAULT DETECTED")
        else:
            st.success("## ✅ NO FAULT DETECTED")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Prediction", results.get("prediction", "Unknown"))
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            confidence = results.get("confidence", 0) * 100
            st.metric("Confidence", f"{confidence:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Fault Type", results.get("fault_type", "N/A"))
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Severity", results.get("severity", "N/A"))
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed analysis
        with st.expander("🔍 Detailed Analysis", expanded=True):
            col_a, col_b = st.columns(2)
            
            with col_a:
                # Confidence gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=confidence,
                    title={'text': "Detection Confidence"},
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
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_b:
                # Recommendations
                st.subheader("📋 Recommendations")
                st.markdown(results.get("recommendation", "No specific recommendation available."))
                
                st.subheader("⚡ Immediate Actions")
                if results.get("severity") == "High":
                    st.warning("""
                    - **Stop machine** if safe to do so
                    - **Schedule immediate maintenance**
                    - **Monitor closely** for changes
                    """)
                elif results.get("severity") == "Medium":
                    st.info("""
                    - **Schedule maintenance** within 1 week
                    - **Increase monitoring** frequency
                    - **Order replacement parts**
                    """)
                else:
                    st.success("""
                    - **Continue normal operation**
                    - **Monitor during next routine check**
                    - **No immediate action needed**
                    """)
        
        # Raw API response
        with st.expander("📄 Raw API Response"):
            st.json(results)
    
    else:
        st.info("👈 Upload and analyze an audio file to see results here")
        # Demo data for testing
        if st.button("Load Sample Data for Testing"):
            st.session_state.analysis_results = {
                "prediction": "FAULT",
                "confidence": 0.87,
                "fault_type": "Bearing Wear",
                "severity": "Medium",
                "recommendation": "Schedule maintenance within 2 weeks. Monitor temperature and vibration.",
                "timestamp": datetime.now().isoformat()
            }
            st.rerun()

with tab3:
    st.header("📜 Analysis History")
    
    if st.session_state.analysis_history:
        for i, analysis in enumerate(reversed(st.session_state.analysis_history[-10:])):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**File:** {analysis.get('filename', 'Unknown')}")
                    st.caption(f"Time: {analysis.get('timestamp', 'Unknown')}")
                with col2:
                    pred = analysis.get('prediction', 'Unknown')
                    if pred == "FAULT":
                        st.error(pred)
                    else:
                        st.success(pred)
                with col3:
                    if st.button(f"View #{len(st.session_state.analysis_history)-i}", key=f"view_{i}"):
                        st.session_state.analysis_results = analysis
                        st.switch_page("?tab=Results")
                st.markdown("---")
        
        # Clear history
        if st.button("Clear History", type="secondary"):
            st.session_state.analysis_history = []
            st.rerun()
    else:
        st.info("No analysis history yet. Upload files to build history.")

# ========== FOOTER ==========
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption(f"🕒 Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with footer_col2:
    st.caption("🔧 Machine Sound Diagnostics v1.0")
with footer_col3:
    st.caption("📧 Need help? Check GitHub repository")

# ========== API CALL FUNCTION ==========
def analyze_audio(file_bytes, filename, api_url):
    """Send audio to backend API for analysis"""
    try:
        # Prepare the file
        files = {"file": (filename, file_bytes, "audio/wav")}
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Sending to API...")
        progress_bar.progress(30)
        
        # Make API request
        response = requests.post(f"{api_url}/predict", files=files, timeout=30)
        
        status_text.text("Processing audio...")
        progress_bar.progress(60)
        
        if response.status_code == 200:
            progress_bar.progress(90)
            result = response.json()
            
            # Add metadata
            result["filename"] = filename
            result["timestamp"] = datetime.now().isoformat()
            
            # Save to history
            st.session_state.analysis_history.append(result)
            
            status_text.text("Complete!")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            return result
        else:
            st.error(f"API Error: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None
    finally:
        # Clean up
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()

# ========== PROCESS ANALYSIS ==========
if analyze_btn and audio_file is not None:
    # Store results in session state
    st.session_state.analysis_results = analyze_audio(
        audio_file.getvalue(),
        audio_file.name,
        backend_url
    )
    
    # Switch to results tab
    st.switch_page("?tab=Results") 
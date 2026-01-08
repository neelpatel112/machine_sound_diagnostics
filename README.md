# Machine Sound Diagnostics 🔊⚙️

**Machine Sound Diagnostics** is a machine fault detection system that analyzes sound recordings to determine if a machine has a fault or not. The project includes a Python-based ML backend and a full Android application that sends `.wav` audio recordings to the backend for analysis.

🌐 **GitHub Repository:**  
https://github.com/Rudrapatel330/machine-sound-diagnostics.git

---

## 📌 Overview

This project uses sound recordings to detect machine faults. An Android app captures or uploads `.wav` audio files of machine sounds and sends them to a Python backend, where machine learning detects whether a fault is present.

The backend is deployed on platforms such as Hugging Face Spaces, and the Android app communicates via API.

---

## 💡 Features

### 🔹 Machine Learning Backend
- Python-based sound classification model
- Takes `.wav` audio as input
- Uses audio preprocessing techniques (MFCC, spectrogram, etc.)
- Predicts Fault / No Fault
- Easily expandable to multiple machine parts

### 📱 Android Application
- Records or uploads `.wav` machine audio
- Sends audio data to ML backend server
- Displays prediction results in app UI

---

## 📁 Project Structure
machine-sound-diagnostics/
├── android_app/ # Full Android application
├── ml_backend/ # Python ML training + prediction + server code
├── .gitignore
└── README.md


---

## 🚀 How It Works

1. User selects or records machine sound (.wav) in the Android app  
2. App sends `.wav` file to the backend server API  
3. Python backend loads model and predicts fault status  
4. Result is returned to the app and displayed to the user  

---

## 🧠 Technologies Used

| Component        | Tech Stack                                      |
|------------------|--------------------------------------------------|
| Mobile App       | Android (Kotlin / Java)                          |
| Backend API      | Python (FastAPI / Flask / HuggingFace Spaces)     |
| Audio Processing | Librosa, NumPy                                   |
| Machine Learning | TensorFlow / PyTorch (model training)             |

---

## 📦 Installation

### 1) Clone Repository

```bash
git clone https://github.com/Rudrapatel330/machine-sound-diagnostics.git
cd machine-sound-diagnostics
```
Python Backend:

cd ml_backend
pip install -r requirements.txt

To run server locally:
python server_app.py

Android App:
Import the android_app/ folder into Android Studio
Build & run on your device/emulator

📋 Notes:
The current model has been trained only on valve sound data — it may not detect faults in all machine parts yet.

To improve accuracy, collect more diverse machine sound samples and retrain the model.

Ensure the Android app sends .wav audio in the correct format supported by the preprocessing code.

🧪 Usage

Open Android app

Record or choose a sound .wav file

Upload to server

View prediction: Fault / No Fault

📁 Dataset Suggestions

To improve the model, you can gather:

Normal machine sounds

Faulty machine sounds from various components

Valve, motor, pump, gear, belt, etc.




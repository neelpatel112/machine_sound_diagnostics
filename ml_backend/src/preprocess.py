
import librosa
import numpy as np
import os
import tensorflow as tf
from src import config

def load_audio(file_path):
    """Loads an audio file and resizes/pads it to the fixed duration."""
    try:
        audio, _ = librosa.load(file_path, sr=config.SAMPLE_RATE, duration=config.DURATION)
        
        # Pad or truncate to ensure consistent length
        target_length = int(config.SAMPLE_RATE * config.DURATION)
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            audio = audio[:target_length]
            
        return audio
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_features(audio):
    """Converts audio waveform to Mel Spectrogram."""
    mel_spec = librosa.feature.melspectrogram(
        y=audio, 
        sr=config.SAMPLE_RATE, 
        n_mels=config.N_MELS, 
        n_fft=config.N_FFT, 
        hop_length=config.HOP_LENGTH
    )
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # Normalize to mean 0, std 1 (Standardization)
    mel_spec_db = (mel_spec_db - np.mean(mel_spec_db)) / (np.std(mel_spec_db) + 1e-8)
    
    # Add channel dimension
    mel_spec_db = mel_spec_db[..., np.newaxis]
    return mel_spec_db

def preprocess_dataset(dataset_path):
    """
    Scans the dataset directory for 'normal' and 'abnormal' folders recursively.
    Returns X (features) and y (labels).
    Label mapping: normal -> 0, abnormal -> 1
    """
    X = []
    y = []
    groups = [] # To store machine IDs
    
    # ... (existing setup)
    
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            # ... (counter logic)
            if file.endswith(".wav"):
                file_path = os.path.join(root, file)
                
                # Determine label from parent folder name
                parent_folder = os.path.basename(root).lower()
                
                # Determine Machine ID (Grandparent folder)
                # ex: dataset/valve/id_00/normal -> id_00
                machine_id = os.path.basename(os.path.dirname(root))
                
                if parent_folder == "normal":
                    label = 0
                elif parent_folder == "abnormal" or "fault" in parent_folder:
                    label = 1
                else:
                    continue 
                
                audio = load_audio(file_path)
                if audio is not None:
                    features = extract_features(audio)
                    # ... (resize logic)
                    if features.shape[1] != config.INPUT_SHAPE[1]:
                         features = tf.image.resize(features, (config.INPUT_SHAPE[0], config.INPUT_SHAPE[1])).numpy()
                    
                    X.append(features)
                    y.append(label)
                    groups.append(machine_id)
                    
    X = np.array(X)
    y = np.array(y)
    groups = np.array(groups)
    
    print(f"Processed {len(X)} samples.")
    print(f"Machine IDs found: {np.unique(groups)}")
    return X, y, groups


import numpy as np
import sys
from src import preprocess

file_path = r"d:\finalminorproject\dataset\valve\id_00\normal\00000000.wav"
if len(sys.argv) > 1:
    file_path = sys.argv[1]

print(f"Checking {file_path}...")
audio = preprocess.load_audio(file_path)
print(f"Audio shape: {audio.shape}, Min: {audio.min()}, Max: {audio.max()}")

features = preprocess.extract_features(audio)
print(f"Features shape: {features.shape}")
print(f"Features Min: {np.min(features)}, Max: {np.max(features)}, Mean: {np.mean(features)}")
print(f"Has NaNs: {np.isnan(features).any()}")

# Print a small patch
print("Top-left 5x5 patch:")
print(features[0:5, 0:5, 0])

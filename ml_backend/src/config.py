
import os

# Audio configurations
SAMPLE_RATE = 22050
DURATION = 5  # seconds
N_MELS = 128
HOP_LENGTH = 512
N_FFT = 2048

# Dataset configurations
DATASET_PATHS = [
    r"d:\finalminorproject\dataset",
    r"d:\finalminorproject\dataset2",
    r"d:\finalminorproject\dataset3"
]
INPUT_SHAPE = (128, 216, 1) # (N_MELS, TimeSteps, Channels) - Approximate for 5s @ 22050Hz with hop 512

# Training configurations
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
MODEL_SAVE_PATH = "model.h5"
TFLITE_MODEL_PATH = "model.tflite"

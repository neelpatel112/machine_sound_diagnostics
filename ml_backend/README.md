# Machine Fault Detection System

This project detects machine faults (Normal vs Abnormal) from audio recordings using a CNN model. It exports the trained model to TFLite for Android deployment.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: You may need to install `libsndfile` manually if using Windows (often handled by `pysoundfile` or `librosa`).*

## Folder Structure
Ensure your data is in `dataset/` folder. The script expects subfolders labeled with "normal" or "abnormal" (case-insensitive) somewhere in their path.
Example:
```
dataset/
    valve/
        id_00/
            normal/
                00001.wav
            abnormal/
                00001.wav
```

## Usage

### 1. Train the Model
This will scan the `dataset` folder, train the model, and save `model.h5` and `model.tflite`.
```bash
python -m src.train
```
**Options:**
- `--dataset "path/to/dataset"`: Specify a different dataset path.
- `--resume`: Load the existing `model.h5` and continue training (Incremental Learning).

### 2. Run Inference
Test the model on a specific audio file.
```bash
python -m src.inference path/to/audio/file.wav
```

## Android Integration
Use the generated `model.tflite` file in your Android project. 
- **Input**: `(1, 128, 216, 1)` (float32) - Mel Spectrogram
- **Output**: `(1, 1)` (float32) - Probability (0=Normal, 1=Abnormal)

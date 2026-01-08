import tensorflow as tf
import numpy as np

# Configuration - MUST MATCH ANDROID EXACTLY
SAMPLE_RATE = 22050
DURATION_SEC = 5.08  # 112128 samples / 22050
INPUT_LENGTH = 112128
N_FFT = 2048
HOP_LENGTH = 512
N_MELS = 128
FMIN = 0.0
FMAX = SAMPLE_RATE / 2.0

def get_preprocessing_model(base_model_path=None):
    """
    Wraps a base model with audio preprocessing layers.
    Input: Raw Audio (Batch, 112128)
    Output: Classification
    """
    # 1. Input Layer: Raw Audio
    input_audio = tf.keras.layers.Input(shape=(INPUT_LENGTH,), dtype=tf.float32, name='input_audio')
    
    # 2. STFT
    # Result: (Batch, Time, Freq) -> (Batch, 216, 1025)
    stft = tf.signal.stft(
        input_audio,
        frame_length=N_FFT,
        frame_step=HOP_LENGTH,
        fft_length=N_FFT
    )
    
    # 3. Magnitude Spectrogram
    spectrogram = tf.abs(stft)
    
    # 4. Mel Filterbank
    # Note: tf.signal.linear_to_mel_weight_matrix uses range [0, sample_rate/2] by default
    # Slaney vs HTK might differ slightly in implementation details in TF vs Librosa.
    # But usually TF's implementation is robust enough for retraining.
    num_spectrogram_bins = stft.shape[-1]
    
    linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins=N_MELS,
        num_spectrogram_bins=num_spectrogram_bins,
        sample_rate=SAMPLE_RATE,
        lower_edge_hertz=FMIN,
        upper_edge_hertz=FMAX 
    )
    
    # (Batch, Time, Freq) x (Freq, Mel) -> (Batch, Time, Mel)
    mel_spectrogram = tf.tensordot(spectrogram, linear_to_mel_weight_matrix, 1)
    
    # Set static shape (TensorDot can lose it)
    mel_spectrogram.set_shape(spectrogram.shape[:-1].concatenate(linear_to_mel_weight_matrix.shape[-1:]))
    
    # 5. Log Mel Spectrogram (Clamped for numerical stability)
    log_mel_spectrogram = tf.math.log(mel_spectrogram + 1e-6)
    
    # 6. MFCC (Optional - if your old model used MFCC, use this. If MelSpec, stop here.)
    # The user's code suggests Mel Spectrogram input of shape [1, 128, 216, 1].
    # Current shape: (Batch, 216, 128) i.e. (Time, Mel).
    # Need to verify if Model expects (Freq, Time) or (Time, Freq).
    # Android code was sending (Freq=128, Time=216).
    # Let's Transpose to match (Freq, Time).
    
    # (Batch, Time, Mel) -> (Batch, Mel, Time)
    log_mel_spectrogram = tf.transpose(log_mel_spectrogram, perm=[0, 2, 1])
    
    # Add Channel dimension: (Batch, Mel, Time, 1) matches [1, 128, 216, 1]
    output_spec = tf.expand_dims(log_mel_spectrogram, -1)
    
    # 7. Connect to Base Model (CNN)
    # If you have an existing trained Keras model:
    # base_model = tf.keras.models.load_model(base_model_path)
    # outputs = base_model(output_spec)
    
    # For DEMO, we create a simple CNN that matches the shape.
    # REPLACE THIS with your actual loaded model!
    x = tf.keras.layers.Conv2D(32, 3, activation='relu')(output_spec)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    outputs = tf.keras.layers.Dense(2, activation='softmax')(x)
    
    full_model = tf.keras.Model(inputs=input_audio, outputs=outputs)
    return full_model

def convert_to_tflite(model, filename="model_with_preprocessing.tflite"):
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # Key: Enable TF Ops (Flex) might be needed for Signal ops, 
    # BUT standard STFT is supported in TFLite now (mostly).
    # If standard conversion fails, enable SELECT_TF_OPS.
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS, # Try standard first
        tf.lite.OpsSet.SELECT_TF_OPS # Fallback to Flex
    ]
    tflite_model = converter.convert()
    
    with open(filename, 'wb') as f:
        f.write(tflite_model)
    print(f"Saved {filename}")

if __name__ == "__main__":
    print("Creating model with in-graph preprocessing...")
    model = get_preprocessing_model()
    model.summary()
    convert_to_tflite(model)
    print("DONE. Deploy this model to Android and send RAW AUDIO.")


    import argparse
    import numpy as np
    import tensorflow as tf
    import os
    from src import config, preprocess

    def predict_single(file_path, model):
        file_path = file_path.strip().strip('"').strip("'")
        
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found: {file_path}")
            return
            
        if os.path.isdir(file_path):
            print(f"❌ Error: '{file_path}' is a folder, not a file. Please enter a path to a .wav file.")
            return

        print(f"Processing {file_path}...")
        audio = preprocess.load_audio(file_path)
        if audio is None:
            print("❌ Error: Could not load audio file.")
            return
            
        features = preprocess.extract_features(audio)
        features = np.expand_dims(features, axis=0) # Add batch dimension
        
        # Resize if needed
        if features.shape[1:3] != config.INPUT_SHAPE[0:2]:
            features = tf.image.resize(features, (config.INPUT_SHAPE[0], config.INPUT_SHAPE[1])).numpy()

        prediction = model.predict(features, verbose=0)
        score = prediction[0][0]
        
        # Calculate Confidence for the predicted class
        if score > 0.5:
            confidence = score * 100
            label = "🔴 MACHINE STATUS: FAULT DETECTED (Abnormal)"
        else:
            confidence = (1 - score) * 100
            label = "🟢 MACHINE STATUS: OK (Normal)"
        
        # Clear Binary Output
        print("\n" + "="*30)
        print(f" Confidence Score: {int(confidence)}%")
        print("="*30)
        print(label)
        print("="*30 + "\n")

    def main():
        parser = argparse.ArgumentParser(description="Predict Machine Fault from Audio")
        parser.add_argument("--model", type=str, default=config.MODEL_SAVE_PATH, help="Path to saved model")
        # File is optional now
        parser.add_argument("file", type=str, nargs='?', help="Path to the wav file")
        
        args = parser.parse_args()
        
        print(f"Loading model from {args.model}...")
        try:
            model = tf.keras.models.load_model(args.model)
        except:
            print("Model not found. Please train the model first.")
            return

        # If file provided in args, run that input
        if args.file:
            predict_single(args.file, model)
        else:
            # Interactive Mode
            print("\n--- Interactive Inference Mode ---")
            print("Enter path to audio file (or 'q' to quit)")
            while True:
                user_input = input("\nPath: ")
                if user_input.lower() in ['q', 'quit', 'exit']:
                    break
                if user_input.strip() == "":
                    continue
                predict_single(user_input, model)

    if __name__ == "__main__":
        main()

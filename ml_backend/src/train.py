
import os
import argparse
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from src import config, preprocess, model as model_module

def train(dataset_path, resume=False):
    all_X = []
    all_y = []
    
    # Handle single string or list of paths
    if isinstance(dataset_path, str):
        dataset_paths = [dataset_path]
    else:
        dataset_paths = dataset_path
        
    all_groups = []
    
    # Handle single string or list of paths
    if isinstance(dataset_path, str):
        dataset_paths = [dataset_path]
    else:
        dataset_paths = dataset_path
        
    for path in dataset_paths:
        print(f"Loading data from {path}...")
        results = preprocess.preprocess_dataset(path)
        # Check if existing preprocess handles 2 or 3 returns
        if len(results) == 3:
            X, y, groups = results
        else:
            X, y = results
            groups = np.array(["unknown"] * len(y))

        if len(X) > 0:
            all_X.append(X)
            all_y.append(y)
            # Prefix groups with path hash to ensure distinctness across datasets
            path_prefix = str(hash(path) % 10000) 
            distinct_groups = [f"{path_prefix}_{g}" for g in groups]
            all_groups.append(distinct_groups)
            
    if not all_X:
        print("No data found in any dataset paths!")
        return

    X = np.concatenate(all_X, axis=0)
    y = np.concatenate(all_y, axis=0)
    groups = np.concatenate(all_groups, axis=0)
    
    print(f"Total Combined Data: {len(X)} samples")
    print(f"Global Distribution: {np.unique(y, return_counts=True)}")
    print(f"Unique Machine Groups: {len(np.unique(groups))}")

    # Split into train and validation using GROUPS
    # This prevents 'Leakage' where same machine appears in both train and test.
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, val_idx = next(gss.split(X, y, groups))
    
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    groups_train, groups_val = groups[train_idx], groups[val_idx]
    
    print(f"Training on {len(np.unique(groups_train))} machines, Validation on {len(np.unique(groups_val))} machines.")
    
    # --- OVERSAMPLING (Better than Class Weights) ---
    # Separate classes
    bool_train_labels = y_train != 0
    pos_features = X_train[bool_train_labels]
    neg_features = X_train[~bool_train_labels]
    pos_labels = y_train[bool_train_labels]
    neg_labels = y_train[~bool_train_labels]

    ids = np.arange(len(pos_features))
    choices = np.random.choice(ids, len(neg_features)) # Sample positive class to match negative size
    
    res_pos_features = pos_features[choices]
    res_pos_labels = pos_labels[choices]
    
    res_X_train = np.concatenate([res_pos_features, neg_features], axis=0)
    res_y_train = np.concatenate([res_pos_labels, neg_labels], axis=0)
    
    # Shuffle
    order = np.arange(len(res_y_train))
    np.random.shuffle(order)
    X_train = res_X_train[order]
    y_train = res_y_train[order]
    
    print(f"Oversampled Training Data: {len(X_train)} samples")
    # ------------------------------------------------
    
    # 2. Setup Model
    if resume:
        if os.path.exists("latest_" + config.MODEL_SAVE_PATH):
            print(f"Resuming training from latest_" + config.MODEL_SAVE_PATH + "...")
            model = tf.keras.models.load_model("latest_" + config.MODEL_SAVE_PATH)
        elif os.path.exists(config.MODEL_SAVE_PATH):
            print(f"Resuming training from " + config.MODEL_SAVE_PATH + "...")
            model = tf.keras.models.load_model(config.MODEL_SAVE_PATH)
        else:
            print("No saved model found to resume. Creating new model...")
            model = model_module.create_model()
    else:
        print("Creating new model...")
        model = model_module.create_model()
        
    model.summary()
    
    # 3. Train
    print("Starting training...")
    
    # Checkpoint Callback - Saves "model.h5" (Best) AND "latest_model.h5" (Every Epoch)
    checkpoint_best = tf.keras.callbacks.ModelCheckpoint(
        filepath=config.MODEL_SAVE_PATH, 
        save_best_only=True,
        monitor='val_accuracy',
        mode='max',
        verbose=1
    )
    
    checkpoint_latest = tf.keras.callbacks.ModelCheckpoint(
        filepath="latest_" + config.MODEL_SAVE_PATH, 
        save_best_only=False, # Save every epoch
        save_freq='epoch',
        verbose=1
    )

    # Custom Callback to save epoch number
    class TrainingStateCallback(tf.keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs=None):
            with open("training_state.txt", "w") as f:
                f.write(str(epoch + 1))
                
    state_cb = TrainingStateCallback()

    initial_epoch = 0
    if resume and os.path.exists("training_state.txt"):
        try:
            with open("training_state.txt", "r") as f:
                initial_epoch = int(f.read().strip())
            print(f"Resuming from Epoch {initial_epoch}...")
        except:
            print("Could not read training state. Starting from Epoch 0.")

    history = model.fit(
        X_train, y_train,
        initial_epoch=initial_epoch,
        epochs=config.EPOCHS, # Will run until Epoch 50
        batch_size=config.BATCH_SIZE,
        validation_data=(X_val, y_val),
        callbacks=[checkpoint_best, checkpoint_latest, state_cb]
    )
    
    # 4. Save Final Model (Overwrites Best? No, keep Best)
    # But usually final model is good to have.
    print(f"Saving final model to final_{config.MODEL_SAVE_PATH}...")
    model.save(f"final_{config.MODEL_SAVE_PATH}")
    
    # 5. Convert to TFLite
    print(f"Converting to TFLite at {config.TFLITE_MODEL_PATH}...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    
    with open(config.TFLITE_MODEL_PATH, 'wb') as f:
        f.write(tflite_model)
        
    print("Training and export complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Audio Fault Detection Model")
    parser.add_argument("--dataset", nargs='+', default=config.DATASET_PATHS, help="Path(s) to dataset directory. Can verify multiple.")
    parser.add_argument("--resume", action="store_true", help="Resume training from existing model")
    
    args = parser.parse_args()
    
    train(args.dataset, args.resume)


import os

dataset_path = r"d:\finalminorproject\dataset"
print(f"Scanning {dataset_path}...")

counts = {0: 0, 1: 0}
paths = {0: [], 1: []}

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.endswith(".wav"):
            parent_folder = os.path.basename(root).lower()
            
            if parent_folder == "normal":
                label = 0
            elif parent_folder == "abnormal" or "fault" in parent_folder:
                label = 1
            else:
                print(f"Skipping ambiguous folder: {parent_folder}")
                continue
            
            counts[label] += 1
            if len(paths[label]) < 3:
                paths[label].append(os.path.join(root, file))

print("Counts:", counts)
print("Sample Normal:", paths[0])
print("Sample Abnormal:", paths[1])

# Import YOLO
from ultralytics import YOLO

# Define paths
DATASET_PATH = "/home/livnsense/Projects/BPRD_usecase/training/data.yaml"  # Path to data.yaml
SAVE_MODEL_PATH = "/home/livnsense/Projects/BPRD_usecase/training"  # Folder to save trained model

# Create folder if it doesn't exist
import os
os.makedirs(SAVE_MODEL_PATH, exist_ok=True)

# Load YOLOv8 model
model = YOLO("/home/livnsense/Projects/BPRD_usecase/inference/models/updated_2_best_yolov8.pt")

# Train YOLOv8 model
model.train(
    data=DATASET_PATH,  # Path to data.yaml
    epochs=100,          # Number of training epochs
    batch=16,           # Batch size
    imgsz=640,         # Image size
    save=True,          # Save the model
    project=SAVE_MODEL_PATH,  # Save model in Google Drive
    # dfl=1.5,  # Enable focal loss
    name="no_helmet_imp_base_run_3"  # Name of the training run
)

print(f"Training Complete! Model saved at: {SAVE_MODEL_PATH}/YOLOv8_Custom")

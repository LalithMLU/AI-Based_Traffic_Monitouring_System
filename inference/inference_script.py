import cv2
import torch
import numpy as np
import os
from ultralytics import YOLO

# Load the trained YOLOv8 model
model = YOLO('G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\models\\best_v8m.pt')
 
# Define class labels and corresponding colors
labels = ['person', 'car', 'bike', 'auto', 'bus', 'livestock', 'helmet', 'no_helmet', 'truck', 'number_plate']
colors = {
    'person': (0, 255, 0),        # Green
    'car': (255, 0, 0),           # Blue
    'bike': (0, 0, 255),          # Red
    'auto': (255, 255, 0),        # Cyan
    'bus': (255, 165, 0),         # Orange
    'livestock': (128, 0, 128),   # Purple
    'helmet': (0, 255, 255),      # Yellow
    'no_helmet': (0, 100, 255),   # Dark Orange
    'truck': (139, 69, 19),       # Brown
    'number_plate': (255, 20, 147) # Pink
}
 
# Input and output directories
input_folder = "G:\desktop\MyProjects\DL_projects\BPRD_usecase\inference\input_videos\input_videos_10-04-2025"
output_folder = "/home/livnsense/Projects/BPRD_usecase/inference/output_videos/output_videos_hit_n_run_10-04-2025"
 
# Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)
 
# Process each video in the input folder
for video_file in os.listdir(input_folder):
    if video_file.endswith(('.mp4', '.avi', '.MOV')):
        input_path = os.path.join(input_folder, video_file)
        output_filename = f'output_{os.path.splitext(video_file)[0]}.mp4'  # Ensure .mp4 format
        output_path = os.path.join(output_folder, output_filename)
       
        # Open video capture and define video writer
        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
       
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
           
            # Run inference
            results = model(frame)[0]
           
            # Loop through detections
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
                conf = box.conf[0].item()  # Confidence score
                cls = int(box.cls[0].item())  # Class index
                label = labels[cls]
                color = colors.get(label, (255, 255, 255))  # Default to white if label not found
               
                # Draw bounding box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
           
            # Write frame to output video
            out.write(frame)
       
        # Release resources
        cap.release()
        out.release()
        print(f'Processed: {video_file} -> {output_path}')
 
print('Processing complete!')
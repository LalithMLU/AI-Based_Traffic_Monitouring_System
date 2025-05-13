# # incidents display


# import streamlit as st
# import cv2
# import os
# import time
# from ultralytics import YOLO
# import numpy as np
# from collections import defaultdict
# from datetime import datetime
# from PIL import Image

# # Paths
# model_path = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\models\\updated_4_best_yolov8.pt'
# video_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\input_videos\\input_videos_10-04-2025'
# output_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\output_videos\\output_videos_15-04-2025'
# base_incident_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\incidents_clips'
# incident_dir = os.path.join(base_incident_dir, 'incidents_clips_15-04-2025_9188')

# # New: Create subfolders
# frames_dir = os.path.join(incident_dir, "frames")
# clips_dir = os.path.join(incident_dir, "clips")
# os.makedirs(frames_dir, exist_ok=True)
# os.makedirs(clips_dir, exist_ok=True)
# os.makedirs(output_dir, exist_ok=True)
# os.makedirs(incident_dir, exist_ok=True)

# # Labels & Colors
# labels = ['person', 'car', 'bike', 'auto', 'bus', 'livestock', 'helmet', 'no_helmet', 'truck', 'number_plate']
# colors = {
#     'person': (0, 255, 0), 'car': (255, 0, 0), 'bike': (0, 0, 255), 'auto': (255, 255, 0),
#     'bus': (255, 165, 0), 'livestock': (128, 0, 128), 'helmet': (0, 255, 255),
#     'no_helmet': (0, 100, 255), 'truck': (139, 69, 19), 'number_plate': (255, 20, 147)
# }

# # Load YOLO model
# model = YOLO(model_path)

# # Streamlit Sidebar Navigation
# st.sidebar.title("🧭 Navigation")
# selected_tab = st.sidebar.radio("Go to", ["Live Inference", "Incidents", "Map"])

# # Live Inference
# if selected_tab == "Live Inference":
#     st.title("🚦Traffic Inference Dashboard")
#     video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.MOV'))]
#     selected_video = st.selectbox("🎥 Select Input Video", video_files)
#     confidence_threshold = st.slider("📏 Confidence Threshold", 0.0, 1.0, 0.3, step=0.05)
#     label_filter = st.multiselect("🏷️ Filter by Label", labels, default=labels)
#     start_inference = st.button("▶️ Start Inference")

#     if start_inference:
#         cap = cv2.VideoCapture(os.path.join(video_dir, selected_video))
#         fps = int(cap.get(cv2.CAP_PROP_FPS))
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         output_path = os.path.join(output_dir, f'output_{os.path.splitext(selected_video)[0]}.mp4')
#         out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#         stframe = st.empty()
#         progress = st.progress(0)
#         summary = defaultdict(int)

#         frame_buffer = []
#         incident_count = 0
#         current_frame_idx = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             current_frame_idx += 1
#             raw_frame = frame.copy()
#             frame_buffer.append(raw_frame)
#             if len(frame_buffer) > fps * 5:
#                 frame_buffer.pop(0)

#             results = model(frame)[0]
#             violation_detected = False
#             detected_frame = None

#             for box in results.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 conf = box.conf[0].item()
#                 cls = int(box.cls[0].item())
#                 label = labels[cls]

#                 if conf < confidence_threshold or label not in label_filter:
#                     continue

#                 summary[label] += 1
#                 color = colors.get(label, (255, 255, 255))
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                 cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#                 if label == "no_helmet" and not violation_detected:
#                     violation_detected = True
#                     detected_frame = frame.copy()

#             out_writer.write(frame)
#             stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

#             if violation_detected and detected_frame is not None:
#                 incident_count += 1
#                 timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

#                 # Save frame
#                 frame_path = os.path.join(frames_dir, f"no_helmet_frame_{incident_count}_{timestamp}.jpg")
#                 cv2.imwrite(frame_path, detected_frame)

#                 # Save video
#                 clip_path = os.path.join(clips_dir, f"no_helmet_incident_{incident_count}_{timestamp}.mp4")
#                 incident_writer = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))

#                 for bf in frame_buffer:
#                     incident_writer.write(bf)

#                 for _ in range(fps):
#                     incident_writer.write(raw_frame)

#                 for _ in range(fps * 4):
#                     ret_post, post_frame = cap.read()
#                     if not ret_post:
#                         break
#                     incident_writer.write(post_frame)

#                 incident_writer.release()

#             progress.progress(current_frame_idx / total_frames)
#             time.sleep(1 / fps)

#         cap.release()
#         out_writer.release()

#         st.success(f"✅ Inference complete! Output saved to `{output_path}`")

#         st.subheader("📊 Violation Summary")
#         st.table([{"Label": k, "Count": v} for k, v in summary.items()])

# # Incident Viewer
# elif selected_tab == "Incidents":
#     st.title("🚨 Incident Viewer")

#     folders = sorted([f for f in os.listdir(base_incident_dir) if os.path.isdir(os.path.join(base_incident_dir, f))])
#     selected_folder = st.selectbox("📁 Select Incident Folder", folders)

#     selected_folder_path = os.path.join(base_incident_dir, selected_folder)
#     selected_frames_dir = os.path.join(selected_folder_path, "frames")
#     selected_clips_dir = os.path.join(selected_folder_path, "clips")

#     image_files = sorted(os.listdir(selected_frames_dir), reverse=True)
#     video_files = sorted(os.listdir(selected_clips_dir), reverse=True)

#     incidents_per_page = 5
#     total_incidents = len(video_files)
#     total_pages = (total_incidents - 1) // incidents_per_page + 1
#     page = st.number_input("📄 Page", 1, total_pages, 1)

#     start = (page - 1) * incidents_per_page
#     end = start + incidents_per_page

#     current_images = image_files[start:end]
#     current_videos = video_files[start:end]

#     st.markdown("### 🖼️ Frames")
#     for img_file in current_images:
#         img_path = os.path.join(selected_frames_dir, img_file)
#         st.image(img_path, caption=img_file, use_container_width=True)

#     # st.markdown("### 🎞️ Clips")
#     # for vid_file in current_videos:
#     #     vid_path = os.path.join(selected_clips_dir, vid_file)
#     #     with open(vid_path, 'rb') as video_file:
#     #         video_bytes = video_file.read()
#     #         st.video(video_bytes)

#     st.markdown("---")
#     st.subheader("🚧 Coming Soon")
#     st.markdown("🅿️ **No Parking Violations** – Data not yet available.")
#     st.markdown("👨‍👩‍👦 **Triple Riding Violations** – Data not yet available.")
    
# # elif selected_tab == "Map":
# #     st.title("🗺️ Real-time Map View")

# #     import streamlit.components.v1 as components

# #     map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3888.9472910587865!2d77.63261757512184!3d12.911109287398782!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae15d1559e2651%3A0xb27e383e612faa20!2sLivNSense%20GreenOps%20Pvt%20Ltd!5e0!3m2!1sen!2sin!4v1744711532262!5m2!1sen!2sin"

# #     components.iframe(map_url, height=800, width=700)

# elif selected_tab == "Map":
#     st.title("🗺️ Real-time Map View")

#     import streamlit.components.v1 as components

#     st.markdown("""
#         ## 📍 Map View – Live Location
#         This map displays the **real-time monitoring area**.
#         Zoom, pan, or switch to satellite view to explore the area being analyzed.
#     """)

#     map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3888.9472910587865!2d77.63261757512184!3d12.911109287398782!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae15d1559e2651%3A0xb27e383e612faa20!2sLivNSense%20GreenOps%20Pvt%20Ltd!5e0!3m2!1sen!2sin!4v1744711532262!5m2!1sen!2sin"

#     components.html(f"""
#         <div style="border: 3px solid #4CAF50; border-radius: 15px; overflow: hidden; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
#             <iframe 
#                 src="{map_url}" 
#                 width="100%" 
#                 height="800" 
#                 style="border:0;" 
#                 allowfullscreen="" 
#                 loading="lazy">
#             </iframe>
#         </div>
#     """, height=820)





#-------------------------------------------------------------------------------------------------------------------------------


# live input



# import streamlit as st
# import cv2
# import os
# import time
# from ultralytics import YOLO
# import numpy as np
# from collections import defaultdict
# from datetime import datetime
# from PIL import Image

# # Paths
# model_path = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\models\\updated_4_best_yolov8.pt'
# video_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\input_videos\\input_videos_10-04-2025'
# output_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\output_videos\\output_videos_15-04-2025'
# base_incident_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\incidents_clips'
# incident_dir = os.path.join(base_incident_dir, 'incidents_clips_live')

# # New: Create subfolders
# frames_dir = os.path.join(incident_dir, "frames")
# clips_dir = os.path.join(incident_dir, "clips")
# os.makedirs(frames_dir, exist_ok=True)
# os.makedirs(clips_dir, exist_ok=True)
# os.makedirs(output_dir, exist_ok=True)
# os.makedirs(incident_dir, exist_ok=True)

# # Labels & Colors
# labels = ['person', 'car', 'bike', 'auto', 'bus', 'livestock', 'helmet', 'no_helmet', 'truck', 'number_plate']
# colors = {
#     'person': (0, 255, 0), 'car': (255, 0, 0), 'bike': (0, 0, 255), 'auto': (255, 255, 0),
#     'bus': (255, 165, 0), 'livestock': (128, 0, 128), 'helmet': (0, 255, 255),
#     'no_helmet': (0, 100, 255), 'truck': (139, 69, 19), 'number_plate': (255, 20, 147)
# }

# # Load YOLO model
# model = YOLO(model_path)

# # Streamlit Sidebar Navigation
# st.sidebar.title("🧭 Navigation")
# selected_tab = st.sidebar.radio("Go to", ["Live Inference", "Incidents", "Map"])

# # Live Inference
# if selected_tab == "Live Inference":
#     st.title("🚦Traffic Inference Dashboard")
#     input_mode = st.radio("📡 Input Mode", ["Upload Video", "Live Cam"])
#     confidence_threshold = st.slider("📏 Confidence Threshold", 0.0, 1.0, 0.3, step=0.05)
#     label_filter = st.multiselect("🏷️ Filter by Label", labels, default=labels)

#     if input_mode == "Upload Video":
#         video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.MOV'))]
#         selected_video = st.selectbox("🎥 Select Input Video", video_files)
#         start_inference = st.button("▶️ Start Inference")

#         if start_inference:
#             cap = cv2.VideoCapture(os.path.join(video_dir, selected_video))
#     else:
#         start_cam = st.button("🎥 Start Camera")
#         stop_cam = st.button("🛑 Stop Camera")
#         cap = None
#         # if start_cam:
#         #     cap = cv2.VideoCapture(0)
#         ip_webcam_url = st.text_input("📱 Enter IP Webcam URL", "http://192.168.2.93:8080/video")

#         if start_cam:
#             cap = cv2.VideoCapture(ip_webcam_url)

#     if (input_mode == "Upload Video" and start_inference) or (input_mode == "Live Cam" and cap is not None):
#         fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')

#         output_path = os.path.join(output_dir, f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4')
#         out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#         stframe = st.empty()
#         summary = defaultdict(int)

#         frame_buffer = []
#         incident_count = 0
#         current_frame_idx = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             current_frame_idx += 1
#             raw_frame = frame.copy()
#             frame_buffer.append(raw_frame)
#             if len(frame_buffer) > fps * 5:
#                 frame_buffer.pop(0)

#             results = model(frame)[0]
#             violation_detected = False
#             detected_frame = None

#             for box in results.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 conf = box.conf[0].item()
#                 cls = int(box.cls[0].item())
#                 label = labels[cls]

#                 if conf < confidence_threshold or label not in label_filter:
#                     continue

#                 summary[label] += 1
#                 color = colors.get(label, (255, 255, 255))
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                 cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#                 if label == "no_helmet" and not violation_detected:
#                     violation_detected = True
#                     detected_frame = frame.copy()

#             out_writer.write(frame)
#             stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

#             if violation_detected and detected_frame is not None:
#                 incident_count += 1
#                 timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

#                 frame_path = os.path.join(frames_dir, f"no_helmet_frame_{incident_count}_{timestamp}.jpg")
#                 cv2.imwrite(frame_path, detected_frame)

#                 clip_path = os.path.join(clips_dir, f"no_helmet_incident_{incident_count}_{timestamp}.mp4")
#                 incident_writer = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))

#                 for bf in frame_buffer:
#                     incident_writer.write(bf)
#                 for _ in range(fps):
#                     incident_writer.write(raw_frame)
#                 incident_writer.release()

#             time.sleep(1 / fps)
#             if input_mode == "Live Cam" and stop_cam:
#                 break

#         cap.release()
#         out_writer.release()

#         st.success(f"✅ Inference complete! Output saved to `{output_path}`")
#         st.subheader("📊 Violation Summary")
#         st.table([{"Label": k, "Count": v} for k, v in summary.items()])

# # Incident Viewer
# elif selected_tab == "Incidents":
#     st.title("🚨 Incident Viewer")

#     folders = sorted([f for f in os.listdir(base_incident_dir) if os.path.isdir(os.path.join(base_incident_dir, f))])
#     selected_folder = st.selectbox("📁 Select Incident Folder", folders)

#     selected_folder_path = os.path.join(base_incident_dir, selected_folder)
#     selected_frames_dir = os.path.join(selected_folder_path, "frames")
#     selected_clips_dir = os.path.join(selected_folder_path, "clips")

#     image_files = sorted(os.listdir(selected_frames_dir), reverse=True)
#     video_files = sorted(os.listdir(selected_clips_dir), reverse=True)

#     incidents_per_page = 5
#     total_incidents = len(video_files)
#     total_pages = (total_incidents - 1) // incidents_per_page + 1
#     page = st.number_input("📄 Page", 1, total_pages, 1)

#     start = (page - 1) * incidents_per_page
#     end = start + incidents_per_page

#     current_images = image_files[start:end]
#     current_videos = video_files[start:end]

#     st.markdown("### 🖼️ Frames")
#     for img_file in current_images:
#         img_path = os.path.join(selected_frames_dir, img_file)
#         st.image(img_path, caption=img_file, use_container_width=True)

#     # st.markdown("### 🎞️ Clips")
#     # for vid_file in current_videos:
#     #     vid_path = os.path.join(selected_clips_dir, vid_file)
#     #     with open(vid_path, 'rb') as video_file:
#     #         video_bytes = video_file.read()
#     #         st.video(video_bytes)

#     st.markdown("---")
#     st.subheader("🚧 Coming Soon")
#     st.markdown("🅿️ **No Parking Violations** – Data not yet available.")
#     st.markdown("👨‍👩‍👦 **Triple Riding Violations** – Data not yet available.")

# # Map Tab
# elif selected_tab == "Map":
#     st.title("🗺️ Real-time Map View")

#     import streamlit.components.v1 as components

#     st.markdown("""
#         ## 📍 Map View – Live Location
#         This map displays the **real-time monitoring area**.
#         Zoom, pan, or switch to satellite view to explore the area being analyzed.
#     """)

#     map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3888.9472910587865!2d77.63261757512184!3d12.911109287398782!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae15d1559e2651%3A0xb27e383e612faa20!2sLivNSense%20GreenOps%20Pvt%20Ltd!5e0!3m2!1sen!2sin!4v1744711532262!5m2!1sen!2sin"

#     components.html(f"""
#         <div style="border: 3px solid #4CAF50; border-radius: 15px; overflow: hidden; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
#             <iframe 
#                 src="{map_url}" 
#                 width="100%" 
#                 height="800" 
#                 style="border:0;" 
#                 allowfullscreen="" 
#                 loading="lazy">
#             </iframe>
#         </div>
#     """, height=820)


#----------------------------------------------------------------------------------------------------------------------------






# telegram alert with video

# TELEGRAM_BOT_TOKEN = "7802076982:AAGYvTpB0Rzt4bSxM_I3DQXBG1ijEbHBkXY"  # Replace with your Telegram Bot Token
# TELEGRAM_CHAT_ID = "7424789030"      # Replace with your Telegram Chat ID



# import streamlit as st
# import cv2
# import os
# import time
# import requests
# from ultralytics import YOLO
# import numpy as np
# from collections import defaultdict
# from datetime import datetime
# from PIL import Image

# # Telegram Bot Config
# TELEGRAM_BOT_TOKEN = "7802076982:AAGYvTpB0Rzt4bSxM_I3DQXBG1ijEbHBkXY"  # Replace with your Telegram Bot Token
# TELEGRAM_CHAT_ID = "7424789030"      # Replace with your Telegram Chat ID

# def send_telegram_alert(bot_token, chat_id, message, video_path=None):
#     url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
#     payload = {"chat_id": chat_id, "text": message}
#     requests.post(url, data=payload)

#     if video_path:
#         send_video_url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
#         with open(video_path, 'rb') as video_file:
#             files = {"video": video_file}
#             data = {"chat_id": chat_id}
#             requests.post(send_video_url, data=data, files=files)

# # Paths
# model_path = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\models\\updated_4_best_yolov8.pt'
# video_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\input_videos\\input_videos_10-04-2025'
# output_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\output_videos\\output_videos_15-04-2025'
# base_incident_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\incidents_clips'
# incident_dir = os.path.join(base_incident_dir, 'incidents_clips_live_alert')

# # Create subfolders
# frames_dir = os.path.join(incident_dir, "frames")
# clips_dir = os.path.join(incident_dir, "clips")
# os.makedirs(frames_dir, exist_ok=True)
# os.makedirs(clips_dir, exist_ok=True)
# os.makedirs(output_dir, exist_ok=True)
# os.makedirs(incident_dir, exist_ok=True)

# # Labels & Colors
# labels = ['person', 'car', 'bike', 'auto', 'bus', 'livestock', 'helmet', 'no_helmet', 'truck', 'number_plate']
# colors = {
#     'person': (0, 255, 0), 'car': (255, 0, 0), 'bike': (0, 0, 255), 'auto': (255, 255, 0),
#     'bus': (255, 165, 0), 'livestock': (128, 0, 128), 'helmet': (0, 255, 255),
#     'no_helmet': (0, 100, 255), 'truck': (139, 69, 19), 'number_plate': (255, 20, 147)
# }

# # Load YOLO model
# model = YOLO(model_path)

# # Streamlit Sidebar Navigation
# st.sidebar.title("🧭 Navigation")
# selected_tab = st.sidebar.radio("Go to", ["Live Inference", "Incidents", "Map"])

# # Live Inference
# if selected_tab == "Live Inference":
#     st.title("🚦Traffic Inference Dashboard")
#     input_mode = st.radio("📡 Input Mode", ["Upload Video", "Live Cam"])
#     confidence_threshold = st.slider("📏 Confidence Threshold", 0.0, 1.0, 0.3, step=0.05)
#     label_filter = st.multiselect("🏷️ Filter by Label", labels, default=labels)

#     if input_mode == "Upload Video":
#         video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.MOV'))]
#         selected_video = st.selectbox("🎥 Select Input Video", video_files)
#         start_inference = st.button("▶️ Start Inference")

#         if start_inference:
#             cap = cv2.VideoCapture(os.path.join(video_dir, selected_video))
#     else:
#         start_cam = st.button("🎥 Start Camera")
#         stop_cam = st.button("🛑 Stop Camera")
#         cap = None
#         ip_webcam_url = st.text_input("📱 Enter IP Webcam URL", "http://192.168.2.93:8080/video")

#         if start_cam:
#             cap = cv2.VideoCapture(ip_webcam_url)

#     if (input_mode == "Upload Video" and start_inference) or (input_mode == "Live Cam" and cap is not None):
#         fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')

#         output_path = os.path.join(output_dir, f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4')
#         out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#         stframe = st.empty()
#         summary = defaultdict(int)

#         frame_buffer = []
#         incident_count = 0
#         current_frame_idx = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             current_frame_idx += 1
#             raw_frame = frame.copy()
#             frame_buffer.append(raw_frame)
#             if len(frame_buffer) > fps * 5:
#                 frame_buffer.pop(0)

#             results = model(frame)[0]
#             violation_detected = False
#             detected_frame = None

#             for box in results.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 conf = box.conf[0].item()
#                 cls = int(box.cls[0].item())
#                 label = labels[cls]

#                 if conf < confidence_threshold or label not in label_filter:
#                     continue

#                 summary[label] += 1
#                 color = colors.get(label, (255, 255, 255))
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                 cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#                 if label == "no_helmet" and not violation_detected:
#                     violation_detected = True
#                     detected_frame = frame.copy()

#             out_writer.write(frame)
#             stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

#             if violation_detected and detected_frame is not None:
#                 incident_count += 1
#                 timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

#                 frame_path = os.path.join(frames_dir, f"no_helmet_frame_{incident_count}_{timestamp}.jpg")
#                 cv2.imwrite(frame_path, detected_frame)

#                 clip_path = os.path.join(clips_dir, f"no_helmet_incident_{incident_count}_{timestamp}.mp4")
#                 incident_writer = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))

#                 for bf in frame_buffer:
#                     incident_writer.write(bf)
#                 for _ in range(fps):
#                     incident_writer.write(raw_frame)
#                 incident_writer.release()

#                 # Send Telegram alert
#                 alert_msg = f"🚨 No Helmet Violation Detected!\nIncident #{incident_count}\nTime: {timestamp}"
#                 send_telegram_alert(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, alert_msg, clip_path)

#             time.sleep(1 / fps)
#             if input_mode == "Live Cam" and stop_cam:
#                 break

#         cap.release()
#         out_writer.release()

#         st.success(f"✅ Inference complete! Output saved to `{output_path}`")
#         st.subheader("📊 Violation Summary")
#         st.table([{"Label": k, "Count": v} for k, v in summary.items()])

# # Incident Viewer
# elif selected_tab == "Incidents":
#     st.title("🚨 Incident Viewer")

#     folders = sorted([f for f in os.listdir(base_incident_dir) if os.path.isdir(os.path.join(base_incident_dir, f))])
#     selected_folder = st.selectbox("📁 Select Incident Folder", folders)

#     selected_folder_path = os.path.join(base_incident_dir, selected_folder)
#     selected_frames_dir = os.path.join(selected_folder_path, "frames")
#     selected_clips_dir = os.path.join(selected_folder_path, "clips")

#     image_files = sorted(os.listdir(selected_frames_dir), reverse=True)
#     video_files = sorted(os.listdir(selected_clips_dir), reverse=True)

#     incidents_per_page = 5
#     total_incidents = len(video_files)
#     total_pages = (total_incidents - 1) // incidents_per_page + 1
#     page = st.number_input("📄 Page", 1, total_pages, 1)

#     start = (page - 1) * incidents_per_page
#     end = start + incidents_per_page

#     current_images = image_files[start:end]
#     current_videos = video_files[start:end]

#     st.markdown("### 🖼️ Frames")
#     for img_file in current_images:
#         img_path = os.path.join(selected_frames_dir, img_file)
#         st.image(img_path, caption=img_file, use_container_width=True)

#     st.markdown("---")
#     st.subheader("🚧 Coming Soon")
#     st.markdown("🅿️ **No Parking Violations** – Data not yet available.")
#     st.markdown("👨‍👩‍👦 **Triple Riding Violations** – Data not yet available.")

# # Map Tab
# elif selected_tab == "Map":
#     st.title("🗺️ Real-time Map View")

#     import streamlit.components.v1 as components

#     st.markdown("""
#         ## 📍 Map View – Live Location
#         This map displays the **real-time monitoring area**.
#         Zoom, pan, or switch to satellite view to explore the area being analyzed.
#     """)

#     map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3888.9472910587865!2d77.63261757512184!3d12.911109287398782!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae15d1559e2651%3A0xb27e383e612faa20!2sLivNSense%20GreenOps%20Pvt%20Ltd!5e0!3m2!1sen!2sin!4v1744711532262!5m2!1sen!2sin"

#     components.html(f"""
#         <div style="border: 3px solid #4CAF50; border-radius: 15px; overflow: hidden; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
#             <iframe 
#                 src="{map_url}" 
#                 width="100%" 
#                 height="800" 
#                 style="border:0;" 
#                 allowfullscreen="" 
#                 loading="lazy">
#             </iframe>
#         </div>
#     """, height=820)









# telegram alert with image




# import streamlit as st
# import cv2
# import os
# import time
# from ultralytics import YOLO
# import numpy as np
# from collections import defaultdict
# from datetime import datetime
# from PIL import Image
# import requests

# # Telegram Configuration
# TELEGRAM_BOT_TOKEN = "7802076982:AAGYvTpB0Rzt4bSxM_I3DQXBG1ijEbHBkXY"
# TELEGRAM_CHAT_ID = "7424789030"

# def send_telegram_alert(image_path, caption="🚨 No Helmet Violation Detected!"):
#     try:
#         with open(image_path, 'rb') as img:
#             files = {'photo': img}
#             url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
#             data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
#             response = requests.post(url, files=files, data=data)
#             if response.status_code != 200:
#                 st.warning("⚠️ Telegram alert failed to send.")
#     except Exception as e:
#         st.error(f"Telegram Alert Error: {e}")

# # Paths
# model_path = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\models\\updated_4_best_yolov8.pt'
# video_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\input_videos\\input_videos_10-04-2025'
# output_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\output_videos\\output_videos_15-04-2025'
# base_incident_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\incidents_clips'
# incident_dir = os.path.join(base_incident_dir, 'incidents_clips_live_alert')

# # New: Create subfolders
# frames_dir = os.path.join(incident_dir, "frames")
# clips_dir = os.path.join(incident_dir, "clips")
# os.makedirs(frames_dir, exist_ok=True)
# os.makedirs(clips_dir, exist_ok=True)
# os.makedirs(output_dir, exist_ok=True)
# os.makedirs(incident_dir, exist_ok=True)

# # Labels & Colors
# labels = ['person', 'car', 'bike', 'auto', 'bus', 'livestock', 'helmet', 'no_helmet', 'truck', 'number_plate']
# colors = {
#     'person': (0, 255, 0), 'car': (255, 0, 0), 'bike': (0, 0, 255), 'auto': (255, 255, 0),
#     'bus': (255, 165, 0), 'livestock': (128, 0, 128), 'helmet': (0, 255, 255),
#     'no_helmet': (0, 100, 255), 'truck': (139, 69, 19), 'number_plate': (255, 20, 147)
# }

# # Load YOLO model
# model = YOLO(model_path)

# # Streamlit Sidebar Navigation
# st.sidebar.title("🧭 Navigation")
# selected_tab = st.sidebar.radio("Go to", ["Live Inference", "Incidents", "Map"])

# # Live Inference
# if selected_tab == "Live Inference":
#     st.title("🚦Traffic Inference Dashboard")
#     input_mode = st.radio("📡 Input Mode", ["Upload Video", "Live Cam"])
#     confidence_threshold = st.slider("📏 Confidence Threshold", 0.0, 1.0, 0.3, step=0.05)
#     label_filter = st.multiselect("🏷️ Filter by Label", labels, default=labels)

#     if input_mode == "Upload Video":
#         video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.MOV'))]
#         selected_video = st.selectbox("🎥 Select Input Video", video_files)
#         start_inference = st.button("▶️ Start Inference")

#         if start_inference:
#             cap = cv2.VideoCapture(os.path.join(video_dir, selected_video))
#     else:
#         start_cam = st.button("🎥 Start Camera")
#         stop_cam = st.button("🛑 Stop Camera")
#         cap = None
#         ip_webcam_url = st.text_input("📱 Enter IP Webcam URL", "http://192.168.2.93:8080/video")

#         if start_cam:
#             cap = cv2.VideoCapture(ip_webcam_url)

#     if (input_mode == "Upload Video" and start_inference) or (input_mode == "Live Cam" and cap is not None):
#         fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')

#         output_path = os.path.join(output_dir, f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4')
#         out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#         stframe = st.empty()
#         summary = defaultdict(int)

#         frame_buffer = []
#         incident_count = 0
#         current_frame_idx = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             current_frame_idx += 1
#             raw_frame = frame.copy()
#             frame_buffer.append(raw_frame)
#             if len(frame_buffer) > fps * 5:
#                 frame_buffer.pop(0)

#             results = model(frame)[0]
#             violation_detected = False
#             detected_frame = None

#             for box in results.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 conf = box.conf[0].item()
#                 cls = int(box.cls[0].item())
#                 label = labels[cls]

#                 if conf < confidence_threshold or label not in label_filter:
#                     continue

#                 summary[label] += 1
#                 color = colors.get(label, (255, 255, 255))
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                 cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#                 if label == "no_helmet" and not violation_detected:
#                     violation_detected = True
#                     detected_frame = frame.copy()

#             out_writer.write(frame)
#             stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

#             if violation_detected and detected_frame is not None:
#                 incident_count += 1
#                 timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

#                 frame_path = os.path.join(frames_dir, f"no_helmet_frame_{incident_count}_{timestamp}.jpg")
#                 cv2.imwrite(frame_path, detected_frame)

#                 # Send to Telegram
#                 send_telegram_alert(frame_path)

#                 clip_path = os.path.join(clips_dir, f"no_helmet_incident_{incident_count}_{timestamp}.mp4")
#                 incident_writer = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))

#                 for bf in frame_buffer:
#                     incident_writer.write(bf)
#                 for _ in range(fps):
#                     incident_writer.write(raw_frame)
#                 incident_writer.release()

#             time.sleep(1 / fps)
#             if input_mode == "Live Cam" and stop_cam:
#                 break

#         cap.release()
#         out_writer.release()

#         st.success(f"✅ Inference complete! Output saved to `{output_path}`")
#         st.subheader("📊 Violation Summary")
#         st.table([{"Label": k, "Count": v} for k, v in summary.items()])

# # Incident Viewer
# elif selected_tab == "Incidents":
#     st.title("🚨 Incident Viewer")

#     folders = sorted([f for f in os.listdir(base_incident_dir) if os.path.isdir(os.path.join(base_incident_dir, f))])
#     selected_folder = st.selectbox("📁 Select Incident Folder", folders)

#     selected_folder_path = os.path.join(base_incident_dir, selected_folder)
#     selected_frames_dir = os.path.join(selected_folder_path, "frames")
#     selected_clips_dir = os.path.join(selected_folder_path, "clips")

#     image_files = sorted(os.listdir(selected_frames_dir), reverse=True)
#     video_files = sorted(os.listdir(selected_clips_dir), reverse=True)

#     incidents_per_page = 5
#     total_incidents = len(video_files)
#     total_pages = (total_incidents - 1) // incidents_per_page + 1
#     page = st.number_input("📄 Page", 1, total_pages, 1)

#     start = (page - 1) * incidents_per_page
#     end = start + incidents_per_page

#     current_images = image_files[start:end]
#     current_videos = video_files[start:end]

#     st.markdown("### 🖼️ Frames")
#     for img_file in current_images:
#         img_path = os.path.join(selected_frames_dir, img_file)
#         st.image(img_path, caption=img_file, use_container_width=True)

#     st.markdown("---")
#     st.subheader("🚧 Coming Soon")
#     st.markdown("🅿️ **No Parking Violations** – Data not yet available.")
#     st.markdown("👨‍👩‍👦 **Triple Riding Violations** – Data not yet available.")

# # Map Tab
# elif selected_tab == "Map":
#     st.title("🗺️ Real-time Map View")

#     import streamlit.components.v1 as components

#     st.markdown("""
#         ## 📍 Map View – Live Location
#         This map displays the **real-time monitoring area**.
#         Zoom, pan, or switch to satellite view to explore the area being analyzed.
#     """)

#     map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3888.9472910587865!2d77.63261757512184!3d12.911109287398782!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae15d1559e2651%3A0xb27e383e612faa20!2sLivNSense%20GreenOps%20Pvt%20Ltd!5e0!3m2!1sen!2sin!4v1744711532262!5m2!1sen!2sin"

#     components.html(f"""
#         <div style="border: 3px solid #4CAF50; border-radius: 15px; overflow: hidden; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
#             <iframe 
#                 src="{map_url}" 
#                 width="100%" 
#                 height="800" 
#                 style="border:0;" 
#                 allowfullscreen="" 
#                 loading="lazy">
#             </iframe>
#         </div>
#     """, height=820)



import streamlit as st
import cv2
import os
import time
import requests
from ultralytics import YOLO
import numpy as np
from collections import defaultdict
from datetime import datetime
from PIL import Image


# ==== TELEGRAM CONFIG ====
BOT_TOKEN = 'YOUR TOKEN'
CHAT_ID = 'YOUR CHAT ID'

def send_telegram_alert(image_path, message="🚨 No Helmet Violation Detected!"):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
    with open(image_path, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': CHAT_ID, 'caption': message}
        response = requests.post(url, files=files, data=data)
        return response.status_code == 200

# ==== PATHS ====
model_path = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\models\\updated_4_best_yolov8.pt'
video_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\input_videos\\input_videos_18-04-2025'
output_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\output_videos\\sam_output_videos_18-04-2025'
base_incident_dir = 'G:\\desktop\\MyProjects\\DL_projects\\BPRD_usecase\\inference\\incidents_clips'
incident_dir = os.path.join(base_incident_dir, 'incidents_clips_18-04-2025')

frames_dir = os.path.join(incident_dir, "frames")
clips_dir = os.path.join(incident_dir, "clips")
os.makedirs(frames_dir, exist_ok=True)
os.makedirs(clips_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(incident_dir, exist_ok=True)

# ==== LABELS ====
labels = ['person', 'car', 'bike', 'auto', 'bus', 'livestock', 'helmet', 'no_helmet', 'truck', 'number_plate']
colors = {
    'person': (0, 255, 0), 'car': (255, 0, 0), 'bike': (0, 0, 255), 'auto': (255, 255, 0),
    'bus': (255, 165, 0), 'livestock': (128, 0, 128), 'helmet': (0, 255, 255),
    'no_helmet': (0, 100, 255), 'truck': (139, 69, 19), 'number_plate': (255, 20, 147)
}

# ==== LOAD MODEL ====
model = YOLO(model_path)

# ==== STREAMLIT SIDEBAR ====
st.sidebar.title("🧭 Navigation")
selected_tab = st.sidebar.radio("Go to", ["Live Inference", "Incidents", "Map"])

# ==== LIVE INFERENCE ====
if selected_tab == "Live Inference":
    st.title("🚦Traffic Inference Dashboard")
    input_mode = st.radio("📡 Input Mode", ["Upload Video", "Live Cam"])
    confidence_threshold = st.slider("📏 Confidence Threshold", 0.0, 1.0, 0.3, step=0.05)
    label_filter = st.multiselect("🏷️ Filter by Label", labels, default=labels)

    if input_mode == "Upload Video":
        video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.MOV'))]
        selected_video = st.selectbox("🎥 Select Input Video", video_files)
        start_inference = st.button("▶️ Start Inference")

        if start_inference:
            cap = cv2.VideoCapture(os.path.join(video_dir, selected_video))
    else:
        start_cam = st.button("🎥 Start Camera")
        stop_cam = st.button("🛑 Stop Camera")
        cap = None
        ip_webcam_url = st.text_input("📱 Enter IP Webcam URL", "http://192.168.2.93:8080/video")

        if start_cam:
            cap = cv2.VideoCapture(ip_webcam_url)

    if (input_mode == "Upload Video" and start_inference) or (input_mode == "Live Cam" and cap is not None):
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        output_path = os.path.join(output_dir, f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4')
        out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        stframe = st.empty()
        summary = defaultdict(int)

        frame_buffer = []
        incident_count = 0
        current_frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            current_frame_idx += 1
            raw_frame = frame.copy()

            # Keep last 5 seconds of frames
            frame_buffer.append(raw_frame)
            if len(frame_buffer) > fps * 5:
                frame_buffer.pop(0)

            results = model(frame)[0]
            violation_detected = False
            detected_frame = None

            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                label = labels[cls]

                if conf < confidence_threshold or label not in label_filter:
                    continue

                summary[label] += 1
                color = colors.get(label, (255, 255, 255))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                if label == "no_helmet" and not violation_detected:
                    violation_detected = True
                    detected_frame = frame.copy()

            out_writer.write(frame)
            stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

            if violation_detected and detected_frame is not None:
                incident_count += 1
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                # Save frame
                frame_path = os.path.join(frames_dir, f"no_helmet_frame_{incident_count}_{timestamp}.jpg")
                cv2.imwrite(frame_path, detected_frame)

                # Send to Telegram
                send_telegram_alert(frame_path)

                # Save 10-sec clip
                clip_path = os.path.join(clips_dir, f"no_helmet_incident_{incident_count}_{timestamp}.mp4")
                incident_writer = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))
                for bf in frame_buffer:  # 5 seconds before
                    incident_writer.write(bf)
                for _ in range(fps * 5):  # 5 seconds after
                    incident_writer.write(raw_frame)
                incident_writer.release()

            time.sleep(1 / fps)
            if input_mode == "Live Cam" and stop_cam:
                break

        cap.release()
        out_writer.release()

        st.success(f"✅ Inference complete! Output saved to `{output_path}`")
        st.subheader("📊 Violation Summary")
        st.table([{"Label": k, "Count": v} for k, v in summary.items()])

# ==== INCIDENT VIEWER ====
elif selected_tab == "Incidents":
    st.title("🚨 Incident Viewer")

    folders = sorted([f for f in os.listdir(base_incident_dir) if os.path.isdir(os.path.join(base_incident_dir, f))])
    selected_folder = st.selectbox("📁 Select Incident Folder", folders)

    selected_folder_path = os.path.join(base_incident_dir, selected_folder)
    selected_frames_dir = os.path.join(selected_folder_path, "frames")
    selected_clips_dir = os.path.join(selected_folder_path, "clips")

    image_files = sorted(os.listdir(selected_frames_dir), reverse=True)
    video_files = sorted(os.listdir(selected_clips_dir), reverse=True)

    incidents_per_page = 5
    total_incidents = len(video_files)
    total_pages = (total_incidents - 1) // incidents_per_page + 1
    page = st.number_input("📄 Page", 1, total_pages, 1)

    start = (page - 1) * incidents_per_page
    end = start + incidents_per_page

    current_images = image_files[start:end]
    current_videos = video_files[start:end]

    st.markdown("### 🖼️ Frames")
    for img_file in current_images:
        img_path = os.path.join(selected_frames_dir, img_file)
        st.image(img_path, caption=img_file, use_container_width=True)

    # st.markdown("### 🎞️ Clips")
    # for vid_file in current_videos:
    #     vid_path = os.path.join(selected_clips_dir, vid_file)
    #     with open(vid_path, 'rb') as video_file:
    #         video_bytes = video_file.read()
    #         st.video(video_bytes)

    st.markdown("---")
    st.subheader("🚧 Coming Soon")
    st.markdown("🅿️ **No Parking Violations** – Data not yet available.")
    st.markdown("👨‍👩‍👦 **Triple Riding Violations** – Data not yet available.")

# ==== MAP TAB ====
elif selected_tab == "Map":
    st.title("🗺️ Real-time Map View")
    import streamlit.components.v1 as components
    map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3888.9472910587865!2d77.63261757512184!3d12.911109287398782!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae15d1559e2651%3A0xb27e383e612faa20!2sLivNSense%20GreenOps%20Pvt%20Ltd!5e0!3m2!1sen!2sin!4v1744711532262!5m2!1sen!2sin"

    components.html(f"""
        <div style="border: 3px solid #4CAF50; border-radius: 15px; overflow: hidden; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
            <iframe 
                src="{map_url}" 
                width="100%" 
                height="800" 
                style="border:0;" 
                allowfullscreen="" 
                loading="lazy">
            </iframe>
        </div>
    """, height=820)

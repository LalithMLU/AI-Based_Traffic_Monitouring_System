# AI-Based Real-Time Traffic Violation Detection System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🚀 Project Overview

This repository contains an end-to-end traffic monitoring pipeline that uses YOLOv8 for real-time object detection (helmet/no-helmet, triple riding, etc.), saves violation clips, and can deploy optimized OpenVINO models for edge devices. It also includes a Streamlit dashboard for live inference, incident review, and map visualization.

---


## 🎯 Features

- 🚘 Detects 'no helmet' violations in real-time using YOLOv8.
- 🎥 Processes live video feeds (webcam/IP camera).
- 📸 Captures and saves 10-second violation clips (5s before & after).
- 📤 Sends alert frames of violations to a Telegram bot.
- 🌐 Streamlit-based UI for live monitoring and violation logs.

## 🧠 Model Design

- **Annotation Tool:** [CVAT](https://cvat.org) used for annotating helmet and no-helmet instances.
- **Model Training:** YOLOv8n model trained on custom dataset with annotated frames.
- **Export to OpenVINO:** YOLOv8n model exported to ONNX and converted to OpenVINO IR format for faster inference.

## 🛠️ Technologies Used

- `Python 3.11`
- `Ultralytics YOLOv8`
- `OpenCV`
- `Tesseract OCR`
- `Streamlit`
- `Telegram Bot API`



## 📬 Contact
Developed by Manoj R Gowda at LivNSense as part of the Digital Twin for Traffic Monitoring project.

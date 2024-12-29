# Object-Detection-With-YoLo
Object detection using YOLO object detector

## Overview
This project implements an object detection system using YOLO (You Only Look Once) models. It provides a GUI to detect objects from live cameras or video files with customizable features such as camera selection, detection areas, detectable vehicle types, and YOLO models.

## Features
- Real-time Detection: Detect objects from live cameras or pre-recorded videos.
- Customizable Detection Area: Define specific areas for detection.
- Vehicle Type Filtering: Choose which vehicle types to detect.
- YOLO Model Customization: Use different YOLO model configurations.
- GPU Acceleration: Leverage GPU for faster inference.
- User-Friendly GUI: Easily control the system through an interactive interface.

## Requirements
To run this project, ensure you have the following:

- Hardware:
  - A CUDA-compatible GPU (optional).
  - Webcams configured (for live detection).

- Software Dependencies:
  - Python 3.9
  - OS - windows
  - Visual studio desktop development with c++
  - Cuda toolkit 
  - Install the required Python packages using the provided requirements.txt file:
    - `pip install -r requirements.txt`

## Installation
- Clone the repository
- Install dependencies 

## Usage 
- Run `main.py`
- Select either video from file picker or camera if available
  ![1](https://github.com/user-attachments/assets/ad941089-de92-4a27-a64e-ec5a2a4e8142)
  
- Close the camera selection winodw after selecting camera if you want live camera option
  ![2](https://github.com/user-attachments/assets/76ace3cf-d125-4f2d-a819-e09e1c75182b)
  
- Proceed to `Detect`
- Select the vehicles need to be detected (default: all), and yolo model (default: yolov8n)
  ![3](https://github.com/user-attachments/assets/283572e0-464b-4629-8870-2e5b2c3ad81f)
  
- Draw the area to be observed using `Draw Boundary` option
  ![4](https://github.com/user-attachments/assets/3b837605-8205-4923-b226-16a27abe3db1)
  ![5](https://github.com/user-attachments/assets/171fb9cc-0ac5-4da3-bf3a-9126bc7e6f6c)
  
- Close drawing window and mask after selecting the area
- Click `Start`

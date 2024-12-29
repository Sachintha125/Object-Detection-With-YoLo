from ultralytics import YOLO
import cv2
import cvzone
import numpy as np
from sort import Sort
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap


# mouse callback function
def boundary_drawing(event, x, y, flags, param):
    self = param  # The instance of the class
    if event == cv2.EVENT_LBUTTONDOWN:
        self.drawing = True
        self.pt1_x, self.pt1_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if self.drawing:
            cv2.line(self.img, (self.pt1_x, self.pt1_y), (x, y), color=(255, 255, 255), thickness=2)
            cv2.imshow('drawer', self.img)
            self.pt1_x, self.pt1_y = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        self.drawing = False
        cv2.line(self.img, (self.pt1_x, self.pt1_y), (x, y), color=(255, 255, 255), thickness=2)
        cv2.imshow('drawer', self.img)



def list_available_cameras():
    available_cameras = []
    for index in range(10):  # Test camera indices 0 to 9
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
    if len(available_cameras) == 0:
        return False
    else:
        return available_cameras


def loadCamera(param):
    self = param
    self.cam = int(self.comboBox.currentText().split(' ')[1])
    self.cap = cv2.VideoCapture(self.cam)
    if not self.cap.isOpened():
        self.player.setText('Failed loading Video.....')
    else:
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerOut)
        self.timer.start(30)  # 30 ms for ~33 FPS video playback
        self.camera_loaded_signal.emit(str(self.cam))


def drawingWindow(param):
    self = param
    cap = cv2.VideoCapture(self.selected_media_input_path)
    success, self.img = cap.read()
    if not success:
        print("Failed to capture image.")
        return
    cv2.namedWindow("drawer", cv2.WINDOW_NORMAL)
    cv2.imshow('drawer', self.img)

        # Pass `self` as the parameter to the callback
    cv2.setMouseCallback('drawer', boundary_drawing, self)

    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 255:  # Close button
            self.drawed_img = self.img.copy()
            cv2.destroyAllWindows()
            break


def show_mask(param):
    self = param
    # Convert the image to grayscale
    gray = cv2.cvtColor(self.drawed_img, cv2.COLOR_BGR2GRAY)
    # Threshold to create a binary image
    _, binary = cv2.threshold(gray, 254, 255, cv2.THRESH_BINARY)

    # Create a mask for floodFill
    # Mask size must be 2 pixels larger than the binary image
    h, w = binary.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Choose a seed point inside the boundary
    seed_point = (50, 50)  # Replace with a point inside the boundary

    # Perform flood fill
    cv2.floodFill(binary, mask, seed_point, 255)  # Fill with white (255)

    # Invert back the binary image if required
    filled = cv2.bitwise_not(binary)

    # Define kernel size for closing (adjust based on spot size)
    kernel = np.ones((5, 5), np.uint8)  # Larger kernel for bigger spots
    # Apply morphological closing to remove small black spots in white area
    filled = cv2.morphologyEx(filled, cv2.MORPH_CLOSE, kernel)

    self.mask = filled

    # Show the result
    cv2.imshow("Filled", filled)

    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 255:  # close button
            cv2.destroyAllWindows()
            break


def updateFrame(param):
    self = param
    ret, frame = self.cap.read()
    if ret:
            # Convert the frame to RGB
        self.exit_label.setText('Close this window if successful....')
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width

            # Convert to QImage
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Set the QPixmap on the QLabel
        self.player.setPixmap(QPixmap.fromImage(q_image))
    else:
            # Stop timer if the video ends
        self.timer.stop()
        self.cap.release()



def draw_straight_boundaries(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    approx_contours = []
    epsilon_factor = 0.01

    for contour in contours:
        epsilon = epsilon_factor * cv2.arcLength(contour, True)  # Approximation accuracy
        approx = cv2.approxPolyDP(contour, epsilon, True)  # Approximate contour
        approx_contours.append(approx)

    return approx_contours



def detect_objects(param):
    self = param
    self.yolo_model = YOLO(self.model_file)
    self.cap = cv2.VideoCapture(self.selected_media_input_path)
    self.tracker = Sort(max_age=20)
    self.entered, self.exited = 0, 0
    self.obj_state = {}
    self.tracked_vehicle_names = []
    self.class_names_dict = self.yolo_model.names

    if not self.cap.isOpened():
        self.player.setText('Failed loading Video.....')
    else:
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerOut)
        self.timer.start(30)  # 30 ms for ~33 FPS video playback


def updateDetectorFrame(param):
    self = param
    try:
        success, img = self.cap.read()
        if not success:
            self.player.setText('Error Occurred...')
        results = self.yolo_model(img, stream=True)

        detections = np.empty((0, 5))
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
                confidence = box.conf[0].item()
                cls = box.cls[0].item()

                if self.class_names_dict[cls] in self.vehi_list:
                    self.tracked_vehicle_names.append(self.class_names_dict[cls])
                    currentArr = np.array([x1, y1, x2, y2, confidence])
                    detections = np.vstack((detections, currentArr))

        resultsTracker = self.tracker.update(detections)

        for vehi_type, result in zip(self.tracked_vehicle_names, resultsTracker):
            x1, y1, x2, y2, id = result
            x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
            xc, yc = (x1 + x2) // 2, (y1 + y2) // 2
            pixel_color = self.mask[yc, xc]
            is_in_area = False if pixel_color == 0 else True
            if id not in self.obj_state.keys():
                self.obj_state[id] = 'in area' if is_in_area else 'out of area'
            else:
                prevState = self.obj_state[id]
                if prevState == 'out of area' and is_in_area:
                    self.entered += 1
                    self.obj_state[id] = 'in area'
                elif prevState == 'in area' and not is_in_area:
                    self.exited += 1
                    self.obj_state[id] = 'out of area'
                elif not is_in_area and id in self.obj_state:
                    del self.obj_state[id]

            if is_in_area:
                width, height = x2 - x1, y2 - y1
                cvzone.cornerRect(img, (x1, y1, width, height), l=9, rt=2, colorR=(0, 0, 255))
                cvzone.putTextRect(img=img, text=f'{vehi_type}', pos=(max(0, x1), max(35, y1)),
                                       scale=2, thickness=2, offset=3)

        cv2.putText(img, f'Entered {str(self.entered)}', (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)
        cv2.putText(img, f'Exited {str(self.exited)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)
        for approx in self.straight_boundaries:
            cv2.polylines(img, [approx], isClosed=True, color=(0, 0, 255), thickness=2)

            # Convert frame to QImage
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Update QLabel
        self.player.setPixmap(QPixmap.fromImage(q_image))

    except Exception as e:
        print(f"Error: {e}")
        exit()

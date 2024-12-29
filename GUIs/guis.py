from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog
from utils import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot


class Home(QMainWindow):

    def __init__(self):
        super(Home, self).__init__()
        self.setWindowIcon(QIcon("GUIs/yolo.png"))
        self.setWindowTitle("Home")
        self.camera_dialog = None
        self.detector = None
        self.selected_media_input_path = None
        loadUi('GUIs/home.ui', self)
        self.detectButton.clicked.connect(self.loadDetector)
        self.actionVideo.triggered.connect(self.loadFilePicker)
        self.actionCamera.triggered.connect(self.loadCameraSelect)
        if (not self.camera_dialog) and (not self.selected_media_input_path):
            self.select_method_label.setText('No media attached yet')


    def loadFilePicker(self):
        video, _ = QFileDialog.getOpenFileName(self, 'Select Video', '', 'mp4 files (*.mp4);; mkv files (*.mkv)')
        if video:
            video_name = video.split('/')[-1]
            self.selected_media_input_path = "\\".join(video.split('/'))
            self.select_method_label.setText(f'Media {video_name} attached')
            self.detectButton.setEnabled(True)


    def loadCameraSelect(self):
        self.select_method_label.setText(f'Cameras Detected')
        self.camera_dialog = CameraSelect()
        self.camera_dialog.camera_loaded_signal.connect(self.updateCameraIndex)
        self.camera_dialog.show()


    def loadDetector(self):
        if self.selected_media_input_path != None:
            self.detector = Detector()
            self.detector.selected_media_input_path = self.selected_media_input_path
            self.detector.show()


    @pyqtSlot(str)
    def updateCameraIndex(self, message):
        """Update the label text when a camera is loaded."""
        self.detectButton.setEnabled(True)
        self.selected_media_input_path = int(message)
        self.select_method_label.setText(f'Camera {message} selected')



class CameraSelect(QDialog):
    camera_loaded_signal = pyqtSignal(str)

    def __init__(self):
        super(CameraSelect, self).__init__()
        self.setWindowIcon(QIcon("GUIs/yolo.png"))
        self.setWindowTitle("Select Camera")
        loadUi('GUIs/camera.ui', self)
        cam_list = list_available_cameras()
        if not cam_list:
            self.player.setText('No cameras found')
        else:
            for i in cam_list:
                self.comboBox.addItem(f'Cam {i}')
        self.cam, self.cap, self.timer = None, None, None
        self.comboBox.currentIndexChanged.connect(self.callLoadCamera)


    def callLoadCamera(self):
        loadCamera(self)


    def timerOut(self):
        updateFrame(self)

    def closeEvent(self, event):
        """Override closeEvent to release the camera and clean up."""
        if self.timer:
            self.timer.stop()  # Stop the timer
        if self.cap and self.cap.isOpened():
            self.cap.release()  # Release the camera
        event.accept()


class Detector(QDialog):
    models = {'YoLo Nano': 'yolov8n.pt',
              'YoLo Medium': 'yolov8m.pt',
              'YoLo Large': 'yolov8l.pt'}

    def __init__(self):
        super(Detector, self).__init__()
        self.setWindowIcon(QIcon("GUIs/yolo.png"))
        self.setWindowTitle("Detector")
        loadUi('GUIs/detector.ui', self)
        self.player.setScaledContents(True)
        self.car.setChecked(True)
        self.truck.setChecked(True)
        self.train.setChecked(True)
        self.motorcycle.setChecked(True)
        self.bicycle.setChecked(True)
        self.bus.setChecked(True)
        self.startButton.setEnabled(False)
        self.vehi_list = ['bicycle', 'car', 'motorcycle', 'bus', 'train', 'truck']
        self.model_file = Detector.models[self.model_combo.currentText()]
        self.car.stateChanged.connect(self.changeVehiList)
        self.truck.stateChanged.connect(self.changeVehiList)
        self.train.stateChanged.connect(self.changeVehiList)
        self.motorcycle.stateChanged.connect(self.changeVehiList)
        self.bicycle.stateChanged.connect(self.changeVehiList)
        self.bus.stateChanged.connect(self.changeVehiList)
        self.model_combo.currentIndexChanged.connect(self.changeModel)
        self.drawButton.clicked.connect(self.loadDrawingWindow)
        self.startButton.clicked.connect(self.startButtonClicked)
        
        self.selected_media_input_path = None
        self.drawing = False
        self.pt1_x = None
        self.pt1_y = None
        self.img = None
        self.mask = None


    def changeVehiList(self):
        checkbox = self.sender()
        state = checkbox.isChecked()
        text = checkbox.text()
        if not state:
            self.vehi_list.remove(text.lower())
        else:
            self.vehi_list.append(text.lower())

    def changeModel(self):
        curr_model =  self.model_combo.currentText()
        self.model_file = Detector.models[curr_model]


    def loadDrawingWindow(self):
        drawingWindow(self)

        show_mask(self)
        self.straight_boundaries = draw_straight_boundaries(self.mask)
        self.startButton.setEnabled(True)

    def startButtonClicked(self):
        detect_objects(self)

    def timerOut(self):
        updateDetectorFrame(self)

    def closeEvent(self, event):
        """Override closeEvent to release the camera and clean up."""
        if self.timer:
            self.timer.stop()  # Stop the timer
        if self.cap and self.cap.isOpened():
            self.cap.release()  # Release the camera
        event.accept()




from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout,  QMessageBox,  QSlider
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6 import QtWidgets, uic
import numpy as np
import pandas as pd
import sys
import pyqtgraph as pg
import qdarkstyle
import os
from scipy import signal
import librosa
import matplotlib
import sounddevice as sd
from functools import partial
import bisect

from imageViewPort import ImageViewport

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()


    def init_ui(self):
        # Load the UI Page
        self.ui = uic.loadUi('Mainwindow.ui', self)
        self.setWindowTitle("FT Mixer")
        self.image_ports = []
        self.load_ui_elements()


    def create_image_viewport(self, parent, mouse_double_click_event_handler):
        image_port = ImageViewport()
        image_layout = QVBoxLayout(parent)
        image_layout.addWidget(image_port)
        image_port.mouseDoubleClickEvent = mouse_double_click_event_handler
        return image_port


    def load_ui_elements(self):
        ui_view_ports = [self.ui.original1, self.ui.original2, self.ui.original3, self.ui.original4]
        ui_combo_boxes = [self.ui.combo1, self.ui.combo2, self.ui.combo3, self.ui.combo4]
        # Create an empty list to store ImageViewport instances
        
        # Create ImageViewport instances using the function
        self.image_ports.extend([
            self.create_image_viewport(ui_view_ports[0], lambda event: self.browse_image(event, 0)),
            self.create_image_viewport(ui_view_ports[1], lambda event: self.browse_image(event, 1)),
            self.create_image_viewport(ui_view_ports[2], lambda event: self.browse_image(event, 2)),
            self.create_image_viewport(ui_view_ports[3], lambda event: self.browse_image(event, 3))
        ])
        
        for combo_box in ui_combo_boxes:
            combo_box.addItems(["Magnitude", "Phase", "Real", "Imaginary"])


    def browse_image(self, event, index):
        file_filter = "Raw Data (*.png *.jpg *.jpeg)"
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Signal File', './', filter=file_filter)
        
        if image_path:
            if 0 <= index < len(self.image_ports):
                # Set the image only for the ImageViewport at the specified index
                self.image_ports[index].set_image(image_path)




def main():
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
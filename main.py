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
        self.load_ui_elements()

    def load_ui_elements(self):
        ui_view_ports = [self.ui.original1, self.ui.original2, self.ui.original3, self.ui.original4]
        # Create an empty list to store ImageViewport instances
        image_ports = []
        for viewport in ui_view_ports:
            image_port = ImageViewport()
            image_layout = QVBoxLayout(viewport)
            image_layout.addWidget(image_port)

            # Append the ImageViewport instance to the list
            image_ports.append(image_port)


def main():
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
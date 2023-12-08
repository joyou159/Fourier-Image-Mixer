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
from mixer import ImageMixer


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        # Load the UI Page
        self.ui = uic.loadUi('Mainwindow.ui', self)
        self.setWindowTitle("FT Mixer")
        self.image_ports = []
        
        #mixer and its connection line
        self.mixer = ImageMixer(self)
        self.ui.mixxer.clicked.connect(self.mixer.mix_images)
        
        self.operations = {"0": '', "1": '', '2': '', '3': ''}
        self.load_ui_elements()

    def create_image_viewport(self, parent, mouse_double_click_event_handler):
        image_port = ImageViewport(self)
        image_layout = QVBoxLayout(parent)
        image_layout.addWidget(image_port)
        image_port.mouseDoubleClickEvent = mouse_double_click_event_handler
        return image_port

    def load_ui_elements(self):
        self.ui_view_ports = [
            self.ui.original1, self.ui.original2, self.ui.original3, self.ui.original4]
        self.ui_image_combo_boxes = [
            self.ui.combo1,self.ui.combo2, self.ui.combo3, self.ui.combo4]
        self.ui_mixing_combo_boxes = [
            self.ui.combo11, self.ui.combo12, self.ui.combo13, self.ui.combo14]
        self.ui_vertical_sliders = [
            self.ui.verticalSlider_1, self.ui.verticalSlider_2, self.ui.verticalSlider_3, self.ui.verticalSlider_4]
        # Create ImageViewport instances using the function
        for index, viewport in enumerate(self.ui_view_ports):
            image_port = self.create_image_viewport(viewport, lambda event, idx=index: self.browse_image(event, idx))
            self.image_ports.append(image_port)
        
        for combo_box in self.ui_mixing_combo_boxes:
            combo_box.addItems(['image1', 'image2', 'image3', 'image4'])


    def browse_image(self, event, index):
        file_filter = "Raw Data (*.png *.jpg *.jpeg)"
        self.image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Signal File', './', filter=file_filter)

        if self.image_path:
            if 0 <= index < len(self.image_ports):
                # Set the image only for the ImageViewport at the specified index
                image = self.image_ports[index]
                image.update_image_parameters(index)
                self.ui_image_combo_boxes[index].addItems(["FT Magnitude", "FT Phase", "FT Real", "FT Imaginary"])
                
    def get_operations(self):
        return self.operations

    def mix_and_display(self):
        images = [viewport.image for viewport in self.viewports]
        self.mixer.mix_images(images)


def main():
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

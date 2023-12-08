import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets

# Placeholder for FT-related functionalities
import numpy as np
from scipy.fft import fft2, ifft2, fftshift

class ImageMixer(QWidget):
    def __init__(self,main_window, parent=None):
        super().__init__(parent)
        self.mix_image = None
        self.main_window = main_window
    def check_op_validity(self):
        #mag / phase pair
        pair1 = 0
        #real / imag pair
        pair2 = 0
        operations = self.main_window.get_operations()
        for key, type in operations.items():
            if type == "phase" or type == "magnitude":
                pair1 += 1
            elif type == "real" or type == "imaginary":
                pair2 += 1
            else:
                raise ValueError("Invalid type")
        
        if pair1%2 != 0  or   pair2%2 != 0 :
            raise ValueError ("")
        # Display the mixed image
        self.set_image(mixed_image)
        
    def mix_images(self):
        self.check_op_validity()
        pass

    # def set_image(self, image_array):
    #     if image_array is not None:
    #         height, width = image_array.shape
    #         mix_image = QImage(image_array, width, height, width, QImage.Format.Format_Grayscale8)
    #         pixmap = QPixmap.fromImage(mix_image)
    #         self.mix_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio))

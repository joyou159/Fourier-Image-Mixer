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
        valid_pairs = [("FT Magnitude","FT Phase"),("FT Phase","FT Magnitude"),("FT Real", "FT Imaginary"),("FT Imaginary","FT Real")]
        op_sequence = []
        operations = self.main_window.get_operations()
        for combo in self.main_window.ui_mixing_combo_boxes:
            if len(self.main_window.image_ports)!=4:
                raise ValueError('please pick the rest of images')
            else:
                image_selection = combo.currentIndex()
                operation = operations[str(image_selection)]
                # image = self.main_window.image_ports[image_selection]
                op_sequence.append(operation)
        pair1 = (op_sequence[0],op_sequence[1])
        pair2 = (op_sequence[2],op_sequence[3])
        if pair1 not in valid_pairs or pair2 not in valid_pairs:
            raise ValueError('Please choose valid pairs')
        # for key, type in operations.items():
        #     if type == "phase" or type == "magnitude":
        #         pair1 += 1
        #     elif type == "real" or type == "imaginary":
        #         pair2 += 1
        #     else:
        #         raise ValueError("Invalid type")
        
        # if pair1%2 != 0  or   pair2%2 != 0 :
        #     raise ValueError ("")
        # # Display the mixed image
        # self.set_image(mixed_image)
        
    def mix_images(self):
        self.check_op_validity()
        pass

    # def set_image(self, image_array):
    #     if image_array is not None:
    #         height, width = image_array.shape
    #         mix_image = QImage(image_array, width, height, width, QImage.Format.Format_Grayscale8)
    #         pixmap = QPixmap.fromImage(mix_image)
    #         self.mix_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio))

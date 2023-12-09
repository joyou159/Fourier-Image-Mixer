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


class ImageMixer(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mix_image = None
        self.main_window = main_window

    def check_pair_validity(self):
        valid_pairs = [("FT Magnitude", "FT Phase"), ("FT Phase", "FT Magnitude"),
                       ("FT Real", "FT Imaginary"), ("FT Imaginary", "FT Real"), ("", "")]
        comp_seq = []
        components = self.main_window.components  # returns the
        print(len(self.main_window.image_ports))
        for combo in self.main_window.ui_mixing_combo_boxes:
            if len(self.main_window.image_ports) % 2 != 0:
                raise ValueError('please pick the rest of images')
            else:
                image_selection = combo.currentIndex()
                component = components[str(image_selection)]
                # image = self.main_window.image_ports[image_selection]
                comp_seq.append(component)
        pair1 = (comp_seq[0], comp_seq[1])
        pair2 = (comp_seq[2], comp_seq[3])
        print(pair1)
        print(pair2)
        if pair1 not in valid_pairs or pair2 not in valid_pairs:
            raise ValueError('Please choose valid pairs')

    def handle_mixing_sliders(self):
        pass

    def collect_chunks(self, ind, event):
        print("don't touch this")

    def mix_images(self):
        self.check_pair_validity()

        pass

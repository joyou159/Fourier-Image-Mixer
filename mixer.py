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
from PyQt6.QtGui import QPixmap, QImage,  QImageReader, QPainter
from PIL import Image, ImageQt, ImageEnhance
from PyQt6.QtGui import QPainter, QBrush, QPen
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets

# Placeholder for FT-related functionalities
import numpy as np
from scipy.fft import ifft2


class ImageMixer(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mix_image = None
        self.main_window = main_window
        self.fft2_output = []
        self.mixing_comp = []
        self.selection_mode = 1
        self.precedence = False
        self.chunks = {
            "0": [],
            "1": [],
            "2": [],
            "3": []
        }

    def check_pair_validity(self):
        valid_pairs = [("FT Magnitude", "FT Phase"), ("FT Phase", "FT Magnitude"),
                       ("FT Real", "FT Imaginary"), ("FT Imaginary", "FT Real"), ("", "")]
        components = self.main_window.components  # returns the
        print(components)
        self.mixing_comp = []
        for combo in self.main_window.ui_mixing_combo_boxes:
            if len(self.main_window.image_ports) % 2 != 0:
                raise ValueError('please pick the rest of images')
            else:
                image_selection = combo.currentIndex()
                if image_selection == 0:
                    component = ""
                else:
                    component = components[str(image_selection)]
                # image = self.main_window.image_ports[image_selection]
                self.mixing_comp.append(component)
        pair1 = (self.mixing_comp[0], self.mixing_comp[1])
        pair2 = (self.mixing_comp[2], self.mixing_comp[3])
        print(self.mixing_comp)
        if pair1 not in valid_pairs or pair2 not in valid_pairs:
            raise ValueError('Please choose valid pairs')

    def handle_mixing_sliders(self):
        pass

    def collect_chunks(self, ind):
        print("the current modified image", ind)
        curr_FTViewport_object = self.main_window.components_ports[ind]

        if self.selection_mode:
            selection_matrix = np.zeros_like(
                curr_FTViewport_object.component_data)
        else:
            selection_matrix = np.ones_like(
                curr_FTViewport_object.component_data)

            start_pos = curr_FTViewport_object.press_pos  # (x1,y1)
            end_pos = curr_FTViewport_object.release_pos  # (x2,y2)

            for i in range(start_pos[1], end_pos[1] + 1):
                for j in range(start_pos[0], end_pos[0] + 1):
                    if self.selection_mode:
                        selection_matrix[i, j] = 1
                    else:
                        selection_matrix[i, j] = 0

        curr_chunk = curr_FTViewport_object.component_data * selection_matrix
        self.chunks[str(ind)] = curr_chunk
        print(f"no of chunks {len(self.chunks)}")

    def mix_images(self):
        self.check_pair_validity()
        mixing_order = self.decode_pairs()
        pair_1_indices = (mixing_order[0], mixing_order[1])
        pair_1_comp = (self.mixing_comp[0], self.mixing_comp[1])
        pair_2_indices = (mixing_order[2], mixing_order[3])
        pair_2_comp = (self.mixing_comp[2], self.mixing_comp[3])
        print(pair_1_indices, pair_2_indices)
        self.fft2_output = []
        self.fft2_output.append(
            self.compose_complex(pair_1_indices, pair_1_comp))
        self.fft2_output.append(
            self.compose_complex(pair_2_indices, pair_2_comp))
        self.mixed_image = ifft2(self.compose_complex)
        self.set_image()

    def decode_pairs(self):
        mixing_order = []
        for combo in self.main_window.ui_mixing_combo_boxes:
            image_num = combo.currentIndex() - 1  # -1 means None
            mixing_order.append(image_num)
        return mixing_order

    def compose_complex(self, pair_indices, pair_comp):
        if -1 in pair_indices:
            return
        if "FT Magnitude" in pair_comp:
            mag_index = pair_indices[pair_comp.index("FT Magnitude")]
            phase_index = pair_indices[pair_comp.index("FT Phase")]
            print(
                f"the resulting complex number is of indices {mag_index, phase_index} in order")
            # complex_numbers = self.chunks[mag_index] * np.exp(
            #     1j * self.chunks[phase_index])
        else:
            real_index = pair_indices[pair_comp.index("FT Real")]
            imaginary_index = pair_indices[pair_comp.index("FT Imaginary")]
            print(
                f"the resulting complex number is of indices {real_index, imaginary_index} in order")
            # complex_numbers = self.chunks[real_index] + \
            #     1j * self.chunks[imaginary_index]
        # return complex_numbers

    def handle_radio_button_toggled(self):
        if self.main_window.ui.radioButton_In.isChecked():
            self.selection_mode = 1
        elif self.main_window.ui.radioButton_Out.isChecked():
            self.selection_mode = 0

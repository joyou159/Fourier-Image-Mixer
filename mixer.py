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
from PyQt6.QtCore import Qt, QRect

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
        self.weight_reference = np.repeat(100, 4)
        self.weight_value = np.repeat(1, 4)
        self.selection_mode = 1
        # the index of the FTviewport at which the mixing begins
        self.higher_precedence_ft_component = None
        self.chunks = {
            "0": np.array([]),
            "1": np.array([]),
            "2": np.array([]),
            "3": np.array([])
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

    def collect_chunks(self):
        for ind in range(len(self.chunks)):
            if self.main_window.image_ports[ind].original_img != None:
                selection_matrix = self.get_chunk(ind)
                curr_chunk = self.main_window.components_ports[ind].component_data * \
                    selection_matrix
                self.chunks[str(ind)] = curr_chunk

    def generalize_rectangle(self, ind):
        if self.higher_precedence_ft_component == None:
            self.higher_precedence_ft_component = ind
            print("higher_precedence_ft_component has changed")
            # the object of position is the same as object of data
        for i, port in enumerate(self.main_window.components_ports):
            if self.main_window.image_ports[i].original_img != None:
                port.current_rect = QRect(
                    self.main_window.components_ports[self.higher_precedence_ft_component].current_rect
                )
                port.press_pos, port.release_pos = port.current_rect.topLeft(
                ), port.current_rect.bottomRight()

                port.holdRect = True
                port.set_image()
                port.deactivate_drawing_events()
                print("generalize")

    def get_chunk(self, ind):
        port = self.main_window.components_ports[ind]

        if self.selection_mode:
            selection_matrix = np.zeros_like(
                port.component_data)
        else:
            selection_matrix = np.ones_like(
                port.component_data)

        start_pos = port.press_pos  # (x1,y1)
        end_pos = port.release_pos  # (x2,y2)

        print(round(start_pos.y()), round(end_pos.y()))
        print(round(start_pos.x()), round(end_pos.x()))

        print("different segmentation")

        for i in range(round(start_pos.y()), round(end_pos.y()) + 1):
            for j in range(round(start_pos.x()), round(end_pos.x()) + 1):
                if self.selection_mode:
                    selection_matrix[i, j] = 1
                else:
                    selection_matrix[i, j] = 0
        return selection_matrix

    def mix_images(self):
        self.check_pair_validity()
        self.collect_chunks()
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
        # self.mixed_image = ifft2(self.fft2_output)
        # self.set_image()

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
            mag_index = str(pair_indices[pair_comp.index("FT Magnitude")])
            phase_index = str(pair_indices[pair_comp.index("FT Phase")])
            print(
                f"the resulting complex number is of indices {mag_index, phase_index} in order")
            print(self.chunks[mag_index].shape,
                  self.chunks[phase_index].shape)
            # complex_numbers = self.weight_value[mag_index]* self.chunks[mag_index] * np.exp(
            #     1j * self.chunks[phase_index] * self.weight_value[phase_index] )
        else:
            real_index = str(pair_indices[pair_comp.index("FT Real")])
            imaginary_index = str(
                pair_indices[pair_comp.index("FT Imaginary")])
            print(
                f"the resulting complex number is of indices {real_index, imaginary_index} in order")
            print(self.chunks[real_index].shape,
                  self.chunks[imaginary_index].shape)
            # complex_numbers = self.chunks[real_index] * self.weight_value[real_index] + \
            #     1j * self.chunks[imaginary_index] * self.weight_value[imaginary_index]
        # return complex_numbers

    def handle_radio_button_toggled(self):
        if self.main_window.ui.radioButton_In.isChecked():
            self.selection_mode = 1
        elif self.main_window.ui.radioButton_Out.isChecked():
            self.selection_mode = 0

    def handle_weight_sliders(self):
        slider = self.sender()
        slider_ind = self.main_window.ui_vertical_sliders.index(slider)
        new_weight_value = slider.value() / self.weight_reference[slider_ind]
        self.weight_reference[slider_ind] = slider.value()
        self.weight_value[slider_ind] = new_weight_value

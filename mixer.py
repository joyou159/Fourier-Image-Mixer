from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QWidget,
)

from PIL import Image

from PyQt6.QtCore import QRect

from PyQt6 import QtWidgets
import sys
import time
import threading
import logging
# Placeholder for FT-related functionalities
import numpy as np
from scipy.fft import ifft2, fftshift, ifftshift
from PyQt6.QtWidgets import QWidget

# Configure logging to capture all log levels
logging.basicConfig(filemode="a", filename="our_log.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


class ImageMixer(QWidget):
    def __init__(self, main_window, parent=None):
        # Initialize the class
        super().__init__(parent)

        # Initialize instance variables
        self.mix_image = None
        self.main_window = main_window
        self.fft2_output = []
        self.mixing_comp = []
        self.weight_value = np.repeat(1.0, 4)
        self.selection_mode = 1
        self.output = 1        # the index of the FTviewport at which the mixing begins
        self.higher_precedence_ft_component = None
        self.reset_after_mixing_and_deselect()

        # Connect radio button toggled signals to corresponding handlers
        self.main_window.ui.radioButton_In.toggled.connect(
            self.handle_radio_button_toggled)
        self.main_window.ui.radioButton_Out.toggled.connect(
            self.handle_radio_button_toggled)

        # Connect output radio button toggled signals to corresponding handlers
        self.main_window.ui.radioButton1.toggled.connect(
            self.handle_out_radio_button_toggled)
        self.main_window.ui.radioButton2.toggled.connect(
            self.handle_out_radio_button_toggled)

        # Set default radio button states
        self.main_window.ui.radioButton_In.setChecked(True)
        self.main_window.ui.radioButton1.setChecked(True)

    def collect_chunks(self):
        """
        Collects chunks of data and stores them in the `self.chunks` dictionary.
        """
        for ind in range(len(self.chunks)):
            # meaning that there is a region selected.
            if self.main_window.image_ports[ind].original_img != None:
                port = self.main_window.components_ports[ind]
                if port.holdRect:
                    selection_matrix = self.get_selection_matrix(ind)
                    curr_chunk = selection_matrix * \
                        port.component_data
                else:
                    curr_chunk = port.component_data

                self.chunks[str(ind)] = curr_chunk

    def get_selection_matrix(self, ind):
        """
        Generates a binary selection matrix based on user-defined selection area.

        Parameters:
        - ind (int): Index of the component.

        Returns:
        numpy.ndarray: Binary matrix (1 for selected, 0 for unselected).

        Retrieves user-defined selection area from the specified component in the
        collection, creating a binary matrix based on the current selection mode.

        Assumes the component has attributes: 'press_pos', 'release_pos',
        'original_img', 'resized_img', 'component_data', and 'map_rectangle'.
        """
        port = self.main_window.components_ports[ind]
        start_pos = port.press_pos  # (x1,y1)
        end_pos = port.release_pos  # (x2,y2)
        map_up_size = port.original_img.size
        port_dim = port.resized_img.size
        position_list = [(port.press_pos.x(), port.press_pos.y()),
                         (port.release_pos.x(), port.release_pos.y())]
        mapped_up_position_list = port.map_rectangle(
            position_list, port_dim, map_up_size)
        # [(x_start,y_start),(x_end,y_end)]
        if self.selection_mode:
            selection_matrix = np.zeros_like(port.component_data)
        else:
            selection_matrix = np.ones_like(port.component_data)

        # y_iteration
        for i in range(mapped_up_position_list[0][1], round(mapped_up_position_list[1][1] + 1)):
            # X_iteration
            for j in range(mapped_up_position_list[0][0], mapped_up_position_list[1][0] + 1):
                if self.selection_mode:  # 1 --> inner
                    selection_matrix[i, j] = 1
                else:  # outer
                    selection_matrix[i, j] = 0
        return selection_matrix

    def generalize_rectangle(self, ind):
        """
        Generalizes the rectangle based on the given index.

        Args:
            ind (int): The index to generalize the rectangle with.
        """
        if self.higher_precedence_ft_component is None:
            self.higher_precedence_ft_component = ind
            # the object of position is the same as object of data

        for i, port in enumerate(self.main_window.components_ports):
            image = self.main_window.image_ports[i]
            if image.original_img is not None:
                port.current_rect = QRect(
                    # deep copy
                    self.main_window.components_ports[self.higher_precedence_ft_component].current_rect)

                port.press_pos, port.release_pos = port.current_rect.topLeft(
                ), port.current_rect.bottomRight()

                port.deactivate_drawing_events()
                port.set_image()

    def mix_images(self):

      # Decode the pairs to determine the mixing order
        mixing_choices = self.collect_mixing_choices()

        # Compose the complex output for the first pair
        self.fft2_output = []
        self.fft2_output = self.compose_complex(mixing_choices)

        # Print the shape of the fft2_output
        logging.info(f"the shape of fft_output{self.fft2_output.shape}")

        # Calculate the mixed image using inverse Fourier transform
        self.mixed_image = np.real(ifft2(self.fft2_output)).astype(np.uint8)

        # Create an image object from the mixed image array
        self.mixed_image = Image.fromarray(self.mixed_image, mode="L")

        # Set the mixed image as the output image in the main window
        self.main_window.out_ports[self.output].set_image(self.mixed_image)

        # Deselect any selected items in the main window
        self.reset_after_mixing_and_deselect()

    def collect_mixing_choices(self):
        """
        Decode the image number pairs from the UI mixing combo boxes.

        Returns:
            list: The decoded image number pairs.
        """
        if self.main_window.curr_mode == "Mag and Phase":
            mixing_choices = {"FT Magnitude": [], "FT Phase": []}
        else:
            mixing_choices = {"FT Real": [], "FT Imaginary": []}

        # Iterate over the UI mixing combo boxes
        for i, combo in enumerate(self.main_window.ui_image_combo_boxes):
            # Get the selected image number from the combo box
            # Add the image number to the mixing order list
            if np.any(self.chunks[str(i)]):
                mixing_choices[combo.currentText()].append(i)
        return mixing_choices

    def compose_complex(self, mixing_choices):  # [0,1] [Mag,phase]
        """
        Composes a complex number based on the given pair indices and pair components.

        Args:
            pair_indices (list of int): The indices of the pair components.
            pair_comp (list of str): The names of the pair components.

        Returns:
            complex: The composed complex number.

        Raises:
            None
        """
        if "FT Magnitude" in mixing_choices:
            mag_indices = mixing_choices["FT Magnitude"]
            phase_indices = mixing_choices["FT Phase"]
            total_mag = self.accumulate(mag_indices)
            total_phase = self.accumulate(phase_indices)
            complex_numbers = total_mag * np.exp(
                1j * total_phase)
        else:
            real_indices = mixing_choices["FT Real"]
            img_indices = mixing_choices["FT Imaginary"]
            total_real = self.accumulate(real_indices)
            total_imaginary = self.accumulate(img_indices)
            complex_numbers = total_real + \
                1j * total_imaginary

        return ifftshift(complex_numbers)

    def accumulate(self, indices):
        output_size = max(self.chunks.values(), key=len).shape
        product_output = np.zeros(output_size, dtype=float)
        for index in indices:
            product_output += (self.chunks[str(index)] *
                               self.weight_value[index])
        return product_output

    def handle_radio_button_toggled(self):
        """
        Handle the event when a radio button is toggled.

        This function is called when a radio button is toggled in the UI. It updates the `selection_mode` attribute based on the
        state of the radio buttons.

        """
        if self.main_window.ui.radioButton_In.isChecked():
            # If the "In" radio button is checked, set the selection mode to 1
            self.selection_mode = 1
        elif self.main_window.ui.radioButton_Out.isChecked():
            # If the "Out" radio button is checked, set the selection mode to 0
            self.selection_mode = 0

    def handle_out_radio_button_toggled(self):
        """
        Handle the toggling of the output radio buttons.

        This function is called when the user toggles the output radio buttons.
        It updates the `output` variable based on the selected radio button.

        """
        if self.main_window.ui.radioButton1.isChecked():
            # Set output to 0 if radioButton1 is checked
            self.output = 0
        elif self.main_window.ui.radioButton2.isChecked():
            # Set output to 1 if radioButton2 is checked
            self.output = 1

    def handle_weight_sliders(self):
        """
        Update the weight values based on the slider input.
        """
        # Get the slider that triggered the event
        slider = self.sender()

        # Find the index of the slider in the list of vertical sliders
        slider_ind = self.main_window.ui_vertical_sliders.index(slider)

        # Calculate the new weight value based on the slider value and the previous weight reference
        new_weight_value = slider.value() / 100

        # Update the weight value with the calculated new value
        self.weight_value[slider_ind] = new_weight_value

    def reset_after_mixing_and_deselect(self):
        """
        Resets the state of the object after mixing and deselecting.
        """
        # Reset the higher_precedence_ft_component attribute to None
        # Reset the chunks dictionary with empty arrays
        self.chunks = {
            "0": np.array([]),
            "1": np.array([]),
            "2": np.array([]),
            "3": np.array([])
        }

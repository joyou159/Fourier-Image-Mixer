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
from scipy.fft import ifft2, fftshift
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
        self.weight_reference = np.repeat(100, 4)
        self.weight_value = np.repeat(1, 4)
        self.selection_mode = 1
        self.output = 1        # the index of the FTviewport at which the mixing begins
        self.higher_precedence_ft_component = None
        self.chunks = {
            "0": np.array([]),
            "1": np.array([]),
            "2": np.array([]),
            "3": np.array([])
        }

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

    def check_pair_validity(self):
        """
        Check the validity of the pairs selected for mixing.

        Raises:
            ValueError: If the selected pairs are not valid.
        """
        valid_pairs = [
            ("FT Magnitude", "FT Phase"),
            ("FT Phase", "FT Magnitude"),
            ("FT Real", "FT Imaginary"),
            ("FT Imaginary", "FT Real"),
            ("", "")
        ]

        components = self.main_window.components

        self.mixing_comp = []

        for combo in self.main_window.ui_mixing_combo_boxes:

            image_selection = combo.currentIndex()

            if image_selection == 0:
                component = ""
            else:
                component = components[str(image_selection)]

            self.mixing_comp.append(component)

        pair1 = (self.mixing_comp[0], self.mixing_comp[1])
        pair2 = (self.mixing_comp[2], self.mixing_comp[3])

        if pair1 not in valid_pairs or pair2 not in valid_pairs:
            self.main_window.show_error_message('Please choose valid pairs')
            logging.error("the user didn't choose valid pairs ")
            return 0

    def collect_chunks(self):
        """
        Collects chunks of data and stores them in the `self.chunks` dictionary.
        """
        for ind in range(len(self.chunks)):
            if self.main_window.image_ports[ind].original_img is not None:
                curr_chunk = self.get_chunk(ind)
                self.chunks[str(ind)] = curr_chunk

    def get_chunk(self, ind):
        """Get the selected region of an image based on the given index.

        Args:
            ind (int): The index of the component port.

        Returns:
            numpy.ndarray: The selected region of the image.
        """
        # Get the component port
        port = self.main_window.components_ports[ind]

        # Get the start and end positions of the port
        start_pos = port.press_pos  # (x1,y1)
        end_pos = port.release_pos  # (x2,y2)

        if self.selection_mode:
            # Extract the selected region within the port
            selected_region = self.inner_region_extraction(
                port, start_pos, end_pos)
        else:
            # Extract the selected region outside the port
            selected_region = self.outer_region_extraction(
                port, start_pos, end_pos)

        # Print the size of the selected region
        logging.info(f"The size of the selected region{
                     selected_region.shape}")

        return selected_region

    def inner_region_extraction(self, port, start_pos, end_pos) -> np.ndarray:
        """
        Extracts a region from the component_data matrix based on the given start and end positions.

        Args:
            port (Port): The port containing the component_data matrix.
            start_pos (Vector2D): The starting position of the region.
            end_pos (Vector2D): The ending position of the region.

        Returns:
            np.ndarray: The extracted region as a numpy array.
        """
        selected_region = np.zeros((round(end_pos.y() - start_pos.y()) + 1,
                                    round(end_pos.x() - start_pos.x()) + 1))

        for ii, i in enumerate(range(round(start_pos.y()), round(end_pos.y()) + 1)):
            for jj, j in enumerate(range(round(start_pos.x()), round(end_pos.x()) + 1)):
                if self.selection_mode:
                    selected_region[ii, jj] = port.component_data[i, j]

        return selected_region

    def outer_region_extraction(self, port, start_pos, end_pos):
        """
        Extracts the outer region of a component's data matrix.

        Parameters:
            - port: The component's port.
            - start_pos: The starting position of the region.
            - end_pos: The ending position of the region.

        Returns:
            - selected_region: The extracted outer region of the component's data matrix.
        """

        # Calculate the shape of the inner region
        inner_region_shape = (
            round(end_pos.y() - start_pos.y()) + 1, round(end_pos.x() - start_pos.x()) + 1)

        # Get the shape of the full matrix
        full_matrix_shape = port.component_data.shape

        # Create an array to store the selected region
        selected_region = np.zeros(
            (full_matrix_shape[0], full_matrix_shape[1] - inner_region_shape[1]))

        # Iterate over each row in the full matrix
        for i in range(full_matrix_shape[0]):
            curr_column = 0  # reset the columns

            # Iterate over each column in the full matrix
            for j in range(full_matrix_shape[1]):

                # Check if the current cell is not within the inner region
                if j not in range(round(start_pos.x()), round(end_pos.x()) + 1) and i not in (range(round(start_pos.y()), round(end_pos.y()) + 1)):

                    # Copy the value from the component's data matrix to the selected region
                    selected_region[i, curr_column] = port.component_data[i, j]
                    curr_column += 1

        return selected_region

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
            if self.main_window.image_ports[i].original_img is not None:
                port.current_rect = QRect(
                    self.main_window.components_ports[self.higher_precedence_ft_component].current_rect)

                port.press_pos, port.release_pos = port.current_rect.topLeft(
                ), port.current_rect.bottomRight()

                port.holdRect = True
                port.set_image()
                port.deactivate_drawing_events()

    def mix_images(self):

        # Collect image chunks
        self.collect_chunks()

        # Decode the pairs to determine the mixing order
        mixing_order = self.decode_pairs()

        # Get the indices and components of the first pair
        pair_1_indices = (mixing_order[0], mixing_order[1])
        pair_1_comp = (self.mixing_comp[0], self.mixing_comp[1])

        # Get the indices and components of the second pair
        pair_2_indices = (mixing_order[2], mixing_order[3])
        pair_2_comp = (self.mixing_comp[2], self.mixing_comp[3])

        # Print the indices of the pairs
        print(pair_1_indices, pair_2_indices)

        # Compose the complex output for the first pair
        self.fft2_output = self.compose_complex(pair_1_indices, pair_1_comp)

        # Add the complex output for the second pair to the first pair
        self.fft2_output += self.compose_complex(pair_2_indices, pair_2_comp)

        # Print the shape of the fft2_output
        logging.info(f"the shape of fft_output{self.fft2_output.shape}")

        # Calculate the mixed image using inverse Fourier transform
        self.mixed_image = abs(ifft2(fftshift(self.fft2_output)))

        # Print the first 10 elements of the mixed image
        print(self.mixed_image[0, 0:10])

        # Create an image object from the mixed image array
        self.mixed_image = Image.fromarray(self.mixed_image, mode="L")

        # Set the mixed image as the output image in the main window
        self.main_window.out_ports[self.output].set_image(self.mixed_image)

        # Deselect any selected items in the main window
        self.main_window.deselect()

    def decode_pairs(self):
        """
        Decode the image number pairs from the UI mixing combo boxes.

        Returns:
            list: The decoded image number pairs.
        """
        mixing_order = []
        # Iterate over the UI mixing combo boxes
        for combo in self.main_window.ui_mixing_combo_boxes:
            # Get the selected image number from the combo box
            image_num = combo.currentIndex() - 1  # Subtract 1 to get the index of the image
            # Add the image number to the mixing order list
            mixing_order.append(image_num)
        return mixing_order

    def compose_complex(self, pair_indices, pair_comp):
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
        if -1 in pair_indices:
            return np.zeros_like(self.fft2_output)
        if "FT Magnitude" in pair_comp:
            mag_index = str(pair_indices[pair_comp.index("FT Magnitude")])
            phase_index = str(pair_indices[pair_comp.index("FT Phase")])
            print(
                f"the resulting complex number is of indices {mag_index, phase_index} in order")
            print(self.chunks[mag_index].shape,
                  self.chunks[phase_index].shape)
            complex_numbers = self.weight_value[int(mag_index)] * self.chunks[mag_index] * np.exp(
                1j * self.chunks[phase_index] * self.weight_value[int(phase_index)])
        else:
            real_index = str(pair_indices[pair_comp.index("FT Real")])
            imaginary_index = str(
                pair_indices[pair_comp.index("FT Imaginary")])
            print(
                f"the resulting complex number is of indices {real_index, imaginary_index} in order")
            print(self.chunks[real_index].shape,
                  self.chunks[imaginary_index].shape)
            complex_numbers = self.chunks[real_index] * self.weight_value[int(real_index)] + \
                1j * self.chunks[imaginary_index] * \
                self.weight_value[int(imaginary_index)]
        return complex_numbers

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
        new_weight_value = slider.value() / self.weight_reference[slider_ind]

        # Update the weight value with the calculated new value
        self.weight_value[slider_ind] = new_weight_value

        # Update the weight reference with the new slider value
        self.weight_reference[slider_ind] = slider.value()

    def reset_after_mixing_and_deselect(self):
        """
        Resets the state of the object after mixing and deselecting.
        """
        # Reset the higher_precedence_ft_component attribute to None
        self.higher_precedence_ft_component = None

        # Reset the chunks dictionary with empty arrays
        self.chunks = {
            "0": np.array([]),
            "1": np.array([]),
            "2": np.array([]),
            "3": np.array([])
        }

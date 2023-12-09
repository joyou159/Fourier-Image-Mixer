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
        self.components_ports = []
        self.components = {"0": '', "1": '', '2': '', '3': ''}
        # mixer and its connection line
        self.mixer = ImageMixer(self)
        self.ui.mixxer.clicked.connect(self.mixer.mix_images)

        self.load_ui_elements()
        self.showFullScreen()
        self.ui.keyPressEvent = self.keyPressEvent

    def keyPressEvent(self, event):
        # Handle key events, for example, pressing ESC to exit full screen
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()  # Show the window in normal size
        else:
            super().keyPressEvent(event)

    def create_image_viewport(self, parent, mouse_double_click_event_handler):
        image_port = ImageViewport(self)
        image_layout = QVBoxLayout(parent)
        image_layout.addWidget(image_port)
        image_port.mouseDoubleClickEvent = mouse_double_click_event_handler
        return image_port

    def load_ui_elements(self):
        """
        Load UI elements.

        This function is responsible for loading the UI elements of the application. It initializes and configures various UI components 
        such as view ports, combo boxes, sliders, and connects them to the appropriate event handlers.

        """
        # List of original UI view ports
        ui_view_ports = [self.ui.original1, self.ui.original2,
                         self.ui.original3, self.ui.original4]

        self.ui_view_ports_comp = [
            self.ui.component_image1, self.ui.component_image2, self.ui.component_image3, self.ui.component_image4]
        # List of combo boxes for UI
        self.ui_image_combo_boxes = [
            self.ui.combo1, self.ui.combo2, self.ui.combo3, self.ui.combo4]

        # List of combo boxes for mixing UI
        self.ui_mixing_combo_boxes = [
            self.ui.combo11, self.ui.combo12, self.ui.combo13, self.ui.combo14]

        # Create image viewports and bind browse_image function to the event
        self.image_ports.extend([
            self.create_image_viewport(
                ui_view_ports[i], lambda event, index=i: self.browse_image(event, index))
            for i in range(4)
        ])

        self.ui_vertical_sliders = [
            self.ui.Slider_weight1, self.ui.Slider_weight2, self.ui.Slider_weight3, self.ui.Slider_weight4]

        # Add items to combo boxes for UI
        # self.add_items_to_combo_boxes(
        #     self.ui_image_combo_boxes, ["Magnitude", "Phase", "Real", "Imaginary"])

        # Add items to combo boxes for mixing UI
        self.add_items_to_combo_boxes(self.ui_mixing_combo_boxes, [
                                      f'image{i+1}' for i in range(4)])

        # List of brightness sliders
        self.ui_brightness_sliders = [
            getattr(self.ui, f"brightnessSlider{i+1}") for i in range(4)]

        # List of contrast sliders
        self.ui_contrast_sliders = [
            getattr(self.ui, f"contrastSlider{i+1}") for i in range(4)]

        # Set minimum, maximum, and initial value for brightness and contrast sliders
        for slider in self.ui_brightness_sliders + self.ui_contrast_sliders:
            slider.setMinimum(-255)
            slider.setMaximum(255)
            slider.setValue(0)
            slider.valueChanged.connect(self.update_slider)

    def browse_image(self, event, index: int):
        """
        Browse for an image file and set it for the ImageViewport at the specified index.

        Args:
            event: The event that triggered the image browsing.
            index: The index of the ImageViewport to set the image for.
        """
        file_filter = "Raw Data (*.png *.jpg *.jpeg *.jfif)"
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Signal File', './', filter=file_filter)

        if image_path and 0 <= index < len(self.image_ports):
            self.image_ports[index].set_image(image_path)
            image_port = self.image_ports[index]
            # image.update_image_parameters(index)
            self.ui_image_combo_boxes[index].addItems(
                ["FT Magnitude", "FT Phase", "FT Real", "FT Imaginary"])
            image_port.update_image_parameters(index, image_path)
            # image_port.calculate_ft_components(image_path)

    def create_image_viewport(self, parent, mouse_double_click_event_handler):
        """
        Creates an image viewport and adds it to the specified parent widget.

        Args:
            parent: The parent widget to which the image viewport will be added.
            mouse_double_click_event_handler: The event handler function to be called when a mouse double-click event occurs on the image viewport.

        Returns:
            The created image viewport.

        """
        image_port = ImageViewport(self)
        image_layout = QVBoxLayout(parent)
        image_layout.addWidget(image_port)
        image_port.mouseDoubleClickEvent = mouse_double_click_event_handler
        return image_port

    def add_items_to_combo_boxes(self, combo_boxes, items):
        """
        Adds the specified items to the given combo boxes.

        Args:
            combo_boxes (list): A list of combo boxes to which the items will be added.
            items (list): A list of items to be added to the combo boxes.

        Returns:
            None
        """
        for combo_box in combo_boxes:
            combo_box.addItems(items)

    def update_slider(self):
        """
        Update the brightness and contrast values of each image port based on the slider values.
        """
        # Iterate over the brightness and contrast sliders and their corresponding image ports
        for index, (brightness_slider, contrast_slider) in enumerate(zip(self.ui_brightness_sliders, self.ui_contrast_sliders)):
            # Update the brightness and contrast values of the image port
            self.image_ports[index].brightness = brightness_slider.value()
            self.image_ports[index].contrast = contrast_slider.value()
            # Update the display of the image port
            self.image_ports[index].update_display()


def main():
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

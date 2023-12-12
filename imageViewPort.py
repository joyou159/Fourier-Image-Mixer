import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,  
)
from PyQt6.QtGui import QPixmap, QImage,  QImageReader, QPainter
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QBuffer, QByteArray
from PyQt6 import QtWidgets
from PIL import Image, ImageQt, ImageEnhance
# Placeholder for FT-related functionalities
import numpy as np
from scipy.fft import fft2, ifft2, fftshift



class ImageViewport(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        # keep track of mini figure size.
        self.original_img = None
        self.resized_img = None
        self.viewport_image_ind = None
        self.slider_pairs = None  # (brightness,contrast)
        self.brightness = 0
        self.contrast = 100

        self.main_window = main_window

        # self.layout = QVBoxLayout(self)
        # self.setLayout(self.layout)

        # connect the combo boxes value changed to a function that shows the corresponding FT type, and to the set_image_op

    def set_image(self, image_path):
        try:
            image = Image.open(image_path).convert('L')  # Convert to grayscale

            self.original_img = image
            self.update_display()

        except Exception as e:
            print(f"Error opening image: {e}")

    def update_display(self):

        if self.original_img:
            self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.original_img:
            painter = QPainter(self)

            # Draw the images onto the widget using the minimum width and height
            x, y = 0, 0

            adjusted_img = self.adjust_brightness_contrast(self.original_img)
            self.resized_img = adjusted_img.resize(
                (self.width(), self.height()))

            pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.resized_img))
            painter.drawPixmap(x, y, pixmap)

            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def adjust_brightness_contrast(self, img):
        # Adjust brightness and contrast
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance((self.brightness + 255) / 255.0)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance((self.contrast + 127) / 127.0)

        return img

    def update_image_parameters(self, index, path):
        self.main_window.image_ports[index].set_image(path)
        self.viewport_image_ind = index
        # pick FT type for each image by default
        # self.main_window.ui_image_combo_boxes[index].setCurrentIndex(index)
        # set some attributes of the Image
        # component = self.main_window.ui_image_combo_boxes[index].currentText()
        # self.main_window.components[str(index)] = component
        # update the mixing boxes and sliders
        self.main_window.ui_mixing_combo_boxes[index].setCurrentIndex(index)
        self.main_window.ui_vertical_sliders[index].setValue(100)

    def update_slider(self, ind):
        """
        Update the brightness and contrast values of each image port based on the slider values.
        """

        self.brightness = self.slider_pairs[0].value()
        self.contrast = self.slider_pairs[1].value()
        # Update the display of the image port
        self.main_window.image_ports[self.viewport_image_ind].update_display()
        self.main_window.components_ports[self.viewport_image_ind].update_FT_components(
        )

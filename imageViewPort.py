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
        self.slider_pairs = None  # (brightness, contrast)
        self.brightness = 0
        self.contrast = 100

        self.last_x = 0
        self.last_y = 0

        self.main_window = main_window

        # connect the combo boxes value changed to a function that shows the corresponding FT type, and to the set_image_op

    def set_image(self, image_path):
        try:
            image = Image.open(image_path).convert('L')  # Convert to grayscale

            # Set default brightness and contrast values
            self.brightness = 0
            self.contrast = 100

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

            # Calculate the new size while maintaining the aspect ratio
            aspect_ratio = self.original_img.width / self.original_img.height
            new_width = self.width()
            new_height = int(new_width / aspect_ratio)

            if new_height > self.height():
                new_height = self.height()
                new_width = int(new_height * aspect_ratio)

            # Calculate the position (x, y) to center the image
            x = (self.width() - new_width) // 2
            y = (self.height() - new_height) // 2

            # Resize the image
            self.adjust_brightness_contrast()
            self.resized_img = self.resized_img.resize((new_width, new_height))
            # Draw the image centered on the widget
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.resized_img))
            painter.drawPixmap(x, y, pixmap)

            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def mouseMoveEvent(self, event):
        if self.resized_img and event.buttons() == Qt.RightButton:
            # Calculate the displacement from the last mouse position
            dx = event.x() - self.last_x
            dy = event.y() - self.last_y

            # Update brightness based on horizontal movement
            self.brightness += dx
            # Update contrast based on vertical movement
            self.contrast += dy

            # Clamp brightness and contrast values to valid ranges
            self.brightness = max(-255, min(255, self.brightness))
            self.contrast = max(-127, min(127, self.contrast))

            # Update the image with adjusted brightness and contrast
            self.adjust_brightness_contrast()

            # Update the display
            self.update_display()

        # Save the current mouse position for the next event
        self.last_x = event.x()
        self.last_y = event.y()

    def mousePressEvent(self, event):
        # Save the initial mouse position when the mouse is pressed
        self.last_x = event.x()
        self.last_y = event.y()

    def adjust_brightness_contrast(self):
        # Adjust brightness and contrast
        enhancer = ImageEnhance.Brightness(self.original_img)
        img = enhancer.enhance((self.brightness + 255) / 255.0)
        enhancer = ImageEnhance.Contrast(img)
        self.resized_img = enhancer.enhance((self.contrast + 127) / 127.0)

    def update_image_parameters(self, path):
        #images indices by openeing order
        order = self.main_window.open_order
        #latest opened image index
        current = order[-1] 
        #used for orderly set the ft components for each opened image
        selection = len(order)-1
        
        self.main_window.image_ports[current].set_image(path)
        # pick FT type for each image by default
        self.main_window.ui_image_combo_boxes[current].setCurrentIndex(selection)
        # set some attributes of the Image
        component = self.main_window.ui_image_combo_boxes[current].currentText()
        self.main_window.components[str(current+1)] = component
        # update the mixing boxes and sliders
        self.main_window.ui_mixing_combo_boxes[selection].setCurrentIndex(current+1)
        self.main_window.ui_vertical_sliders[selection].setValue(100)

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

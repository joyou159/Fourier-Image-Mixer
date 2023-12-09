import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
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
        self.images = []  # keep track of mini figure size.
        self.resized_img_data = None
        self.ft_component = dict()  # the viewport of the FT components
        self.resized_imgs = []
        self.brightness = 0
        self.contrast = 100

        self.main_window = main_window

        # self.layout = QVBoxLayout(self)
        # self.setLayout(self.layout)

        # connect the combo boxes value changed to a function that shows the corresponding FT type, and to the set_image_op
        for index, combo_box in enumerate(self.main_window.ui_image_combo_boxes):
            combo_box.currentIndexChanged.connect(
                self.handle_image_combo_boxes_selection)

    def set_image(self, image_path):
        try:
            image = Image.open(image_path).convert('L')  # Convert to grayscale
            self.images.append(image)
            self.update_display()
        except Exception as e:
            print(f"Error opening image: {e}")

    def update_display(self):
        if self.images:
            self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.images:
            painter = QPainter(self)

            # Draw the images onto the widget using the minimum width and height
            x, y = 0, 0
            for img in self.images:
                adjusted_img = self.adjust_brightness_contrast(img)
                resized_img = adjusted_img.resize(
                    (self.width(), self.height()))
                pixmap = QPixmap.fromImage(ImageQt.ImageQt(resized_img))
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
    # def calculate_ft_components(self, image_path):
    #     if image_path is not None:
    #         # Compute the 2D Fourier Transform
    #         fft = np.fft.fft2(self.image)

    #         # Shift the zero-frequency component to the center
    #         fft_shifted = np.fft.fftshift(fft)

    #         # Compute the magnitude of the spectrum
    #         mag = np.abs(fft)

    #         # Compute the phase of the spectrum
    #         phase = np.angle(self.fft)

    #         # real ft components
    #         real = self.fft.real

    #         # imaginary ft components
    #         imaginary = self.fft.imag

    #         # Store the calculated components
    #         self.ft_components["FT Magnitude"] = QImage(
    #             mag.data, mag.shape[1], mag.shape[0], QImage.Format.Format_Grayscale8)

    #         self.ft_components["FT Phase"] = QImage(
    #             phase.data, phase.shape[1], phase.shape[0], QImage.Format.Format_Grayscale8)

    #         self.ft_components["FT Real"] = QImage(
    #             real.data, real.shape[1], real.shape[0], QImage.Format.Format_Grayscale8)

    #         self.ft_components["FT Imaginary"] = QImage(
    #             imaginary.data, imaginary.shape[1], imaginary.shape[0], QImage.Format.Format_Grayscale8)

    def handle_image_combo_boxes_selection(self):
        sender_combo_box = self.sender()
        combo_ind = self.main_window.ui_image_combo_boxes.index(
            sender_combo_box)
        target_combo = self.main_window.ui_image_combo_boxes[self.main_window.ui_image_combo_boxes.index(
            sender_combo_box)]
        # now we have the combo box , the new operation now we set the image(combo box index = image index) to the new chosen op
        component = target_combo.currentText()
        self.main_window.components[str(combo_ind)] = component

    def update_image_parameters(self, index, path):
        self.main_window.image_ports[index].set_image(path)
        # pick FT type for each image by default
        self.main_window.ui_image_combo_boxes[index].setCurrentIndex(index)
        # set some attributes of the Image
        component = self.main_window.ui_image_combo_boxes[index].currentText()
        self.main_window.components[str(index)] = component
        # update the mixing boxes and sliders
        self.main_window.ui_mixing_combo_boxes[index].setCurrentIndex(index)
        self.main_window.ui_vertical_sliders[index].setValue(100)

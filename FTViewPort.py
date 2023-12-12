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
from PIL import Image, ImageQt, ImageEnhance
from PyQt6 import QtWidgets
from PyQt6.QtGui import QPainter, QBrush, QPen
from PyQt6.QtCore import Qt, QRect
# Placeholder for FT-related functionalities
import numpy as np
from scipy.fft import fft2, ifft2, fftshift


class FTViewPort(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.viewport_FT_ind = None  # the index of the components view port
        self.combo_box = None  # as widget object
        self.main_window = main_window
        self.curr_component_name = None
        self.component_data = None
        self.ft_components = {}
        self.original_img = None
        self.press_pos = None
        self.release_pos = None
        self.current_rect = None
        self.drawRect = False

    def update_FT_components(self):
        self.component_data = np.array(
            self.main_window.image_ports[self.viewport_FT_ind].resized_img)
        self.calculate_ft_components()
        self.handle_image_combo_boxes_selection()

    def handle_image_combo_boxes_selection(self):
        if self.ft_components:
            self.curr_component_name = self.combo_box.currentText()
            self.main_window.components[str(
                self.viewport_FT_ind + 1)] = self.curr_component_name
            self.set_image()

    def set_image(self):
        try:
            # Convert to grayscale
            image = self.ft_components[self.curr_component_name]

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

            # Draw the images onto the widget using the minimum width and height
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.original_img))
            painter.drawPixmap(x, y, pixmap)

            painter.end()
        if self.drawRect:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.red, Qt.DiagCrossPattern))
            painter.drawRect(self.current_rect)
            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_pos = (event.position().x(), event.position().y())
            print("Mouse Pressed at:", event.position())
            self.current_rect = QRect(
                int(self.press_pos[0]), int(self.press_pos[1]), 0, 0)
            self.drawRect = True
            self.update_display()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.release_pos = (event.position().x(), event.position().y())
            print("Mouse Released at:", event.position())
            self.main_window.mixer.collect_chunks(self.viewport_FT_ind)
            self.drawRect = False
            self.update_display()

    def clear_rect(self):
        self.current_rect = None
        self.update_display()

    def calculate_ft_components(self):

        # Compute the 2D Fourier Transform
        fft = fft2(self.component_data)

        # Shift the zero-frequency component to the center
        fft_shifted = fftshift(fft)

        # Compute the magnitude of the spectrum
        mag = np.abs(fft_shifted)
        mag = np.log(np.abs(mag) + 1)

        # Compute the phase of the spectrum
        phase = np.angle(fft_shifted)

        # real ft components
        real = fft_shifted.real

        # imaginary ft components
        imaginary = fft_shifted.imag

        self.ft_components['FT Magnitude'] = Image.fromarray(
            mag, mode="L")

        self.ft_components['FT Phase'] = Image.fromarray(
            phase, mode='L')

        self.ft_components["FT Real"] = Image.fromarray(
            real, mode='L')

        self.ft_components["FT Imaginary"] = Image.fromarray(
            imaginary, mode='L')

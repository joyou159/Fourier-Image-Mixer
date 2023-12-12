import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,  
)
from PyQt6.QtGui import QPixmap, QImage,  QPainter
from PyQt6.QtCore import Qt, QSize
from PyQt6 import QtWidgets

from PIL import Image, ImageQt, ImageEnhance
# Placeholder for FT-related functionalities
import numpy as np
from scipy.fft import fft2, ifft2, fftshift


class ImageViewport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.images = []  # List to store all opened images
        self.resized_imgs = []

        self.brightness = 0
        self.contrast = 100       

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)


    def calculate_min_size(self):
        if self.resized_imgs:
            min_width = min(img.width for img in self.images)
            min_height = min(img.height for img in self.images)
            return min_width, min_height
        else:
            return None, None

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
                resized_img = adjusted_img.resize((self.width(), self.height()))
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



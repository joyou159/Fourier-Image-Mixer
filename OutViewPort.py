
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
)
from PyQt6.QtGui import QPixmap, QImage,  QImageReader, QPainter
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PIL import Image, ImageQt, ImageEnhance


class OutViewPort(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        # keep track of mini figure size.
        self.original_img = None
        self.resized_img = None
        # connect the combo boxes value changed to a function that shows the corresponding FT type, and to the set_image_op

    def set_image(self, output_image):
        try:
            # Convert to grayscale
            self.original_img = output_image
            self.update_display()

        except Exception:
            print("Error Displaying Output Image")

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
            self.resized_img = self.original_img.resize(
                (self.width(), self.height()))
            # Draw the image centered on the widget
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.resized_img))
            painter.drawPixmap(0, 0, pixmap)

            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

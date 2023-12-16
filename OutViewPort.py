from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap, QPainter
from PIL import ImageQt
import logging

# Configure logging to capture all log levels
logging.basicConfig(filemode="a", filename="our_log.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


class OutViewPort(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # keep track of mini figure size.
        self.original_img = None
        self.resized_img = None

    def set_image(self, output_image):
        try:
            # Convert to grayscale
            self.original_img = output_image

            self.update_display()

        except Exception:
            logging.error("Error Displaying Output Image")

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

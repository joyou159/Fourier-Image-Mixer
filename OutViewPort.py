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
            painter_out = QPainter(self)

            # Resize the image
            self.resized_img = self.original_img.resize(
                (self.width(), self.height()))

            # Draw the image centered on the widget
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.resized_img))
            painter_out.drawPixmap(0, 0, pixmap)

            painter_out.end()
            

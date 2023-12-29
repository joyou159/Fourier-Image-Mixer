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
            with QPainter(self) as painter_out:
                # Calculate the aspect ratio
                aspect_ratio = self.original_img.width / self.original_img.height

                # Calculate the size of the image to maintain the aspect ratio
                widget_width = self.width()
                widget_height = self.height()
                img_width = min(widget_width, int(widget_height * aspect_ratio))
                img_height = min(widget_height, int(widget_width / aspect_ratio))

                # Calculate the position to center the image
                x = (widget_width - img_width) // 2
                y = (widget_height - img_height) // 2

                # Resize the image
                self.resized_img = self.original_img.resize((img_width, img_height))

                # Draw the image centered on the widget
                pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.resized_img))
                painter_out.drawPixmap(x, y, pixmap)

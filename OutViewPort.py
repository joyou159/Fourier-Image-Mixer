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
                # Calculate the new size while preserving the aspect ratio
                img_width = self.original_img.width
                img_height = self.original_img.height
                widget_width = self.width()
                widget_height = self.height()

                aspect_ratio = img_width / img_height
                new_width = widget_width
                new_height = int(widget_width / aspect_ratio)

                if new_height > widget_height:
                    new_height = widget_height
                    new_width = int(widget_height * aspect_ratio)

                # Resize the image
                self.resized_img = self.original_img.resize((new_width, new_height))

                # Calculate the position to center the image
                x_pos = (widget_width - new_width) // 2
                y_pos = (widget_height - new_height) // 2

                # Draw the image centered on the widget
                pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.resized_img))
                painter_out.drawPixmap(x_pos, y_pos, pixmap)

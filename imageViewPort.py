
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt
from PIL import Image, ImageQt, ImageEnhance
import logging
import copy
import numpy as np


# Configure logging to capture all log levels
logging.basicConfig(filemode="a", filename="our_log.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


class ImageViewport(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        # keep track of mini figure size.
        self.original_img = None
        self.resized_img = None
        self.image_area = None
        self.viewport_image_ind = None  # (brightness, contrast)
        self.brightness = 0
        self.contrast = 0
        self.last_x = 0
        self.last_y = 0
        self.main_window = main_window

    def set_image(self, image_path):
        """
        Set the image for the object.

        Args:
            image_path (str): The path to the image file.

        Returns:
            None
        """
        try:
            # Open the image and convert it to grayscale
            image = Image.open(image_path).convert('L')

            # Set the original_img attribute to the grayscale image
            self.original_img = image

            self.resized_img = copy.deepcopy(self.original_img)  # Deep copy

            self.image_area = self.original_img.height * self.original_img.width

            self.main_window.images_areas[self.viewport_image_ind] = self.image_area
            self.unify_size()
            # Update the display to show the new image
            self.update_display()

        except Exception as e:
            logging.info(f"Error opening image: {e}")

    def update_display(self):
        """
        This function updates the display if the original image is available. 

        Parameters:0000000000000000000000000
            self: The current instance of the class.

        Returns:
            None
        """
        if self.original_img:
            self.repaint()

    def paintEvent(self, event):
        if not event.rect().intersects(self.rect()):
            return

        super().paintEvent(event)

        """
        Override the paintEvent method to draw the resized image on the widget.
        """

        if self.original_img:
            with QPainter(self) as painter_img:

                # adjust brightness, contrast, and resize the image
                self.adjust_brightness_contrast()
                resized_img = self.resized_img.resize(
                    (self.width(), self.height()))

                # Draw the image on the widget
                pixmap = QPixmap.fromImage(ImageQt.ImageQt(resized_img))
                painter_img.drawPixmap(0, 0, pixmap)


    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.

        Parameters:
            event (QMouseEvent): The mouse event triggered by the user.

        Returns:
            None
        """

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
            self.contrast = max(-255, min(255, self.contrast))

            # Update the image with adjusted brightness and contrast
            self.adjust_brightness_contrast()
            self.main_window.components_ports[self.viewport_image_ind].update_FT_components(
            )
            # Update the display\
            self.update_display()
        # Save the current mouse position for the next event
            self.last_x = event.x()
            self.last_y = event.y()
        else:
            event.accept()
            return
        print("image move")

    def mousePressEvent(self, event):
        """
        Save the initial mouse position when the mouse is pressed.

        Parameters:
            event (QMouseEvent): The mouse event object.

        Returns:
            None
        """
        # Save the initial mouse position when the mouse is pressed
        self.last_x = event.x()
        self.last_y = event.y()

    def unify_size(self):
        min_area = min(self.main_window.images_areas)
        if min_area < self.image_area:
            index_of_interest = np.where(self.main_window.image_area == min_area)[
                0][0]  # the first occurrence
            template_image = self.main_window.image_ports[index_of_interest].original_img
            self.resized_img = self.resized_img.resize(
                (template_image.width, template_image.height))
        elif min_area == self.image_area:
            self.main_window.generalize_image_size(self.viewport_image_ind)

    def adjust_brightness_contrast(self):
        """
        Adjusts the brightness and contrast of the image.
        """
        # Adjust brightness
        brightness_factor = (self.brightness + 255) / 255.0
        brightness_enhancer = ImageEnhance.Brightness(
            self.original_img.resize(self.resized_img.size))
        img_with_brightness_adjusted = brightness_enhancer.enhance(
            brightness_factor)

        # Adjust contrast
        contrast_factor = (self.contrast + 127) / 127.0
        contrast_enhancer = ImageEnhance.Contrast(img_with_brightness_adjusted)
        self.resized_img = contrast_enhancer.enhance(contrast_factor)

    def update_image_parameters(self, path):
        """
        Update the image parameters for the specified path.

        Args:
            path (str): The path of the image to update.

        Returns:
            None
        """
        # images indices by openeing order
        order = self.main_window.open_order

        # latest opened image index
        current = order[-1]

        # used for orderly set the ft components for each opened image
        selection = len(order)-1

        self.main_window.image_ports[current].set_image(path)

        # pick FT type for each image by default
        self.main_window.ui_image_combo_boxes[current].setCurrentIndex(
            selection)

        # set some attributes of the Image
        component = self.main_window.ui_image_combo_boxes[current].currentText(
        )
        self.main_window.components[str(current+1)] = component

        # update the mixing boxes and sliders
        self.main_window.ui_mixing_combo_boxes[selection].setCurrentIndex(
            current+1)

        self.main_window.ui_vertical_sliders[selection].setValue(100)

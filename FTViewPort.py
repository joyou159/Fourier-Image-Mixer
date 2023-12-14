from PyQt6.QtWidgets import (
    QWidget,
)
from PyQt6.QtGui import QPixmap, QImage,  QImageReader, QPainter
from PIL import Image, ImageQt
from PyQt6.QtGui import QPainter, QBrush, QPen
from PyQt6.QtCore import Qt, QRect, QPoint
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
        self.weight_slider = None
        self.original_img = None
        self.press_pos = None
        self.release_pos = None
        self.drawRect = False
        self.holdRect = False
        self.move_active = False
        self.current_rect = QRect()

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
            resized_img = self.original_img.resize((new_width, new_height))
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(resized_img))
            painter.drawPixmap(x, y, pixmap)

            painter.end()

        if self.holdRect:
            self.draw_rectangle()

        if self.drawRect:
            self.draw_rectangle()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_pos = event.position()
            print("Mouse Pressed at:", self.press_pos)
            self.current_rect.setTopLeft(self.press_pos.toPoint())
            self.current_rect.setBottomRight(self.press_pos.toPoint())
            self.drawRect = True
            self.update_display()

    def mouseMoveEvent(self, event):
        if self.drawRect:
            self.current_rect.setBottomRight(event.position().toPoint())
            self.update_display()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.release_pos = event.position()
            print("Mouse Released at:", self.release_pos)
            self.main_window.mixer.generalize_rectangle(
                self.viewport_FT_ind)
            self.drawRect = False
            self.update_display()

    def draw_rectangle(self):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.red, Qt.DiagCrossPattern))
        painter.drawRect(self.current_rect)
        painter.end()

    def draw_mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_pos = event.position()
            print("Mouse Pressed at:", self.press_pos)
            self.current_rect.setTopLeft(self.press_pos.toPoint())
            self.current_rect.setBottomRight(self.press_pos.toPoint())
            self.drawRect = True
            self.update_display()

    def draw_mouseMoveEvent(self, event):
        if self.drawRect:
            self.current_rect.setBottomRight(event.position().toPoint())
            self.update_display()

    def draw_mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.release_pos = event.position()
            print("Mouse Released at:", self.release_pos)
            self.main_window.mixer.generalize_rectangle(
                self.viewport_FT_ind)
            self.drawRect = False
            self.update_display()

    def move_mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_pos = event.position()
            print("Mouse Pressed at:", self.press_pos)
            # Check if the press position is inside the current rectangle
            if self.current_rect.contains(self.press_pos.toPoint()):
                self.move_active = True

    def move_mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.release_pos = event.position()
            print("Mouse Released at:", self.release_pos)
            self.move_active = False

    def move_mouseMoveEvent(self, event):
        if self.move_active:
            # Calculate the offset to move the rectangle
            offset = event.position() - self.press_pos

            # Calculate the new position of the top-left corner
            new_top_left = self.current_rect.topLeft() + offset.toPoint()

            # Ensure the new position stays within the original image boundaries
            if self.rect_within_widget(new_top_left):
                self.current_rect.translate(offset.toPoint())
                self.press_pos = event.position()
                self.update_display()

    def rect_within_widget(self, top_left):
        # Check if the rectangle defined by top_left stays within the widget boundaries
        return self.rect().contains(QRect(top_left, self.current_rect.size()))

    def deactivate_drawing_events(self):
        self.mousePressEvent = self.move_mousePressEvent
        self.mouseMoveEvent = self.move_mouseMoveEvent
        self.mouseReleaseEvent = self.move_mouseReleaseEvent

    def reactivate_drawing_events(self):
        self.mousePressEvent = self.draw_mousePressEvent
        self.mouseMoveEvent = self.draw_mouseMoveEvent
        self.mouseReleaseEvent = self.draw_mouseReleaseEvent

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

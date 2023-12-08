import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)
from PyQt6.QtGui import QPixmap, QImage,  QImageReader,QPainter
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
# Placeholder for FT-related functionalities
import numpy as np
from scipy.fft import fft2, ifft2, fftshift

class ImageViewport(QWidget):
    def __init__(self,main_window, parent=None):
        super().__init__(parent)
        self.image = None
        self.image_ind = None
        self.ft_components = {}  # Store calculated FT components
        self.main_window = main_window
        
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # connect the combo boxes value changed to a function that shows the corresponding FT type, and to the set_image_op
        for index, combo_box in enumerate(self.main_window.ui_image_combo_boxes):
            combo_box.currentIndexChanged.connect(
                self.handle_image_combo_boxes_selection)
            
    def handle_image_combo_boxes_selection(self):
        sender_combo_box = self.sender()
        combo_ind = self.main_window.ui_image_combo_boxes.index(sender_combo_box)
        target_combo = self.main_window.ui_image_combo_boxes[self.main_window.ui_image_combo_boxes.index(
            sender_combo_box)]
        # now we have the combo box , the new operation now we set the image(combo box index = image index) to the new chosen op
        operation = target_combo.currentText()
        self.main_window.operations[str(combo_ind)] = operation
        print(self.main_window.operations)
        
        
    def update_image_parameters(self,index,path):
        self.main_window.image_ports[index].set_image(path)
        self.main_window.image_ports[index].set_image_ind(index)
        #pick FT type for each image by default
        self.main_window.ui_image_combo_boxes[index].setCurrentIndex(index)
        #set some attributes of the Image
        operation = self.main_window.ui_image_combo_boxes[index].currentText()
        self.main_window.operations[str(index)] = operation
        #update the mixing boxes and sliders
        self.main_window.ui_mixing_combo_boxes[index].setCurrentIndex(index)
        self.main_window.ui_vertical_sliders[index].setValue(100)
        print(self.ft_components)

    def set_image(self, image_path):
        try:
            image = QImage(image_path)
            if image.format() != QImage.Format.Format_Grayscale8:
                image = image.convertToFormat(QImage.Format.Format_Grayscale8)

            self.image = image
            self.update_display()
        except Exception as e:
            print(f"Error opening image: {e}")
    
    #save the image index in case we need it, Optional
    def set_image_ind(self,index):
        self.image_ind = index

    def update_display(self):
            if self.image:
                # Update the widget by triggering a repaint
                self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.image:
            painter = QPainter(self)

            # Draw the images onto the widget using the minimum width and height
            x, y = 0, 0

            self.image = self.image.scaled(self.width(), self.height(),  Qt.AspectRatioMode.IgnoreAspectRatio)
            pixmap = QPixmap.fromImage(self.image)
            painter.drawPixmap(x, y, pixmap)

            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()
        
    # Placeholder for FT calculations
    def calculate_ft_components(self, image_path):
        if image_path is not None:
            # Compute the 2D Fourier Transform
            fft = np.fft.fft2(self.image)

            # Shift the zero-frequency component to the center
            fft_shifted = np.fft.fftshift(fft)

            # Compute the magnitude of the spectrum
            mag = np.abs(fft)

            # Compute the phase of the spectrum
            phase = np.angle(self.fft)

            # real ft components
            real = self.fft.real

            #imaginary ft components
            imaginary = self.fft.imag

            # Store the calculated components
            self.ft_components["FT Magnitude"] = QImage(
                mag.data, mag.shape[1], mag.shape[0], QImage.Format.Format_Grayscale8)

            self.ft_components["FT Phase"] = QImage(
                phase.data, phase.shape[1], phase.shape[0], QImage.Format.Format_Grayscale8)

            self.ft_components["FT Real"] = QImage(
                real.data, real.shape[1], real.shape[0], QImage.Format.Format_Grayscale8)

            self.ft_components["FT Imaginary"] = QImage(
                imaginary.data, imaginary.shape[1], imaginary.shape[0], QImage.Format.Format_Grayscale8)



    # def update_component(self, index):
    #     component = self.component_selector.currentText()
    #     if component == "Original":
    #         self.component_label.setPixmap(None)
    #     else:
    #         try:
    #             ft_image = self.get_ft_component(component)
    #             pixmap = QPixmap.fromImage(ft_image)
    #             self.component_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio))
    #         except KeyError:
    #             # Calculate and store the FT component
    #             self.calculate_ft_components()
    #             self.update_component(index)


    # def get_ft_component(self, component):
    #     return self.ft_components[component]



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.viewports = []

        # Create four viewports
        for _ in range(4):
            viewport = ImageViewport(self)
            self.viewports.append(viewport)

        layout = QHBoxLayout()
        for viewport in self.viewports:
            layout.addWidget(viewport)
        
        self.setLayout(layout)
        self.resize(800, 600)
        self.setWindowTitle("Image Viewer")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

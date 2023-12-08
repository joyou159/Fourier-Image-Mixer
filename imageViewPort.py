import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)
from PyQt6.QtGui import QPixmap, QImage
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
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

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

    def set_image(self, image_path):
        try:
            image = QImage(image_path)
            if image.format() == QImage.Format.Format_Grayscale8:
                self.set_image_from_qimage(image)
            else:
                self.set_image_from_qimage(image.convertToFormat(QImage.Format.Format_Grayscale8))
        except Exception as e:
            print(f"Error opening image: {e}")
    
    #save the image index in case we need it, Optional
    def set_image_ind(self,index):
        self.image_ind = index

    def set_image_from_qimage(self, image):
        self.image = image

        # If the widget has been shown, calculate and set the initial display
        if self.isVisible():
            self.update_display()
            
    def update_display(self):
        if self.image is not None:
            pixmap = QPixmap.fromImage(self.image)
            self.image_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio))

    # Placeholder for FT calculations
    def calculate_ft_components(self):
        if self.image is not None:
            image_array = np.array(self.image.convertToFormat(QImage.Format.Format_Grayscale8))

            # Calculate 2D Fourier Transform
            ft_image = fft2(image_array)

            # Shift zero frequency components to the center
            ft_image_shifted = fftshift(ft_image)

            # Calculate magnitude, phase, real, and imaginary components
            ft_magnitude = np.abs(ft_image_shifted)
            ft_phase = np.angle(ft_image_shifted)
            ft_real = np.real(ft_image_shifted)
            ft_imaginary = np.imag(ft_image_shifted)

            # Store the calculated components
            self.ft_components["FT Magnitude"] = QImage(
                ft_magnitude.data, ft_magnitude.shape[1], ft_magnitude.shape[0], QImage.Format.Format_Grayscale8)
            
            self.ft_components["FT Phase"] = QImage(
                ft_phase.data, ft_phase.shape[1], ft_phase.shape[0], QImage.Format.Format_Grayscale8)
            
            self.ft_components["FT Real"] = QImage(
                ft_real.data, ft_real.shape[1], ft_real.shape[0], QImage.Format.Format_Grayscale8)
            
            self.ft_components["FT Imaginary"] = QImage(
                ft_imaginary.data, ft_imaginary.shape[1], ft_imaginary.shape[0], QImage.Format.Format_Grayscale8)





    def update_component(self, index):
        component = self.component_selector.currentText()
        if component == "Original":
            self.component_label.setPixmap(None)
        else:
            try:
                ft_image = self.get_ft_component(component)
                pixmap = QPixmap.fromImage(ft_image)
                self.component_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio))
            except KeyError:
                # Calculate and store the FT component
                self.calculate_ft_components()
                self.update_component(index)


    def get_ft_component(self, component):
        return self.ft_components[component]



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

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
from scipy.fft import fft2, ifft2

class ImageViewport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.ft_components = {}  # Store calculated FT components

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.mousePressEvent = self.browse_image  # Connect the method to the mousePressEvent

        # self.component_label = QLabel()
        # self.component_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # self.component_selector = QComboBox()
        # self.component_selector.addItems(["Original", "FT Magnitude", "FT Phase", "FT Real", "FT Imaginary"])
        # self.component_selector.currentIndexChanged.connect(self.update_component)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        # layout.addWidget(self.component_selector)
        # layout.addWidget(self.component_label)
        self.setLayout(layout)


    def set_image(self, image_path):
        try:
            image = QImage(image_path)
            if image.format() == QImage.Format.Format_Grayscale8:
                self.set_image_from_qimage(image)
            else:
                self.set_image_from_qimage(image.convertToFormat(QImage.Format.Format_Grayscale8))
        except Exception as e:
            print(f"Error opening image: {e}")



    def update_display(self):
        pixmap = QPixmap.fromImage(self.image)
        self.image_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio))


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

    # Placeholder for FT calculations
    def calculate_ft_components(self):
        if self.image is not None:
            # Get individual pixel values as a NumPy array
            buffer = self.image.bits().asarray().data
            image_array = np.frombuffer(buffer, dtype=np.uint8)

            # Reshape the array to match the image dimensions
            image_array = image_array.reshape(self.image.height(), self.image.width())

            # Convert to float64 for calculations
            image_array = image_array.astype(np.float64)

            # Perform FFT calculations and convert back to NumPy uint8
            ft_magnitude = np.abs(fft2(image_array))
            ft_magnitude = ft_magnitude.astype(np.uint8)
            ft_phase = np.angle(fft2(image_array))
            ft_phase = ft_phase.astype(np.uint8)
            ft_real = np.real(fft2(image_array))
            ft_real = ft_real.astype(np.uint8)
            ft_imaginary = np.imag(fft2(image_array))
            ft_imaginary = ft_imaginary.astype(np.uint8)

            # Create QImages from the FT components
            self.ft_components["FT Magnitude"] = QImage(ft_magnitude, ft_magnitude.shape[1], ft_magnitude.shape[0], ft_magnitude.shape[1], QImage.Format.Format_Grayscale8)
            self.ft_components["FT Phase"] = QImage(ft_phase, ft_phase.shape[1], ft_phase.shape[0], ft_phase.shape[1], QImage.Format.Format_Grayscale8)
            self.ft_components["FT Real"] = QImage(ft_real, ft_real.shape[1], ft_real.shape[0], ft_real.shape[1], QImage.Format.Format_Grayscale8)
            self.ft_components["FT Imaginary"] = QImage(ft_imaginary, ft_imaginary.shape[1], ft_imaginary.shape[0], ft_imaginary.shape[1], QImage.Format.Format_Grayscale8)


    def browse_image(self, event):
        file_filter = "Raw Data (*.png *.jpg *.jpeg)"
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Signal File', './', filter=file_filter)
        if image_path:
            self.set_image(image_path)
    
    
    def set_image_from_qimage(self, image):
        self.image = image
        self.update_display()



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.viewports = []

        # Create four viewports
        for _ in range(4):
            viewport = ImageViewport()
            self.viewports.append(viewport)

        layout = QHBoxLayout()
        for viewport in self.viewports:
            layout.addWidget(viewport)
        
        self.setLayout(layout)
        self.resize(800, 600)
        self.setWindowTitle("Image Viewer")

        # Adjust the sizes of images in all viewports based on the smallest size
        self.adjust_image_sizes()

    def adjust_image_sizes(self):
        # Check if there are images in the viewports
        if any(viewport.image is not None for viewport in self.viewports):
            # Find the smallest width and height among all images
            min_width = min(viewport.image.width() for viewport in self.viewports if viewport.image is not None)
            min_height = min(viewport.image.height() for viewport in self.viewports if viewport.image is not None)

            # Resize images in all viewports to the smallest size
            for viewport in self.viewports:
                if viewport.image is not None:
                    new_image = viewport.image.scaled(min_width, min_height, Qt.AspectRatioMode.KeepAspectRatio)
                    viewport.set_image_from_qimage(new_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

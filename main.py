from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout,  QMessageBox,  QSlider
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6 import QtWidgets, uic
import numpy as np
import pandas as pd
import sys
import pyqtgraph as pg
import qdarkstyle
import os
import sounddevice as sd
from PyQt6.QtCore import Qt, QRect, QPoint
import sys
import logging
from imageViewPort import ImageViewport
from FTViewPort import FTViewPort
from mixer import ImageMixer
from ThreadingClass import WorkerSignals, WorkerThread

# Configure logging to capture all log levels
logging.basicConfig(filemode="a", filename="our_log.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s")

# logging.info("This is an info message.")
# logging.warning("This is a warning message.")
# logging.error("This is an error message.")
# logging.critical("This is a critical message.")


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        # Load the UI Page
        self.ui = uic.loadUi('Mainwindow.ui', self)
        self.setWindowTitle("Image Mixer")
        self.setWindowIcon(QIcon("icons/mixer.png"))
        self.image_ports = []
        self.components_ports = []
        self.open_order = []
        self.min_width = None
        self.min_height = None
        self.components = {"1": '', "2": '', '3': '', '4': ''}
        self.ui.output1_port.resize(
            self.ui.original1.width(), self.ui.original1.height())
        # mixer and its connection line
        self.mixer = ImageMixer(self)
        self.ui.mixxer.clicked.connect(self.start_thread)
        self.ui.radioButton_In.setChecked(True)
        self.ui.radioButton_In.toggled.connect(
            self.mixer.handle_radio_button_toggled)
        self.ui.radioButton_Out.toggled.connect(
            self.mixer.handle_radio_button_toggled)
        self.ui.Deselect.clicked.connect(self.deselect)

        self.load_ui_elements()

        self.showFullScreen()
        self.ui.keyPressEvent = self.keyPressEvent

        self.worker_signals = WorkerSignals()
        self.worker_thread = None

        

    def deselect(self):
        for comp in self.components_ports:
            comp.current_rect = QRect()
            comp.reactivate_drawing_events()
            comp.update_display()

    def start_thread(self):
        if self.worker_thread and self.worker_thread.is_alive():
            print('Terminating the running thread...')
            self.worker_thread.cancel()
            print('Thread terminated.')

        print('Starting a new thread...')
        self.worker_signals.canceled.clear()
        self.worker_thread = WorkerThread(5, self.worker_signals, self)
        self.worker_thread.start()
        self.mixer.mix_images()

    def keyPressEvent(self, event):
        # Handle key events, for example, pressing ESC to exit full screen
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()  # Show the window in normal size
        else:
            super().keyPressEvent(event)

        self.showFullScreen()
        self.ui.keyPressEvent = self.keyPressEvent

    def keyPressEvent(self, event):
        # Handle key events, for example, pressing ESC to exit full screen
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()  # Show the window in normal size
        else:
            super().keyPressEvent(event)

    def load_ui_elements(self):
        """
        Load UI elements.

        This function is responsible for loading the UI elements of the application. It initializes and configures various UI components 
        such as view ports, combo boxes, sliders, and connects them to the appropriate event handlers.

        """
        # List of original UI view ports
        ui_view_ports = [self.ui.original1, self.ui.original2,
                         self.ui.original3, self.ui.original4]

        self.ui_view_ports_comp = [
            self.ui.component_image1, self.ui.component_image2,
            self.ui.component_image3, self.ui.component_image4]

        # List of combo boxes for UI
        self.ui_image_combo_boxes = [
            self.ui.combo1, self.ui.combo2,
            self.ui.combo3, self.ui.combo4]

        # List of combo boxes for mixing UI
        self.ui_mixing_combo_boxes = [
            self.ui.combo11, self.ui.combo12,
            self.ui.combo13, self.ui.combo14]

        self.ui_vertical_sliders = [
            self.ui.Slider_weight1, self.ui.Slider_weight2,
            self.ui.Slider_weight3, self.ui.Slider_weight4]

        # Create image viewports and bind browse_image function to the event
        self.image_ports.extend([
            self.create_image_viewport(
                ui_view_ports[i], lambda event, index=i: self.browse_image(event, index))
            for i in range(4)
        ])

        self.components_ports.extend([
            self.create_FT_viewport(
                self.ui_view_ports_comp[i])
            for i in range(4)
        ])

        # Add items to combo boxes for mixing UI
        for combo_box in self.ui_mixing_combo_boxes:
            combo_box.addItems(['None']+[f'image{i+1}' for i in range(4)])

        for i, combo_box in enumerate(self.ui_image_combo_boxes):
            self.components_ports[i].combo_box = combo_box
            self.components_ports[i].weight_slider = self.ui_vertical_sliders[i]
            self.ui_vertical_sliders[i].setMinimum(1)
            self.ui_vertical_sliders[i].setMaximum(100)
            self.ui_vertical_sliders[i].valueChanged.connect(
                self.mixer.handle_weight_sliders)
            combo_box.addItems(
                ["FT Magnitude", "FT Phase", "FT Real", "FT Imaginary"])
            combo_box.setCurrentIndex(0)
            combo_box.currentIndexChanged.connect(
                self.components_ports[i].handle_image_combo_boxes_selection)

    def browse_image(self, event, index: int):
        """
        Browse for an image file and set it for the ImageViewport at the specified index.

        Args:
            event: The event that triggered the image browsing.
            index: The index of the ImageViewport to set the image for.
        """
        file_filter = "Raw Data (*.png *.jpg *.jpeg *.jfif)"
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Signal File', './', filter=file_filter)

        if image_path and 0 <= index < len(self.image_ports):
            image_port = self.image_ports[index]
            if index not in self.open_order:
                self.open_order.append(index)
            else:
                # swap ,and make the one we open the last one
                self.open_order[-1], self.open_order[self.open_order.index(
                    index)] = self.open_order[self.open_order.index(index)], self.open_order[-1]

            self.image_processing(index, image_port, image_path)

    def image_processing(self, index, image_port, image_path):
        image_port.viewport_image_ind = index
        self.components_ports[index].viewport_FT_ind = index
        image_port.update_image_parameters(image_path)
        self.components_ports[index].update_FT_components()
        # print(
        #     f"the size of the image before resizing{np.array(image_port.original_img).shape}")
        # print(
        #     f"the size of the image after resizing{np.array( image_port.resized_img).shape}")
        # self.resize_image()

    def resize_image(self):
        dimension_lst = []

        for viewport in self.image_ports:

            dimensions = np.array(viewport.resized_img).shape
            if dimensions:  # Check if the shape tuple is not empty
                dimension_lst.append(dimensions)

        if dimension_lst:
            min_width = min(dim[1] for dim in dimension_lst)
            min_height = min(dim[0] for dim in dimension_lst)

            for viewport in self.image_ports:
                viewport.resize_image(min_width, min_height)

    def create_image_viewport(self, parent, mouse_double_click_event_handler):
        """
        Creates an image viewport and adds it to the specified parent widget.

        Args:
            parent: The parent widget to which the image viewport will be added.
            mouse_double_click_event_handler: The event handler function to be called when a mouse double-click event occurs on the image viewport.

        Returns:
            The created image viewport.

        """
        image_port = ImageViewport(self)
        image_layout = QVBoxLayout(parent)
        image_layout.addWidget(image_port)
        image_port.mouseDoubleClickEvent = mouse_double_click_event_handler
        return image_port

    def add_items_to_combo_boxes(self, combo_boxes, items):
        """
        Adds the specified items to the given combo boxes.

        Args:
            combo_boxes (list): A list of combo boxes to which the items will be added.
            items (list): A list of items to be added to the combo boxes.

        Returns:
            None
        """
        for combo_box in combo_boxes:
            combo_box.addItems(items)

    def create_FT_viewport(self, parent):
        """
        Creates an FT viewport and adds it to the specified parent widget.

        Args:
            parent: The parent widget to which the image viewport will be added.
            mouse_double_click_event_handler: The event handler function to be called when a mouse double-click event occurs on the image viewport.

        Returns:
            The created FT viewport.

        """
        FT_port = FTViewPort(self)
        FT_layout = QVBoxLayout(parent)
        FT_layout.addWidget(FT_port)
        return FT_port


def main():

    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

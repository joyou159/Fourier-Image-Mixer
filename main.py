from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout,  QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6 import QtWidgets, uic
import numpy as np
import sys
import qdarkstyle
from PyQt6.QtCore import Qt, QRect
import sys
import logging
from imageViewPort import ImageViewport
from FTViewPort import FTViewPort
from OutViewPort import OutViewPort
from mixer import ImageMixer
from ThreadingClass import WorkerSignals, WorkerThread


# Configure logging to capture all log levels
logging.basicConfig(filemode="a", filename="our_log.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)

# logging.info("This is an info message.")
# logging.warning("This is a warning message.")
# logging.error("This is an error message.")
# logging.critical("This is a critical message.")


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface by loading the UI page, setting the window title and icon,
        initializing various attributes, connecting signals to slots, loading UI elements, and 
        setting the window to full screen.

        Parameters:
            None

        Returns:
            None
        """
        # Load the UI Page
        self.ui = uic.loadUi('Mainwindow.ui', self)
        self.setWindowTitle("Image Mixer")
        self.setWindowIcon(QIcon("icons/mixer.png"))
        self.image_ports = []
        self.components_ports = []
        self.images_areas = np.repeat(np.inf, 4)  # initialized
        self.out_ports = []
        self.open_order = []
        self.min_width = None
        self.min_height = None
        self.components = {"1": '', "2": '', '3': '', '4': ''}
        self.ui.output1_port.resize(
            self.ui.original1.width(), self.ui.original1.height())
        # mixer and its connection line
        self.mixer = ImageMixer(self)
        self.ui.mixxer.clicked.connect(self.start_thread)

        self.ui.Deselect.clicked.connect(self.deselect)

        self.load_ui_elements()

        self.showFullScreen()
        self.ui.keyPressEvent = self.keyPressEvent

        self.worker_signals = WorkerSignals()
        self.worker_thread = None

    def show_error_message(self, message):
        """
        Displays an error message to the user.

        Args:
            message (str): The error message to be displayed.

        Returns:
            None
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()

    def deselect(self):
        """
        Deselects all components and resets their properties.

        This function does not take any parameters and does not return anything.
        """
        for comp in self.components_ports:
            self.holdRect = False
            self.drawRect = True
            comp.press_pos = None
            comp.release_pos = None
            self.move_active = False
            comp.current_rect = QRect()
            comp.reactivate_drawing_events()
            comp.update_display()

    def start_thread(self):
        """
        Start a new thread for processing.

        If there is a running thread, terminate it before starting a new one.
        """
        # Check if the pair of images is valid
        if self.mixer.check_pair_validity():
            if not any(np.any(port.press_pos for port in self.components_ports)):
                logging.error("the user didn't select area from the images ")
                return

            if len(self.open_order) % 2 == 0:
                if self.worker_thread and self.worker_thread.is_alive():
                    logging.info('Terminating the running thread...')
                    self.worker_thread.cancel()
                    logging.info('Thread terminated.')

                logging.info('Starting a new thread...')
                self.worker_signals.canceled.clear()
                self.worker_thread = WorkerThread(
                    5, self.worker_signals, self)
                self.worker_thread.start()
            else:
                logging.error(msg=f"The user mix odd number of images {
                    len(self.open_order)}")
                return

    def map_value(self, value, lower_range, upper_range, lower_range_new, upper_range_new):
        """
        Maps a given value from one range to another linearly.

        Parameters:
        - value (float): The input value to be mapped.
        - lower_range (float): The lower bound of the input range.
        - upper_range (float): The upper bound of the input range.
        - lower_range_new (float): The lower bound of the target range.
        - upper_range_new (float): The upper bound of the target range.

        Returns:
        float: The mapped value in the target range.
        """

        mapped_value = ((value - lower_range) * (upper_range_new - lower_range_new) /
                        (upper_range - lower_range)) + lower_range_new
        return mapped_value

    def generalize_image_size(self, template_image_ind):
        """
        Generalizes the size of all images in the collection based on a template image.

        Parameters:
        - template_image_ind (int): The index of the template image in the collection.

        Description:
        Resizes all images in the collection to match the dimensions of the template image.
        If an image at the given index is the template itself or if it is None, it is skipped.

        This method assumes that the images are represented by objects with 'resized_img'
        attribute that can be resized using the 'resize' method, and updates the display
        and Fourier Transform (FT) components accordingly.

        Note: Make sure that the 'resized_img' attribute is not None for images that need
        to be resized.

        Returns:
        None
        """
        for i, image in enumerate(self.image_ports):
            if i != template_image_ind and image.original_img is not None:
                template_image = self.image_ports[template_image_ind].resized_img
                image.resized_img = image.resized_img.resize(
                    (template_image.width, template_image.height))
                image.update_display()
                self.components_ports[i].update_FT_components()

    def keyPressEvent(self, event):
        """
        Handle key events, for example, pressing ESC to exit full screen.

        Parameters:
            event (QKeyEvent): The key event object.

        Returns:
            None
        """
        # Handle key events, for example, pressing ESC to exit full screen
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()  # Show the window in normal size
        else:
            super().keyPressEvent(event)

    def load_ui_elements(self):
        """
        Load UI elements.

        Initializes and configures various UI components such as viewports, combo boxes, sliders, and connects them to appropriate event handlers.

        """
        # Define lists of original UI view ports, output ports, component view ports, image combo boxes, mixing combo boxes, and vertical sliders
        ui_view_ports = [self.ui.original1, self.ui.original2,
                         self.ui.original3, self.ui.original4]
        self.ui_out_ports = [self.ui.output1_port, self.ui.output2_port]
        self.ui_view_ports_comp = [
            self.ui.component_image1, self.ui.component_image2, self.ui.component_image3, self.ui.component_image4]
        self.ui_image_combo_boxes = [
            self.ui.combo1, self.ui.combo2, self.ui.combo3, self.ui.combo4]
        self.ui_mixing_combo_boxes = [
            self.ui.combo11, self.ui.combo12, self.ui.combo13, self.ui.combo14]
        self.ui_vertical_sliders = [
            self.ui.Slider_weight1, self.ui.Slider_weight2, self.ui.Slider_weight3, self.ui.Slider_weight4]

        # Create image viewports and bind browse_image function to the event
        self.image_ports.extend([
            self.create_image_viewport(ui_view_ports[i], lambda event, index=i: self.browse_image(event, index)) for i in range(4)])

        # Create FT viewports
        self.components_ports.extend([self.create_FT_viewport(
            self.ui_view_ports_comp[i]) for i in range(4)])

        # Create output viewports
        self.out_ports.extend([self.create_output_viewport(
            self.ui_out_ports[i]) for i in range(2)])

        # Add items to combo boxes for mixing UI
        for combo_box in self.ui_mixing_combo_boxes:
            combo_box.addItems(['None'] + [f'image{i+1}' for i in range(4)])

        # Loop through each combo box and associated components_ports
        for i, combo_box in enumerate(self.ui_image_combo_boxes):
            # Set the combo box and weight slider for the corresponding components_port
            self.components_ports[i].combo_box = combo_box
            self.components_ports[i].weight_slider = self.ui_vertical_sliders[i]

            # Set the minimum and maximum values for the weight slider
            self.ui_vertical_sliders[i].setMinimum(1)
            self.ui_vertical_sliders[i].setMaximum(100)

            # Connect the valueChanged signal of the weight slider to the handle_weight_sliders method of the mixer
            self.ui_vertical_sliders[i].valueChanged.connect(
                self.mixer.handle_weight_sliders)

            # Add items to the combo box and set the current index to 0
            combo_box.addItems(
                ["FT Magnitude", "FT Phase", "FT Real", "FT Imaginary"])
            combo_box.setCurrentIndex(0)

            # Connect the currentIndexChanged signal of the combo box to the handle_image_combo_boxes_selection method of the components_port
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
        """
        Process the image with the given index and update the image parameters.

        Parameters:
        - index: int - The index of the image to process.
        - image_port: ImagePort - The image port object.
        - image_path: str - The path to the image file.

        Returns:
        - None
        """
        # Update the viewport image index
        image_port.viewport_image_ind = index

        # Update the FT index of the component port
        self.components_ports[index].viewport_FT_ind = index

        # Update the image parameters
        image_port.update_image_parameters(image_path)

        # store the loading initial size of the component viewport
        self.components_ports[index].pre_widget_dim = (
            self.components_ports[index].width(), self.components_ports[index].height())

        # Update the FT components of the component port
        self.components_ports[index].update_FT_components()

        # Print the size of the image before resizing
        logging.info(f"The size of the image before resizing: {
            np.array(image_port.original_img).shape}")

        # Print the size of the image after resizing
        logging.info(f"The size of the image after resizing: {
            np.array(image_port.resized_img).shape}")

    def create_viewport(self, parent, viewport_class, mouse_double_click_event_handler=None):
        """
        Creates a viewport of the specified class and adds it to the specified parent widget.

        Args:
            parent: The parent widget to which the viewport will be added.
            viewport_class: The class of the viewport to be created.
            mouse_double_click_event_handler: The event handler function to be called when a mouse double-click event occurs (optional).

        Returns:
            The created viewport.

        """
        new_port = viewport_class(self)
        layout = QVBoxLayout(parent)
        layout.addWidget(new_port)

        if mouse_double_click_event_handler:
            new_port.mouseDoubleClickEvent = mouse_double_click_event_handler

        return new_port

    def create_image_viewport(self, parent, mouse_double_click_event_handler):
        return self.create_viewport(parent, ImageViewport, mouse_double_click_event_handler)

    def create_FT_viewport(self, parent):
        return self.create_viewport(parent, FTViewPort)

    def create_output_viewport(self, parent):
        return self.create_viewport(parent, OutViewPort)

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


def main():
    logging.info(
        "----------------------the user open the app-------------------------------------")
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

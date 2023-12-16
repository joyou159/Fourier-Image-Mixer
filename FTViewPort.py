from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap, QPainter
from PIL import Image, ImageQt
from PyQt6.QtGui import QPainter, QBrush, QPen
from PyQt6.QtCore import Qt, QRect
import numpy as np
from scipy.fft import fft2, fftshift


class FTViewPort(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.viewport_FT_ind = None  # the index of the components view port
        self.combo_box = None  # as widget object, Used for selecting different FT components and handling combo box events.
        self.main_window = main_window # Used to access and interact with other components of the main application.
        self.curr_component_name = None # Used to track the current FT component selected in the combo box.
        self.image_data = None # Used for computing FT components
        self.component_data = None # Used to access the pixel data of the currently selected FT component.

        self.ft_components_images = {} # Used to cache FT component images for efficient display
        self.ft_components = {} # Used to cache FT component data for further processing.
        self.weight_slider = None # Used for adjusting weights during the mixing process.
        self.original_img = None # Used for displaying the original image and updating the display.
        self.resized_img = None # Used for displaying the image with adjusted dimensions.
        self.press_pos = None #  Used for drawing rectangles and determining their dimensions.
        self.release_pos = None 
        self.drawRect = False # Used to control the drawing state.
        self.holdRect = False # Used to control the state of holding a drawn rectangle.
        self.move_active = False # Used to control the state of moving a drawn rectangle.
        self.current_rect = QRect() # Stores the coordinates and dimensions of the rectangle.

        
    def set_image(self):
        """
        Set the image for the current component.

        Raises:
            Exception: If there is an error opening the image.
        """
        try:
            # Get the image for the current component
            image = self.ft_components_images[self.curr_component_name]

            # Get the data for the current component
            self.component_data = self.ft_components[self.curr_component_name]

            # Set the original image
            self.original_img = image

            # Update the display
            self.update_display()

        except Exception as opening_Error:
            print(f"Error opening image: {opening_Error}")


    def update_display(self):
        """
        This method is responsible for updating the display based on the current state of the object. 
        It checks if the original image is set and if so, it repaints the display.

        """
        if self.original_img:
            self.repaint()


    def paintEvent(self, event):
        """
        Override the paint event of the widget.

        Args:
            event (QPaintEvent): The paint event.

        Returns:
            None
        """
        super().paintEvent(event)

        # Check if there is an original image
        if self.original_img:
            painter = QPainter(self)

            # Calculate the new size while maintaining the aspect ratio
            aspect_ratio = self.original_img.width / self.original_img.height
            new_width = self.width()
            new_height = int(new_width / aspect_ratio)

            # Adjust the new size if it exceeds the height of the widget
            if new_height > self.height():
                new_height = self.height()
                new_width = int(new_height * aspect_ratio)

            # Calculate the position (x, y) to center the image
            x = (self.width() - new_width) // 2
            y = (self.height() - new_height) // 2

            # Resize the original image to match the size of the widget
            self.resized_img = self.original_img.resize((self.width(), self.height()))

            # Convert the resized image to QPixmap
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(self.resized_img))

            # Draw the pixmap on the widget
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

        # Check if either holdRect or drawRect is True
        if self.holdRect or self.drawRect:
            self.draw_rectangle()


    def update_FT_components(self):
        """

        Updates the image data by converting it to a numpy array. Then, calculates the FT components
        based on the updated image data. Finally, handles the selection of image combo boxes.
        """
        self.image_data = np.array(self.main_window.image_ports[self.viewport_FT_ind].resized_img)

        self.calculate_ft_components()
        self.handle_image_combo_boxes_selection()


    def handle_image_combo_boxes_selection(self):
        """
        This function is responsible for handling the selection of image combo boxes. 
        It checks if the ft_components_images list is not empty, and if so, it performs the following actions:
        - Retrieves the currently selected component name from the combo_box.
        - Updates the main_window components dictionary with the current component name, using the viewport_FT_ind + 1 as the key.
        - Calls the set_image() function to update the image.

        """
        if self.ft_components_images:
            self.curr_component_name = self.combo_box.currentText() # note a None object why?
            self.main_window.components[str(self.viewport_FT_ind + 1)] = self.curr_component_name
            self.set_image()


    def mousePressEvent(self, event):
        """
        Handle the mouse press event.

        Args:
            event (QMouseEvent): The mouse press event object.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Set the press position
            self.press_pos = event.position()

            # Print the press position
            print("Mouse Pressed at:", self.press_pos)

            # Set the top left and bottom right points of the current rectangle
            self.current_rect.setTopLeft(self.press_pos.toPoint())
            self.current_rect.setBottomRight(self.press_pos.toPoint())

            # Set the flag to draw the rectangle
            self.drawRect = True

            # Update the display
            self.update_display()

    def mouseMoveEvent(self, event):
        """
        Handle the mouse move event.

        Args:
            event (QMouseEvent): The mouse move event.

        Returns:
            None
        """
        if self.drawRect:
            self.current_rect.setBottomRight(event.position().toPoint())
            self.update_display()

    def mouseReleaseEvent(self, event):
        """
        Handle the mouse release event.

        Args:
            event: The mouse release event object.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.release_pos = event.position()  # Store the position where the mouse was released
            print("Mouse Released at:", self.release_pos)  # Print the position to the console
            self.main_window.mixer.generalize_rectangle(self.viewport_FT_ind)  # Generalize the rectangle in the mixer
            self.drawRect = False  # Set the `drawRect` flag to False
            self.update_display()  # Update the display

    def draw_rectangle(self):
        """
        Draws a rectangle on the widget.

        This function creates a QPainter object to draw a red rectangle on the widget. It sets the pen color to red with a width of 2 pixels and a solid line style. The brush color is also set to red with a diagonal cross pattern. The rectangle to be drawn is specified by the `current_rect` attribute of the widget.

        Parameters:
            self: The widget object on which to draw the rectangle.

        Returns:
            None
        """
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.red, Qt.DiagCrossPattern))
        painter.drawRect(self.current_rect)
        painter.end()


    def draw_mousePressEvent(self, event):
        """
        Handles the mouse press event.

        Parameters:
            event (QMouseEvent): The mouse press event.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_pos = event.position()
            print("Mouse Pressed at:", self.press_pos)
            self.current_rect.setTopLeft(self.press_pos.toPoint())
            self.current_rect.setBottomRight(self.press_pos.toPoint())
            self.drawRect = True
            self.update_display()

    def draw_mouseMoveEvent(self, event):
        """
        Handle the mouse move event.

        Args:
            event: The event object representing the mouse move event.

        Returns:
            None.
        """
        if self.drawRect:
            self.current_rect.setBottomRight(event.position().toPoint())
            self.update_display()

    def draw_mouseReleaseEvent(self, event):
        """
        Handle the mouse release event.

        Parameters:
            event: The mouse release event.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.release_pos = event.position()
            print("Mouse Released at:", self.release_pos)
            self.main_window.mixer.generalize_rectangle(
                self.viewport_FT_ind)
            self.drawRect = False
            self.update_display()

    def move_mousePressEvent(self, event):
        """
        Handle the mouse press event.

        Args:
            event (QMouseEvent): The mouse press event.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_pos = event.position()
            print("Mouse Pressed at:", self.press_pos)
            # Check if the press position is inside the current rectangle
            if self.current_rect.contains(self.press_pos.toPoint()):
                self.move_active = True

    def move_mouseReleaseEvent(self, event):
        """
        Handle the mouse release event.

        Args:
            event (QtGui.QMouseEvent): The mouse release event.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.release_pos = event.position()
            print("Mouse Released at:", self.release_pos)
            self.move_active = False

    def move_mouseMoveEvent(self, event):
        """
        Handles the mouse move event for the `move_active` state.

        Parameters:
            event (QMouseEvent): The mouse move event.

        Returns:
            None
        """
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
        """
        Check if the rectangle defined by top_left stays within the widget boundaries.

        Parameters:
            top_left (QPoint): The top left corner of the rectangle.

        Returns:
            bool: True if the rectangle stays within the widget boundaries, False otherwise.
        """
        # Check if the rectangle defined by top_left stays within the widget boundaries
        return self.rect().contains(QRect(top_left, self.current_rect.size()))


    def deactivate_drawing_events(self):
        """
        Deactivates the drawing events for the current object.

        This function overrides the mousePressEvent, mouseMoveEvent, and mouseReleaseEvent
        methods of the current object to prevent any drawing events from being triggered.

        """
        self.mousePressEvent = self.move_mousePressEvent
        self.mouseMoveEvent = self.move_mouseMoveEvent
        self.mouseReleaseEvent = self.move_mouseReleaseEvent

    def reactivate_drawing_events(self):
        """
        Reactivates the drawing events for the current object.

        """
        self.mousePressEvent = self.draw_mousePressEvent
        self.mouseMoveEvent = self.draw_mouseMoveEvent
        self.mouseReleaseEvent = self.draw_mouseReleaseEvent


    def calculate_ft_components(self):
        """
        Calculate the components of the Fourier Transform for the image data.
    
        """
        # Compute the 2D Fourier Transform
        fft = fft2(self.image_data)

        # Shift the zero-frequency component to the center
        fft_shifted = fftshift(fft)

        # Compute the magnitude of the spectrum
        mag = np.abs(fft_shifted)
        mag_log = 10 * np.log(mag + 1e-10).astype(np.uint8)

        # Compute the phase of the spectrum
        phase = np.angle(fft_shifted).astype(np.uint8)

        # Compute the real and imaginary components
        real = 10 * np.log(np.abs(np.real(fft_shifted)) + 1e-10).astype(np.uint8)
        imaginary = fft_shifted.imag.astype(np.uint8)

        # Store the results as images
        self.ft_components_images['FT Magnitude'] = Image.fromarray(mag_log, mode="L")
        self.ft_components_images['FT Phase'] = Image.fromarray(phase, mode='L')
        self.ft_components_images["FT Real"] = Image.fromarray(real, mode='L')
        self.ft_components_images["FT Imaginary"] = Image.fromarray(imaginary, mode='L')

        # Store the numerical components
        self.ft_components['FT Magnitude'] = mag
        self.ft_components['FT Phase'] = np.angle(fft_shifted)
        self.ft_components['FT Real'] = fft_shifted.real
        self.ft_components['FT Imaginary'] = fft_shifted.imag


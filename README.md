# Image Mixer Project
![Demo of UI](https://github.com/MohamedMandour10/Fourier-Image-Mixer/assets/115044826/6a6c859e-4838-45cb-bd8e-0db4bcea9e5f)

A desktop application designed for composing images by combining Fourier Transform components, `Mag and Phase` or `Real and Imaginary` depending on the mode, from other images. It provides a user-friendly interface to load images, select rectangular regions from them, and adjust the weight of each region using sliders, ultimately mixing these components in threads and applying inverse Fourier Transform to get the output image.
### 1. Graphical User Interface (GUI)

The application boasts an intuitive GUI with the following components:

- **Image Viewports:** Display images loaded into the application.
- **FT Viewports:** Visualize the selected Fourier Transform components of the loaded images.
- **Output Viewports:** Display the mixed and processed images.

### 2. Image Loading and Processing

#### Load Images

Users can load images (in formats such as PNG, JPG, JPEG, and JFIF) into the application. The "Browse" option in each Image Viewport allows users to select images for processing.

#### Image Processing

The application processes the loaded images to generate Fourier Transform components. Users can visualize these components in the FT Viewports, serving as the basis for the mixing operations.

### 3. Image Mixing

#### Mixing Options

User can choose the mode of mixing, whether it is `Mag and Phase` or `Real and Imaginary`. This modes will ensure that the mixing process is valid under any circumstances.

#### Mixing Parameters

Adjustable sliders enable users to fine-tune mixing parameters, including weights assigned to each selected FT component. This provides control over the contribution of each component to the final mixed image.

### 4. Interactive User Interactions

#### Component Selection

Users can interactively select rectangular region from the FT component of each image for mixing, where this region of interest can be the inner or outer with respect to the rectangular region depending on the user's choice. The application provides functionality to extract and manipulate specific regions, enhancing user control over the mixing process.

#### Brightness and Contrast Adjustment

Users can adjust the brightness and contrast of images using mouse interactions. This feature adds another control manner over the selected regions besides the weight sliders.

### 5. Multithreaded Mixing

The application employs multithreading to efficiently mix the selected regions, enhancing performance and responsiveness.


## How to Use

1. **Run the Application:**
   - Execute the application script to launch the GUI.

2. **Load Images:**
   - Double click on any input Image Viewport or use the "Browse" option to load images.

3. **Adjust Parameters:**
   - Interactively adjust brightness and contrast for better visualization via right-click on the mouse and drag horizontally (Brightness) and vertically (Contrast).

4. **Choose Mixing Mode:**
   - Choose between `Mag and phase` or `Real and Imaginary` modes.

5. **Choose Components of Interest:**
   - Choose the component of interest for each image from the combo box of each FT Viewport.
6. **Choose Mode of extraction:**
   - Choose whether you will be interested in the inner or outer part of the rectangular region.
   
7. **Select Regions of Interest (Optional):**
   - Choose the rectangular region of interest within each FT Viewport, simply initiate the process by left-clicking on the FT viewport. Continue by holding down the left mouse button and dragging the cursor to define the desired rectangular region. The size of the  rectangle will be generalized for the rest FT components, with capability of moving such rectangle around within each FT Viewport.
  
8. **Mix Images:**
   - Click the "Mix" button to initiate the image mixing process.

9. **View Output:**
   - The mixed image is displayed in the chosen output      Viewport.

## Dependencies

The project utilizes the following libraries:

- **PyQt6:** For GUI development.
- **NumPy:** For numerical operations.
- **PIL (Pillow):** For image processing.
- **scipy:** For FFT (Fast Fourier Transform) operations.

## Logging

The application logs events and errors to a file named `our_log.log`. Refer to this log file for detailed information on application activities.

For additional details on the code structure and implementation, refer to the source code in the provided Python script.

Feel free to explore and experiment with the Image Mixer project!

## Demo


https://github.com/MohamedMandour10/Fourier-Image-Mixer/assets/115044826/8c4150bb-c027-46da-8f69-8a2edba914d1


## How to Run

1. Install the required dependencies using 
```bash
pip install -r requirements.txt
```
2. Run the application using 
```bash
python main.py
```

## Contributors <a name = "Contributors"></a>
<table>
  <tr>
    <td align="center">
    <a href="https://github.com/MohamedMandour10" target="_black">
    <img src="https://avatars.githubusercontent.com/u/115044826?v=4" width="150px;" alt="Mohamed Elsayed Eid"/>
    <br />
    <sub><b>Mohamed Elsayed Eid</b></sub></a>
    </td>
    <td align="center">
    <a href="https://github.com/mohamedmosilhy" target="_black">
    <img src="https://avatars.githubusercontent.com/u/93820559?v=4" width="150px;" alt="mohamed mosilhy"/>
    <br />
    <sub><b>Mohamed Mosilhy</b></sub></a>
    </td>
    <td align="center">
    <a href="https://github.com/MahmoudMagdy404" target="_black">
    <img src="https://avatars.githubusercontent.com/u/83336074?v=4" width="150px;" alt="Mahmoud Magdy"/>
    <br />
    <sub><b>Mahmoud Magdy</b></sub></a>
    </td>
    <td align="center">
    <a href="https://github.com/joyou159" target="_black">
    <img src="https://avatars.githubusercontent.com/u/85418161?v=4" width="150px;" alt="Youssef Ahmed"/>
    <br />
    <sub><b>Youssef Ahmed</b></sub></a>
    </td>
      </tr>

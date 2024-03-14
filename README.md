# Image Mixer Project
![Demo of UI](https://github.com/MohamedMandour10/Fourier-Image-Mixer/assets/115044826/6a6c859e-4838-45cb-bd8e-0db4bcea9e5f)

The Image Mixer project is a graphical application designed for mixing and processing images using Fourier Transform (FT) components. It provides a user-friendly interface to load images, perform Fourier Transform operations, and create composite images by combining selected FT components.

## Features

### 1. Graphical User Interface (GUI)

The project offers an intuitive GUI with the following components:

- **Image Viewports:** Display images loaded into the application.
- **FT Viewports:** Display Fourier Transform components of the loaded images.
- **Output Viewports:** Display the mixed and processed images.

### 2. Image Loading and Processing

#### Load Images

Users can load images (in formats such as PNG, JPG, JPEG, and JFIF) into the application. The "Browse" option in each Image Viewport allows users to select images for processing.

#### Image Processing

The application processes the loaded images to generate Fourier Transform components. Users can visualize these components in the FT Viewports. The processed images serve as the basis for the mixing operations.

### 3. Image Mixing

#### Mixing Options

Users can select pairs of FT components for mixing using combo boxes. The available pairs include combinations of Magnitude, Phase, Real, and Imaginary components. The application validates user selections to ensure the mixing process is valid.

#### Mixing Parameters

Adjustable sliders enable users to fine-tune mixing parameters. These parameters include weights assigned to each selected FT component, providing control over the contribution of each component to the final mixed image.

### 4. Interactive User Interactions

#### Component Selection

Users can interactively select regions of images and FT components for mixing. The application provides functionality to extract and manipulate specific regions, enhancing user control over the mixing process.

#### Brightness and Contrast Adjustment

To facilitate better visualization, users can adjust the brightness and contrast of images using mouse interactions. This feature improves the clarity of selected regions and aids in the mixing process.

### 5. Error Handling

#### Error Messages

The application displays informative error messages for invalid user inputs or operations. This ensures that users receive feedback on issues such as invalid component selections or unsuccessful mixing attempts.

### 6. Logging

#### Logging

The project incorporates logging functionality using Python's `logging` module. Events and errors are logged to a file named `our_log.log`. This log file captures details about the application's activities, aiding in debugging and issue resolution.

## How to Use

1. **Run the Application:**
   - Execute the application script to launch the GUI.

2. **Load Images:**
   - Double click on any input Image Viewport Use the "Browse" option to load images.

3. **Adjust Parameters:**
   - Interactively adjust brightness and contrast for better visualization via Rightclick on the mouse and drag horizontally and vertically .

4. **Select Mixing Options:**
   - Choose FT components and set mixing parameters.

5. **Mix Images:**
   - Click the "Mix" button to initiate the image mixing process.

6. **View Output:**
   - The mixed image is displayed in the Output Viewport.

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

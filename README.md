# Documentation: Installing PyPangolin from Source

This guide covers the specific sequence required to build **Pangolin** with Python bindings (`pypangolin`) so that it is compatible with modern NumPy arrays and strict `pybind11` type checking.

---

### Part 1: System Preparation & Installation

Execute these commands in your terminal to install the necessary dependencies and build the library.

### 1. Clone the Repository

Bash

```
git clone --recursive https://github.com/stevenlovegrove/Pangolin.git
cd Pangolin`
```
### 2. Install Prerequisites

Bash

```
# Get the core tools and GL development headers
sudo apt update
sudo apt install cmake pkg-config libgl1-mesa-dev libglew-dev libwayland-dev libx11-dev \
                 python3-dev python3-pip pybind11-dev`
```
### 3. Build & Python Integration

This step ensures the Python interpreter you are currently using is the one Pangolin binds to.

Bash

```
# Create and enter build directory
mkdir build && cd build

# Configure with explicit Python path
cmake .. -DPython3_EXECUTABLE=$(which python3)

# Verify the output: 
# Ensure it says: "Selected Python: /usr/bin/python3" 
# and "Building PyPangolin: Yes"

# Build the library using 8 cores
cmake --build . -j8

# Install the Python bindings directly to your python environment
cmake --build . -t pypangolin_pip_install`
```
---

### Part 2: Verified Implementation Example

The following code is specifically written to handle the **Strict Binding** requirements of the latest `pypangolin` builds, specifically the `pango.Attach` requirement for viewports and the `list[ndarray]` requirement for drawing points.

### `pango_debug_test.py`

Python

```
import pypangolin as pango
from OpenGL.GL import *
import numpy as np

def format_list(arr):
    """
    Helper to convert Nx3 matrix to list of 3x1 arrays.
    Required by this specific build's pypangolin signature for 
    functions like glDrawPoints and glDrawLines.
    """
    return [p.reshape(3, 1).astype(np.float32) for p in arr]

def main():
    # 1. Create Window and Bind Context
    pango.CreateWindowAndBind('V-SLAM Debugger', 640, 480)
    glEnable(GL_DEPTH_TEST)

    # 2. Setup Camera State (Projection and View Matrix)
    scam = pango.OpenGlRenderState(
        pango.ProjectionMatrix(640, 480, 420, 420, 320, 240, 0.2, 200),
        pango.ModelViewLookAt(-2, 2, -2, 0, 0, 0, pango.AxisDirection.AxisY))
    
    handler = pango.Handler3D(scam)

    # 3. Setup Display Viewport 
    # Must use pango.Attach for boundary values
    dcam = pango.CreateDisplay().SetBounds(
        pango.Attach(0.0), pango.Attach(1.0), # Bottom to Top
        pango.Attach(0.0), pango.Attach(1.0), # Left to Right
        -640.0/480.0                          # Aspect Ratio
    ).SetHandler(handler)

    # 4. Data Generation (Dummy Trajectory)
    trajectory = [np.array([0, 0, 0])]
    for i in range(100):
        trajectory.append(trajectory[-1] + (np.random.random(3) * 0.2 - 0.1))
    
    # Pre-format the list to avoid overhead in the render loop
    traj_list = format_list(trajectory)

    print("Controls: Left-click rotate, Scroll zoom, Right-click pan. Press Esc to exit.")

    while not pango.ShouldQuit():
        # Clear screen with White Background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        
        dcam.Activate(scam)
        
        # --- DRAWING SECTION ---

        # A. Draw RGB Axis at Origin
        pango.glDrawAxis(0.5)

        # B. Draw Coloured Cube (Built-in Pangolin helper)
        pango.glDrawColouredCube(0.1)

        # C. Draw Random Point Cloud (Red)
        points = np.random.random((100, 3)) * 2 - 1
        glPointSize(3)
        glColor3f(1.0, 0.0, 0.0) 
        pango.glDrawPoints(format_list(points))

        # D. Draw Trajectory Line (Black) using raw OpenGL for stability
        glLineWidth(2)
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        for p in trajectory:
            glVertex3f(p[0], p[1], p[2])
        glEnd()

        # E. Draw Camera Representation (Blue Axis)
        glColor3f(0.0, 0.0, 1.0) 
        pango.glDrawAxis(0.3) 

        pango.FinishFrame()

if __name__ == '__main__':
    main()`
```
---

### Key Compatibility Notes

- **`pango.Attach(val)`**: Unlike older versions or C++ examples that accept `float`, the Python bindings require explicit wrapping of window coordinates.
- **`format_list()`**: The `pypangolin` C++ wrapper expects `std::vector<Eigen::Matrix<float,3,1>>`. In Python, this translates to a list of individual 3x1 NumPy arrays, not a single Nx3 matrix.
- **OpenGL Context**: `PyOpenGL` (`from OpenGL.GL import *`) functions will work correctly as long as they are called *after* `CreateWindowAndBind` and within the same thread.

Would you like me to help you create a **`setup.py`** or a **`requirements.txt`** to ensure these dependencies are automatically handled for your team?

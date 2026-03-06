import pypangolin as pango
from OpenGL.GL import *
import numpy as np

def format_list(arr):
    """
    Helper to convert Nx3 matrix to list of 3x1 arrays.
    Required by this specific build's pypangolin signature.
    """
    return [p.reshape(3, 1).astype(np.float32) for p in arr]

def main():
    # 1. Create Window
    pango.CreateWindowAndBind('V-SLAM Debugger', 640, 480)
    glEnable(GL_DEPTH_TEST)

    # 2. Setup Camera State
    scam = pango.OpenGlRenderState(
        pango.ProjectionMatrix(640, 480, 420, 420, 320, 240, 0.2, 200),
        pango.ModelViewLookAt(-2, 2, -2, 0, 0, 0, pango.AxisDirection.AxisY))
    
    handler = pango.Handler3D(scam)

    # 3. Setup Display Viewport (FIXED: Using pango.Attach)
    dcam = pango.CreateDisplay().SetBounds(
        pango.Attach(0.0), pango.Attach(1.0), # Bottom to Top
        pango.Attach(0.0), pango.Attach(1.0), # Left to Right
        -640.0/480.0                          # Aspect Ratio
    ).SetHandler(handler)

    # 4. Pre-generate a dummy SLAM Trajectory
    trajectory = [np.array([0, 0, 0])]
    for i in range(100):
        # Move slightly in a random direction
        trajectory.append(trajectory[-1] + (np.random.random(3) * 0.2 - 0.1))
    
    # Convert trajectory to the list format required for drawing
    traj_list = format_list(trajectory)

    print("Controls: Left-click rotate, Scroll zoom, Right-click pan. Press Esc to exit.")

    while not pango.ShouldQuit():
        # Clear screen with White Background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        
        dcam.Activate(scam)
        
        # Draw RGB Axis at Origin
        pango.glDrawAxis(0.5)

        # 1. Draw Coloured Cube (built-in helper)
        pango.glDrawColouredCube(0.1)

        # 2. Draw Random Point Cloud (Red)
        # Generates new points every frame for visualization test
        points = np.random.random((100, 3)) * 2 - 1
        glPointSize(3)
        glColor3f(1.0, 0.0, 0.0) # Red
        pango.glDrawPoints(format_list(points))

        # --- Alternative if glDrawLineStrip is missing ---
        glLineWidth(2)
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        for p in trajectory:
            glVertex3f(p[0], p[1], p[2])
        glEnd()

        # 4. Draw a Camera Frustum (Blue)
        # Note: If pango.glDrawFrustum isn't in your build, glDrawAxis is the backup
        glColor3f(0.0, 0.0, 1.0) 
        pango.glDrawAxis(0.3) 

        pango.FinishFrame()

if __name__ == '__main__':
    main()
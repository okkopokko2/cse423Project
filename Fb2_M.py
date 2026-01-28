from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

# Game state variables
camera_pos = [0, 8, 0]  # Player position
camera_rot_x = 0  # Camera rotation around X-axis (pitch)
camera_rot_y = 0  # Camera rotation around Y-axis (yaw)
camera_speed = 0.2  # Much smoother movement
mouse_sensitivity = 0.2  # Much smoother mouse movement

# World generation variables - ULTRA OPTIMIZED for smoothness
CHUNK_SIZE = 4  # Even smaller chunks
WORLD_SIZE = 1  # Tiny world for maximum smoothness
BLOCK_SIZE = 1.0
world_blocks = {}  # Dictionary to store block positions and types

# Performance tracking
last_frame_time = time.time()
frame_count = 0
fps = 0

# Block types - simplified for performance
BLOCK_TYPES = {
    'grass': (0.2, 0.8, 0.2),    # Green
    'dirt': (0.6, 0.4, 0.2),     # Brown
    'stone': (0.5, 0.5, 0.5),    # Gray
}

# Game settings
fovY = 60  # Reduced FOV for better performance
GRID_LENGTH = 25  # Much smaller grid
rand_var = 423

# Mouse state
last_mouse_x = 500
last_mouse_y = 400
mouse_captured = False

# World generation flag
world_generated = False

# Rendering optimization
visible_blocks = set()  # Cache for visible blocks
last_camera_pos = None  # Track camera movement for optimization

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draw text on screen at specified coordinates"""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_shapes():
    """Modified to draw the Minecraft world instead of original shapes"""
    global world_generated, world_blocks, visible_blocks, last_camera_pos
    
    # Generate world on first call
    if not world_generated:
        # Generate a tiny, ultra-optimized voxel world
        world_blocks.clear()
        
        for chunk_x in range(-WORLD_SIZE, WORLD_SIZE):
            for chunk_z in range(-WORLD_SIZE, WORLD_SIZE):
                for x in range(CHUNK_SIZE):
                    for z in range(CHUNK_SIZE):
                        world_x = chunk_x * CHUNK_SIZE + x
                        world_z = chunk_z * CHUNK_SIZE + z
                        
                        # Ultra-simple height generation for maximum performance
                        height = int(2 + math.sin(world_x * 0.3) + math.sin(world_z * 0.3))
                        
                        # Generate terrain layers
                        for y in range(height + 1):
                            if y == height:
                                block_type = 'grass'
                            else:
                                block_type = 'stone'
                            
                            world_blocks[(world_x, y, world_z)] = block_type
        
        world_generated = True
    
    # Update visible blocks cache for optimization
    if last_camera_pos is None or (
        abs(camera_pos[0] - last_camera_pos[0]) > 2 or
        abs(camera_pos[2] - last_camera_pos[2]) > 2
    ):
        visible_blocks.clear()
        
        # Calculate visible chunks based on camera position
        camera_chunk_x = int(camera_pos[0] / (CHUNK_SIZE * BLOCK_SIZE))
        camera_chunk_z = int(camera_pos[2] / (CHUNK_SIZE * BLOCK_SIZE))
        
        # Render chunks within tiny view distance
        view_distance = 1  # Ultra-small view distance
        for chunk_x in range(camera_chunk_x - view_distance, camera_chunk_x + view_distance + 1):
            for chunk_z in range(camera_chunk_z - view_distance, camera_chunk_z + view_distance + 1):
                for x in range(CHUNK_SIZE):
                    for z in range(CHUNK_SIZE):
                        world_x = chunk_x * CHUNK_SIZE + x
                        world_z = chunk_z * CHUNK_SIZE + z
                        
                        # Check if block exists at this position
                        for y in range(8):  # Ultra-reduced height check
                            if (world_x, y, world_z) in world_blocks:
                                visible_blocks.add((world_x, y, world_z))
        
        last_camera_pos = camera_pos.copy()
    
    # Draw the world - ultra-optimized rendering
    for block_pos in visible_blocks:
        x, y, z = block_pos
        if block_pos in world_blocks:
            block_type = world_blocks[block_pos]
            if block_type in BLOCK_TYPES:
                color = BLOCK_TYPES[block_type]
                glColor3f(*color)
                
                # Calculate cube vertices
                x1, y1, z1 = x * BLOCK_SIZE, y * BLOCK_SIZE, z * BLOCK_SIZE
                x2, y2, z2 = (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE, (z + 1) * BLOCK_SIZE
                
                # Draw cube faces - simplified for performance
                glBegin(GL_QUADS)
                
                # Front face only (for maximum performance)
                glVertex3f(x1, y1, z1)
                glVertex3f(x2, y1, z1)
                glVertex3f(x2, y2, z1)
                glVertex3f(x1, y2, z1)
                
                # Top face only
                glVertex3f(x1, y2, z1)
                glVertex3f(x2, y2, z1)
                glVertex3f(x2, y2, z2)
                glVertex3f(x1, y2, z2)
                
                glEnd()

def keyboardListener(key, x, y):
    """Handle keyboard inputs for player movement and block interaction"""
    global camera_pos, camera_rot_y, world_blocks, visible_blocks
    
    # Calculate movement direction based on camera rotation
    angle_rad = math.radians(camera_rot_y)
    forward_x = -math.sin(angle_rad)
    forward_z = -math.cos(angle_rad)
    right_x = math.cos(angle_rad)
    right_z = -math.sin(angle_rad)
    
    # Move forward (W key)
    if key == b'w':
        camera_pos[0] += forward_x * camera_speed
        camera_pos[2] += forward_z * camera_speed
    
    # Move backward (S key)
    if key == b's':
        camera_pos[0] -= forward_x * camera_speed
        camera_pos[2] -= forward_z * camera_speed
    
    # Strafe left (A key)
    if key == b'a':
        camera_pos[0] -= right_x * camera_speed
        camera_pos[2] -= right_z * camera_speed
    
    # Strafe right (D key)
    if key == b'd':
        camera_pos[0] += right_x * camera_speed
        camera_pos[2] += right_z * camera_speed
    
    # Jump (Space key)
    if key == b' ':
        camera_pos[1] += camera_speed
    
    # Crouch (Shift key)
    if key == b'\x1b':  # Shift key
        camera_pos[1] -= camera_speed
    
    # Place block (E key)
    if key == b'e':
        # Calculate the direction the player is looking
        angle_rad_y = math.radians(camera_rot_y)
        angle_rad_x = math.radians(camera_rot_x)
        
        # Calculate forward vector
        forward_x = -math.sin(angle_rad_y) * math.cos(angle_rad_x)
        forward_y = -math.sin(angle_rad_x)
        forward_z = -math.cos(angle_rad_y) * math.cos(angle_rad_x)
        
        # Calculate block position (3 units in front of player)
        block_x = int((camera_pos[0] + forward_x * 3) / BLOCK_SIZE)
        block_y = int((camera_pos[1] + forward_y * 3) / BLOCK_SIZE)
        block_z = int((camera_pos[2] + forward_z * 3) / BLOCK_SIZE)
        
        # Place a grass block
        world_blocks[(block_x, block_y, block_z)] = 'grass'
        visible_blocks.add((block_x, block_y, block_z))
    
    # Remove block (Q key)
    if key == b'q':
        # Calculate the direction the player is looking
        angle_rad_y = math.radians(camera_rot_y)
        angle_rad_x = math.radians(camera_rot_x)
        
        # Calculate forward vector
        forward_x = -math.sin(angle_rad_y) * math.cos(angle_rad_x)
        forward_y = -math.sin(angle_rad_x)
        forward_z = -math.cos(angle_rad_y) * math.cos(angle_rad_x)
        
        # Check blocks along the ray
        for distance in range(1, 4):  # Reduced range for performance
            check_x = int((camera_pos[0] + forward_x * distance) / BLOCK_SIZE)
            check_y = int((camera_pos[1] + forward_y * distance) / BLOCK_SIZE)
            check_z = int((camera_pos[2] + forward_z * distance) / BLOCK_SIZE)
            
            if (check_x, check_y, check_z) in world_blocks:
                del world_blocks[(check_x, check_y, check_z)]
                visible_blocks.discard((check_x, check_y, check_z))
                break
    
    # Toggle mouse capture (Tab key)
    if key == b'\t':
        global mouse_captured
        mouse_captured = not mouse_captured
        if mouse_captured:
            glutSetCursor(GLUT_CURSOR_NONE)
        else:
            glutSetCursor(GLUT_CURSOR_INHERIT)

def specialKeyListener(key, x, y):
    """Handle special key inputs for camera movement"""
    global camera_pos
    
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_pos[1] += camera_speed
    
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_pos[1] -= camera_speed
    
    # Move camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_pos[0] -= camera_speed
    
    # Move camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_pos[0] += camera_speed

def mouseListener(button, state, x, y):
    """Handle mouse inputs for block interaction"""
    global mouse_captured, world_blocks, visible_blocks
    
    # Left mouse button removes blocks
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Calculate the direction the player is looking
        angle_rad_y = math.radians(camera_rot_y)
        angle_rad_x = math.radians(camera_rot_x)
        
        # Calculate forward vector
        forward_x = -math.sin(angle_rad_y) * math.cos(angle_rad_x)
        forward_y = -math.sin(angle_rad_x)
        forward_z = -math.cos(angle_rad_y) * math.cos(angle_rad_x)
        
        # Check blocks along the ray
        for distance in range(1, 4):  # Reduced range for performance
            check_x = int((camera_pos[0] + forward_x * distance) / BLOCK_SIZE)
            check_y = int((camera_pos[1] + forward_y * distance) / BLOCK_SIZE)
            check_z = int((camera_pos[2] + forward_z * distance) / BLOCK_SIZE)
            
            if (check_x, check_y, check_z) in world_blocks:
                del world_blocks[(check_x, check_y, check_z)]
                visible_blocks.discard((check_x, check_y, check_z))
                break
    
    # Right mouse button places blocks
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Calculate the direction the player is looking
        angle_rad_y = math.radians(camera_rot_y)
        angle_rad_x = math.radians(camera_rot_x)
        
        # Calculate forward vector
        forward_x = -math.sin(angle_rad_y) * math.cos(angle_rad_x)
        forward_y = -math.sin(angle_rad_x)
        forward_z = -math.cos(angle_rad_y) * math.cos(angle_rad_x)
        
        # Calculate block position (3 units in front of player)
        block_x = int((camera_pos[0] + forward_x * 3) / BLOCK_SIZE)
        block_y = int((camera_pos[1] + forward_y * 3) / BLOCK_SIZE)
        block_z = int((camera_pos[2] + forward_z * 3) / BLOCK_SIZE)
        
        # Place a grass block
        world_blocks[(block_x, block_y, block_z)] = 'grass'
        visible_blocks.add((block_x, block_y, block_z))
    
    # Middle mouse button toggles mouse capture
    if button == GLUT_MIDDLE_BUTTON and state == GLUT_DOWN:
        mouse_captured = not mouse_captured
        if mouse_captured:
            glutSetCursor(GLUT_CURSOR_NONE)
        else:
            glutSetCursor(GLUT_CURSOR_INHERIT)

def setupCamera():
    """Configure the camera's projection and view settings"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Set up a perspective projection
    gluPerspective(fovY, 1.25, 0.1, 200)  # Ultra-reduced far clip for maximum performance
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Apply camera rotation
    glRotatef(-camera_rot_x, 1, 0, 0)
    glRotatef(-camera_rot_y, 0, 1, 0)
    
    # Apply camera translation
    glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])

def idle():
    """Idle function that runs continuously for smooth updates"""
    global last_frame_time, frame_count, fps
    
    # Calculate FPS
    current_time = time.time()
    frame_count += 1
    
    if current_time - last_frame_time >= 1.0:
        fps = frame_count
        frame_count = 0
        last_frame_time = current_time
    
    glutPostRedisplay()

def showScreen():
    """Display function to render the game scene"""
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    # Enable depth testing for proper 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    setupCamera()
    
    # Draw the world using the modified draw_shapes function
    draw_shapes()
    
    # Draw crosshair - simplified for performance
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw simple crosshair
    glBegin(GL_LINES)
    glVertex2f(495, 400)  # Horizontal line left
    glVertex2f(485, 400)
    glVertex2f(505, 400)  # Horizontal line right
    glVertex2f(515, 400)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # Display game info with FPS
    draw_text(10, 770, "Minecraft-Style Voxel World (Template Compliant)")
    draw_text(10, 740, f"Position: ({camera_pos[0]:.1f}, {camera_pos[1]:.1f}, {camera_pos[2]:.1f})")
    draw_text(10, 710, f"Rotation: ({camera_rot_x:.1f}, {camera_rot_y:.1f})")
    draw_text(10, 680, f"FPS: {fps}")
    draw_text(10, 650, "Controls: WASD=Move, Mouse=Look, E=Place, Q=Remove, Tab=Toggle Mouse")
    
    # Swap buffers for smooth rendering
    glutSwapBuffers()

def main():
    """Main function to set up OpenGL window and game loop"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutPassiveMotionFunc(passiveMouseListener)
    glutMotionFunc(passiveMouseListener)
    wind = glutCreateWindow(b"Minecraft-Style Voxel World (Template Compliant)")
    
    # Register callback functions
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    # Set initial mouse position
    glutWarpPointer(500, 400)
    
    # Enter the GLUT main loop
    glutMainLoop()

if __name__ == "__main__":
    main()
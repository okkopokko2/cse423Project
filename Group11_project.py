from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Camera-related variables
camera_pos = [0, 500, 500]
fovY = 60
GRID_LENGTH = 600

# Game state variables
GAME_RUNNING = True
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

# Player variables
player_pos = [0.0, 0.0, 30.0]
player_rotation = 0.0
player_pitch = 0.0  # Vertical look angle
player_health = 100
player_max_health = 100
player_speed = 5.0
player_radius = 100.0  # Player detection radius - increased for larger detection area
is_first_person = False

# Jump physics
player_vel_z = 0.0
is_grounded = True

# Game mechanics
pokeball_count = 10
total_caught = 0
experience_points = 0
shop_currency = 0
current_pokeball_type = 0  # 0=pokeball, 1=greatball, 2=ultraball, 3=masterball

# Walking animation variables
is_walking = False
walk_cycle = 0.0
walk_speed = 0.2

# Mouse tracking variables
mouse_x = WINDOW_WIDTH // 2
mouse_y = WINDOW_HEIGHT // 2
mouse_sensitivity = 0.2
mouse_capture_enabled = True  # Toggle for mouse control

# Pokemon data - using simple lists instead of classes
# Each pokemon: [x, y, z, type, health, max_health, caught, being_caught, direction, move_timer]
pokemon_list = []
max_pokemon = 20
spawn_timer = 0
spawn_interval = 3.0
last_time = 0

# Pokeball data - using simple lists instead of classes
# Each pokeball: [x, y, z, vx, vy, vz, active, target_x, target_y, target_z]
pokeballs_thrown = []
rocks_thrown = []

# Bush data - each bush: [x, y, z, radius, pokemon_index]
bush_list = []

# UI event message (e.g., hit/capture notifications)
last_event_message = ""
last_event_timer = 0.0  # seconds remaining to display

# Game state
game_over = False
ultra_balls = 0

# AI Opponent system
opponent_pos = [200, 200, 30]
opponent_health = 100
opponent_max_health = 100
opponent_pokeballs = 10
opponent_throw_cooldown = 0.0
opponent_move_timer = 0.0
opponent_direction = 0.0
opponent_pokeballs_thrown = []





# Pokemon types data
pokemon_types = [
    # [name, r, g, b, size, catch_rate, speed, health, type, special_features]
    ["Pikachu", 1.0, 1.0, 0.0, 15, 0.7, 2.0, 50, "Electric", "ears"],
    ["Charmander", 1.0, 0.4, 0.0, 18, 0.6, 1.5, 60, "Fire", "tail_flame"],
    ["Squirtle", 0.0, 0.6, 1.0, 16, 0.65, 1.8, 55, "Water", "shell"],
    ["Bulbasaur", 0.2, 0.8, 0.4, 17, 0.65, 1.6, 58, "Grass", "bulb"],
    ["Dragonite", 1.0, 0.6, 0.2, 25, 0.3, 3.0, 120, "Dragon", "wings"],
    ["Mewtwo", 0.8, 0.6, 0.9, 30, 0.1, 4.0, 200, "Psychic", "aura"],
    ["Eevee", 0.8, 0.6, 0.4, 14, 0.8, 2.5, 45, "Normal", "fluffy_tail"],
    ["Jigglypuff", 1.0, 0.8, 0.9, 16, 0.75, 1.0, 70, "Fairy", "round_body"],
    ["Gengar", 0.4, 0.2, 0.6, 20, 0.4, 3.5, 80, "Ghost", "shadow_aura"],
    ["Lapras", 0.3, 0.7, 1.0, 28, 0.5, 1.2, 100, "Water", "shell_back"],
    ["Snorlax", 0.2, 0.4, 0.6, 35, 0.2, 0.5, 150, "Normal", "sleeping"],
    ["Machamp", 0.6, 0.3, 0.8, 22, 0.3, 2.0, 90, "Fighting", "four_arms"],
    ["Alakazam", 0.9, 0.7, 0.3, 18, 0.4, 2.8, 75, "Psychic", "spoons"],
    ["Gyarados", 0.1, 0.3, 0.9, 32, 0.2, 1.8, 110, "Water", "serpent_body"],
    ["Arcanine", 1.0, 0.5, 0.0, 24, 0.4, 3.2, 95, "Fire", "mane"]
]

# Pokeball types data
pokeball_types = [
    # [name, r, g, b, catch_bonus, cost]
    ["Pokeball", 1.0, 0.0, 0.0, 0.0, 0],
    ["Great Ball", 0.0, 0.0, 1.0, 0.15, 5],
    ["Ultra Ball", 1.0, 1.0, 0.0, 0.3, 15],
    ["Master Ball", 0.5, 0.0, 1.0, 0.95, 50]
]

# Terrain data - simple height map
terrain_heights = {}
BLOCK_SIZE = 20

def draw_text(x, y, text, font=None):
    # Use retro pixel font for authentic gaming feel
    text_font = GLUT_BITMAP_9_BY_15
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw shadow (drop shadow for retro style)
    glColor3f(0.0, 0.0, 0.0)
    glRasterPos2f(x + 1, y - 1)
    for ch in text:
        glutBitmapCharacter(text_font, ord(ch))
    
    # Main retro text with bright neon colors
    glColor3f(0.0, 1.0, 0.8)  # Cyan/teal for retro gaming feel
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(text_font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_terrain():
    """Draw simple terrain using quads"""
    glColor3f(0.2, 0.8, 0.2)  # Green grass color
    
    # Draw a simple grid-based terrain
    for x in range(-GRID_LENGTH, GRID_LENGTH, BLOCK_SIZE):
        for y in range(-GRID_LENGTH, GRID_LENGTH, BLOCK_SIZE):
            # Simple height calculation
            height = 5 * math.sin(x * 0.01) * math.cos(y * 0.01)
            
            glBegin(GL_QUADS)
            glVertex3f(x, y, height)
            glVertex3f(x + BLOCK_SIZE, y, height)
            glVertex3f(x + BLOCK_SIZE, y + BLOCK_SIZE, height)
            glVertex3f(x, y + BLOCK_SIZE, height)
            glEnd()

def draw_opponent():
    """Draw the AI opponent character (red version of player)"""
    global opponent_move_timer
    
    glPushMatrix()
    glTranslatef(opponent_pos[0], opponent_pos[1], opponent_pos[2])
    glRotatef(opponent_direction, 0, 0, 1)
    glRotatef(90, 0, 0, 1)  # Rotate body 90 degrees to the right
    
    # Calculate animation angles
    arm_swing = math.sin(opponent_move_timer * 2) * 30
    leg_swing = math.sin(opponent_move_timer * 2) * 20
    
    # Opponent body (torso) - Red shirt
    glColor3f(0.8, 0.2, 0.2)  # Red shirt
    glutSolidCube(18)
    
    # Shirt details
    glColor3f(1.0, 1.0, 1.0)  # White collar
    glPushMatrix()
    glTranslatef(0, 0, 8)
    glutSolidTorus(2, 8, 6, 6)
    glPopMatrix()
    
    # Opponent head
    glPushMatrix()
    glTranslatef(0, 0, 16)
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glutSolidSphere(7, 10, 10)
    
    # Hair
    glColor3f(0.3, 0.2, 0.1)  # Brown hair
    glPushMatrix()
    glTranslatef(0, 0, 4)
    glutSolidSphere(6, 8, 8)
    glPopMatrix()
    
    # Eyes
    glColor3f(0.1, 0.1, 0.1)  # Black eyes
    glPushMatrix()
    glTranslatef(-2, 5, 2)
    glutSolidSphere(1, 6, 6)
    glTranslatef(4, 0, 0)
    glutSolidSphere(1, 6, 6)
    glPopMatrix()
    
    # Cap (Red opponent cap)
    glColor3f(0.8, 0.2, 0.2)  # Red cap
    glPushMatrix()
    glTranslatef(0, 0, 6)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()
    
    glPopMatrix()
    
    # Left arm (swings opposite to right leg)
    glPushMatrix()
    glTranslatef(-12, 0, 6)  # Position to left side of body
    glRotatef(arm_swing, 1, 0, 0)  # Swing animation
    glRotatef(90, 0, 1, 0)   # Rotate to make cylinder horizontal
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glutSolidCylinder(2.5, 12, 8, 8)  # Upper arm
    glTranslatef(0, 0, 12)
    glutSolidCylinder(2, 8, 6, 6)  # Forearm
    glPopMatrix()
    
    # Right arm (swings opposite to left leg)
    glPushMatrix()
    glTranslatef(12, 0, 6)   # Position to right side of body
    glRotatef(-arm_swing, 1, 0, 0)  # Swing animation (opposite direction)
    glRotatef(-90, 0, 1, 0)  # Rotate to make cylinder horizontal
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glutSolidCylinder(2.5, 12, 8, 8)  # Upper arm
    glTranslatef(0, 0, 12)
    glutSolidCylinder(2, 8, 6, 6)  # Forearm
    glPopMatrix()
    
    # Left leg (swings opposite to right arm)
    glPushMatrix()
    glTranslatef(-6, 0, -12)  # Position to left side below body
    glRotatef(-leg_swing, 1, 0, 0)  # Swing animation
    glRotatef(90, 1, 0, 0)    # Rotate to make cylinder vertical
    glColor3f(0.1, 0.1, 0.1)  # Black pants
    glutSolidCylinder(3.5, 16, 8, 8)  # Thigh
    glTranslatef(0, 0, 16)
    glutSolidCylinder(3, 12, 6, 6)  # Shin
    glPopMatrix()
    
    # Right leg (swings opposite to left arm)
    glPushMatrix()
    glTranslatef(6, 0, -12)   # Position to right side below body
    glRotatef(leg_swing, 1, 0, 0)  # Swing animation (opposite direction)
    glRotatef(90, 1, 0, 0)    # Rotate to make cylinder vertical
    glColor3f(0.1, 0.1, 0.1)  # Black pants
    glutSolidCylinder(3.5, 16, 8, 8)  # Thigh
    glTranslatef(0, 0, 12)
    glutSolidCylinder(3, 12, 6, 6)  # Shin
    glPopMatrix()
    
    glPopMatrix()

def draw_player():
    """Draw enhanced player character with better proportions and Pokemon trainer outfit"""
    global is_walking, walk_cycle
    
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_rotation, 0, 0, 1)
    glRotatef(90, 0, 0, 1)  # Rotate body 90 degrees to the right
    
    # Calculate animation angles
    arm_swing = 0
    leg_swing = 0
    if is_walking:
        arm_swing = math.sin(walk_cycle) * 30  # 30 degree swing
        leg_swing = math.sin(walk_cycle) * 20  # 20 degree swing
        # Reset walking state (will be set again if still moving)
        is_walking = False
    
    # Player body (torso) - Pokemon trainer shirt
    glColor3f(0.2, 0.4, 0.8)  # Blue shirt
    glutSolidCube(18)
    
    # Shirt details
    glColor3f(1.0, 1.0, 1.0)  # White collar
    glPushMatrix()
    glTranslatef(0, 0, 8)
    glutSolidTorus(2, 8, 6, 6)
    glPopMatrix()
    
    # Player head
    glPushMatrix()
    glTranslatef(0, 0, 16)
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glutSolidSphere(7, 10, 10)
    
    # Hair
    glColor3f(0.3, 0.2, 0.1)  # Brown hair
    glPushMatrix()
    glTranslatef(0, 0, 4)
    glutSolidSphere(6, 8, 8)
    glPopMatrix()
    
    # Eyes
    glColor3f(0.1, 0.1, 0.1)  # Black eyes
    glPushMatrix()
    glTranslatef(-2, 5, 2)
    glutSolidSphere(1, 6, 6)
    glTranslatef(4, 0, 0)
    glutSolidSphere(1, 6, 6)
    glPopMatrix()
    
    # Cap (Pokemon trainer cap)
    glColor3f(1.0, 0.0, 0.0)  # Red cap
    glPushMatrix()
    glTranslatef(0, 0, 6)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()
    
    glPopMatrix()
    
    # Left arm (swings opposite to right leg)
    glPushMatrix()
    glTranslatef(-12, 0, 6)  # Position to left side of body
    glRotatef(arm_swing, 1, 0, 0)  # Swing animation
    glRotatef(90, 0, 1, 0)   # Rotate to make cylinder horizontal
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glutSolidCylinder(2.5, 12, 8, 8)  # Upper arm
    glTranslatef(0, 0, 12)
    glutSolidCylinder(2, 8, 6, 6)  # Forearm
    glPopMatrix()
    
    # Right arm (swings opposite to left leg)
    glPushMatrix()
    glTranslatef(12, 0, 6)   # Position to right side of body
    glRotatef(-arm_swing, 1, 0, 0)  # Swing animation (opposite direction)
    glRotatef(-90, 0, 1, 0)  # Rotate to make cylinder horizontal
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glutSolidCylinder(2.5, 12, 8, 8)  # Upper arm
    glTranslatef(0, 0, 12)
    glutSolidCylinder(2, 8, 6, 6)  # Forearm
    glPopMatrix()
    
    # Left leg (swings opposite to right arm)
    glPushMatrix()
    glTranslatef(-6, 0, -12)  # Position to left side below body
    glRotatef(-leg_swing, 1, 0, 0)  # Swing animation
    glRotatef(90, 1, 0, 0)    # Rotate to make cylinder vertical
    glColor3f(0.1, 0.1, 0.1)  # Black pants
    glutSolidCylinder(3.5, 16, 8, 8)  # Thigh
    glTranslatef(0, 0, 16)
    glutSolidCylinder(3, 12, 6, 6)  # Shin
    glPopMatrix()
    
    # Right leg (swings opposite to left arm)
    glPushMatrix()
    glTranslatef(6, 0, -12)   # Position to right side below body
    glRotatef(leg_swing, 1, 0, 0)  # Swing animation (opposite direction)
    glRotatef(90, 1, 0, 0)    # Rotate to make cylinder vertical
    glColor3f(0.1, 0.1, 0.1)  # Black pants
    glutSolidCylinder(3.5, 16, 8, 8)  # Thigh
    glTranslatef(0, 0, 16)
    glutSolidCylinder(3, 12, 6, 6)  # Shin
    glPopMatrix()
    
    # Backpack (Pokemon trainer backpack)
    glPushMatrix()
    glTranslatef(-8, -8, 2)
    glColor3f(0.8, 0.6, 0.2)  # Brown backpack
    glutSolidCube(12)
    glPopMatrix()
    
    # Pokeball belt
    glPushMatrix()
    glTranslatef(0, 0, -5)
    glColor3f(0.0, 0.0, 0.0)  # Black belt
    glutSolidTorus(1, 12, 6, 6)
    
    # Pokeballs on belt
    glColor3f(1.0, 0.0, 0.0)  # Red pokeball
    glPushMatrix()
    glTranslatef(8, 0, 0)
    glutSolidSphere(2, 6, 6)
    glPopMatrix()
    
    glColor3f(0.0, 0.0, 1.0)  # Blue great ball
    glPushMatrix()
    glTranslatef(-8, 0, 0)
    glutSolidSphere(2, 6, 6)
    glPopMatrix()
    
    glPopMatrix()
    
    glPopMatrix()

def draw_pokemon():
    """Draw all pokemon with unique visual features - only visible ones"""
    for i in range(len(pokemon_list)):
        pokemon = pokemon_list[i]
        if len(pokemon) < 8 or pokemon[6]:  # Skip if caught
            continue
        
        # Only draw Pokemon if they are visible (player radius intersects bush)
        if not is_pokemon_visible(i):
            continue
            
        x, y, z, ptype, health, max_health = pokemon[0], pokemon[1], pokemon[2], pokemon[3], pokemon[4], pokemon[5]
        
        glPushMatrix()
        glTranslatef(x, y, z + 20)  # Ensure Pokemon are above ground level
        
        # Add floating animation
        float_offset = math.sin(pokemon[9] * 2) * 3  # Use move_timer for animation
        glTranslatef(0, 0, float_offset)
        
        # Pokemon body
        pdata = pokemon_types[ptype]
        glColor3f(pdata[1], pdata[2], pdata[3])  # Pokemon color
        
        # Draw Pokemon-specific shapes and features
        draw_pokemon_features(pdata, pokemon[9])  # Pass animation time
        
        # Health bar above pokemon - billboarded to always face camera
        glTranslatef(0, 0, pdata[4] + 15)
        
        # Calculate billboard rotation to face camera
        glPushMatrix()
        
        # Calculate actual camera position based on player position and rotation
        if is_first_person:
            # First person camera position
            cam_x = player_pos[0]
            cam_y = player_pos[1]
            cam_z = player_pos[2] + 15
        else:
            # Over-the-shoulder camera position (match setupCamera)
            camera_distance = 60
            camera_height = 30
            shoulder_offset = 25
            cam_x = player_pos[0] - camera_distance * math.cos(math.radians(player_rotation)) + shoulder_offset * math.cos(math.radians(player_rotation + 90))
            cam_y = player_pos[1] - camera_distance * math.sin(math.radians(player_rotation)) + shoulder_offset * math.sin(math.radians(player_rotation + 90))
            cam_z = player_pos[2] + camera_height
        
        bar_x, bar_y, bar_z = x, y, z + pdata[4] + 15
        
        # Direction vector from health bar to camera
        dir_x = cam_x - bar_x
        dir_y = cam_y - bar_y
        dir_z = cam_z - bar_z
        
        # Calculate rotation angles to face camera
        # Rotation around Z-axis (yaw)
        yaw_angle = math.atan2(dir_y, dir_x) * 180.0 / math.pi
        glRotatef(yaw_angle, 0, 0, 1)
        
        # Rotation around Y-axis (pitch) - calculate pitch from horizontal distance and vertical distance
        horizontal_dist = math.sqrt(dir_x * dir_x + dir_y * dir_y)
        if horizontal_dist > 0:
            pitch_angle = math.atan2(dir_z, horizontal_dist) * 180.0 / math.pi
            glRotatef(-pitch_angle, 0, 1, 0)
        
        # Health bar background
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-12, -2, 0)
        glVertex3f(12, -2, 0)
        glVertex3f(12, 2, 0)
        glVertex3f(-12, 2, 0)
        glEnd()
        
        # Health bar fill
        health_ratio = health / max_health if max_health > 0 else 0
        if health_ratio > 0.6:
            glColor3f(0.0, 1.0, 0.0)  # Green
        elif health_ratio > 0.3:
            glColor3f(1.0, 1.0, 0.0)  # Yellow
        else:
            glColor3f(1.0, 0.0, 0.0)  # Red
        
        glBegin(GL_QUADS)
        glVertex3f(-10, -1, 0.1)
        glVertex3f(-10 + (20 * health_ratio), -1, 0.1)
        glVertex3f(-10 + (20 * health_ratio), 1, 0.1)
        glVertex3f(-10, 1, 0.1)
        glEnd()
        
        # Pokemon name above health bar
        # Pixelated name label using 9x15 with shadow
        name_x = -len(pdata[0]) * 4
        name_y = 5
        glColor3f(0.0, 0.0, 0.0)
        glRasterPos3f(name_x + 2, name_y - 2, 0)
        for char in pdata[0]:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
        glColor3f(1.0, 1.0, 0.6)
        glRasterPos3f(name_x, name_y, 0)
        for char in pdata[0]:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
        
        glPopMatrix()
        
        glPopMatrix()

def draw_pokemon_features(pdata, animation_time):
    """Draw unique features for each Pokemon type"""
    name = pdata[0]
    size = pdata[4]
    color = (pdata[1], pdata[2], pdata[3])
    
    # Main body - make it more visible
    glutSolidSphere(size, 16, 16)
    
    # Pokemon-specific features
    if name == "Pikachu":
        # Yellow ears
        glColor3f(0.8, 0.8, 0.2)
        glPushMatrix()
        glTranslatef(-size*0.6, 0, size*0.8)
        glutSolidSphere(size*0.3, 8, 8)
        glTranslatef(size*1.2, 0, 0)
        glutSolidSphere(size*0.3, 8, 8)
        glPopMatrix()
        
        # Red cheeks
        glColor3f(1.0, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(size*0.7, size*0.5, size*0.3)
        glutSolidSphere(size*0.2, 6, 6)
        glTranslatef(0, -size*1.0, 0)
        glutSolidSphere(size*0.2, 6, 6)
        glPopMatrix()
        
    elif name == "Charmander":
        # Orange tail with flame
        glColor3f(1.0, 0.3, 0.0)
        glPushMatrix()
        glTranslatef(-size*1.2, 0, -size*0.3)
        glRotatef(45, 0, 1, 0)
        glutSolidSphere(size*0.4, 8, 8)
        glPopMatrix()
        
        # Flame on tail
        glColor3f(1.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(-size*1.5, 0, -size*0.2)
        glRotatef(45, 0, 1, 0)
        glutSolidSphere(size*0.3, 6, 6)
        glPopMatrix()
        
    elif name == "Squirtle":
        # Blue shell
        glColor3f(0.1, 0.4, 0.8)
        glPushMatrix()
        glTranslatef(0, 0, -size*0.4)
        glutSolidSphere(size*0.8, 12, 12)
        glPopMatrix()
        
    elif name == "Bulbasaur":
        # Green bulb on back
        glColor3f(0.1, 0.9, 0.1)
        glPushMatrix()
        glTranslatef(0, 0, size*0.8)
        glutSolidSphere(size*0.6, 10, 10)
        glPopMatrix()
        
    elif name == "Dragonite":
        # Orange wings
        glColor3f(1.0, 0.5, 0.2)
        glPushMatrix()
        glTranslatef(-size*0.8, 0, size*0.3)
        glScalef(0.2, 1.2, 0.1)
        glutSolidSphere(size*0.8, 8, 8)
        glTranslatef(size*8, 0, 0)
        glutSolidSphere(size*0.8, 8, 8)
        glPopMatrix()
        
    elif name == "Mewtwo":
        # Purple aura effect
        glColor3f(0.6, 0.3, 0.8)
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glutSolidSphere(size*1.2, 8, 8)
        glPopMatrix()
        
    elif name == "Eevee":
        # Brown fluffy tail
        glColor3f(0.6, 0.4, 0.2)
        glPushMatrix()
        glTranslatef(-size*0.8, 0, -size*0.2)
        glutSolidSphere(size*0.5, 10, 10)
        glPopMatrix()
        
        # Cream collar
        glColor3f(0.9, 0.8, 0.7)
        glPushMatrix()
        glTranslatef(0, 0, size*0.2)
        glutSolidTorus(size*0.1, size*0.6, 8, 8)
        glPopMatrix()
        
    elif name == "Jigglypuff":
        # Pink round body (already drawn as main sphere)
        # Add curl on head
        glColor3f(0.9, 0.7, 0.8)
        glPushMatrix()
        glTranslatef(0, 0, size*0.9)
        glutSolidSphere(size*0.3, 8, 8)
        glPopMatrix()
        
    elif name == "Gengar":
        # Dark purple with spikes
        glColor3f(0.2, 0.1, 0.4)
        glPushMatrix()
        glTranslatef(0, 0, size*0.8)
        glutSolidSphere(size*0.4, 6, 6)
        glPopMatrix()
        
    elif name == "Lapras":
        # Blue shell-like back
        glColor3f(0.2, 0.5, 0.9)
        glPushMatrix()
        glTranslatef(0, 0, -size*0.3)
        glutSolidSphere(size*0.9, 12, 12)
        glPopMatrix()
        
    elif name == "Snorlax":
        # Large sleeping body (already drawn as main sphere)
        # Add closed eyes
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(-size*0.3, size*0.6, size*0.4)
        glutSolidSphere(size*0.15, 6, 6)
        glTranslatef(size*0.6, 0, 0)
        glutSolidSphere(size*0.15, 6, 6)
        glPopMatrix()
        
    elif name == "Machamp":
        # Four arms
        glColor3f(0.4, 0.2, 0.6)
        # Left arms
        glPushMatrix()
        glTranslatef(-size*0.8, -size*0.3, size*0.2)
        glutSolidSphere(size*0.3, 8, 8)
        glTranslatef(0, size*0.6, 0)
        glutSolidSphere(size*0.3, 8, 8)
        glPopMatrix()
        # Right arms
        glPushMatrix()
        glTranslatef(size*0.8, -size*0.3, size*0.2)
        glutSolidSphere(size*0.3, 8, 8)
        glTranslatef(0, size*0.6, 0)
        glutSolidSphere(size*0.3, 8, 8)
        glPopMatrix()
        
    elif name == "Alakazam":
        # Psychic spoons
        glColor3f(0.8, 0.6, 0.2)
        glPushMatrix()
        glTranslatef(-size*0.8, 0, size*0.5)
        glRotatef(90, 0, 1, 0)
        glutSolidCylinder(1, size*0.8, 6, 6)
        glTranslatef(0, 0, size*1.6)
        glutSolidCylinder(1, size*0.8, 6, 6)
        glPopMatrix()
        
    elif name == "Gyarados":
        # Serpent-like body
        glColor3f(0.0, 0.2, 0.8)
        glPushMatrix()
        glTranslatef(-size*0.5, 0, 0)
        glutSolidSphere(size*0.7, 10, 10)
        glTranslatef(-size*0.8, 0, 0)
        glutSolidSphere(size*0.6, 10, 10)
        glPopMatrix()
        
    elif name == "Arcanine":
        # Orange mane
        glColor3f(1.0, 0.4, 0.0)
        glPushMatrix()
        glTranslatef(0, 0, size*0.6)
        glutSolidSphere(size*0.8, 10, 10)
        glPopMatrix()
        
        # Black stripes
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, 0, size*0.3)
        glScalef(1.1, 0.1, 0.1)
        glutSolidSphere(size*0.5, 6, 6)
        glPopMatrix()
    
    # Reset color to original Pokemon color
    glColor3f(*color)

def draw_pokeballs():
    """Draw all thrown pokeballs"""
    for i in range(len(pokeballs_thrown)):
        pokeball = pokeballs_thrown[i]
        if len(pokeball) < 7 or not pokeball[6]:  # Skip if not active
            continue
            
        x, y, z = pokeball[0], pokeball[1], pokeball[2]
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Pokeball body
        ball_type = pokeball_types[current_pokeball_type]
        glColor3f(ball_type[1], ball_type[2], ball_type[3])
        glutSolidSphere(8, 8, 8)
        
        # White stripe
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(0, 0, 0.1)
        glScalef(1.1, 1.1, 0.2)
        glutSolidSphere(8, 8, 8)
        
        glPopMatrix()

def draw_opponent_pokeballs():
    """Draw all opponent pokeballs"""
    for pokeball in opponent_pokeballs_thrown:
        if not pokeball[6]:  # Skip if not active
            continue
        
        x, y, z = pokeball[0], pokeball[1], pokeball[2]
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Opponent pokeball (different color to distinguish)
        glColor3f(0.8, 0.2, 0.8)  # Purple/magenta
        glutSolidSphere(3, 8, 8)
        
        glPopMatrix()

def draw_rocks():
    """Draw all thrown rocks"""
    for i in range(len(rocks_thrown)):
        rock = rocks_thrown[i]
        if len(rock) < 7 or not rock[6]:  # Skip if not active
            continue
            
        x, y, z = rock[0], rock[1], rock[2]
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Rock (gray sphere)
        glColor3f(0.5, 0.5, 0.5)
        glutSolidSphere(6, 6, 6)
        
        glPopMatrix()

def draw_bushes():
    """Draw all bushes using OpenGL primitives - only if they should be visible"""
    for i in range(len(bush_list)):
        bush = bush_list[i]
        if len(bush) < 5:
            continue
            
        # Only draw bush if it should be visible (not intersecting with player radius)
        if not is_bush_visible(i):
            continue
            
        x, y, z, radius = bush[0], bush[1], bush[2], bush[3]
        
        # Draw multiple spheres to create a bush effect
        for j in range(8):  # 8 spheres per bush
            glPushMatrix()
            
            # Random offset for each sphere within the bush radius
            offset_x = (j % 3 - 1) * radius * 0.3
            offset_y = ((j // 3) % 3 - 1) * radius * 0.3
            offset_z = (j // 6) * radius * 0.2
            
            glTranslatef(x + offset_x, y + offset_y, z + offset_z)
            
            # Green bush color with slight variation
            green_variation = 0.3 + (j * 0.1) % 0.4
            glColor3f(0.1, green_variation, 0.1)
            glutSolidSphere(radius * 0.2, 8, 8)  # Reduced size to be smaller than Pokemon
            
            glPopMatrix()

def draw_player_radius():
    """Draw visible player detection radius using OpenGL lines"""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 5)  # Slightly above ground
    
    # Draw circle using line segments
    glColor3f(0.0, 1.0, 1.0)  # Cyan color for visibility
    glBegin(GL_LINES)
    
    num_segments = 32
    for i in range(num_segments):
        angle1 = (i * 2 * math.pi) / num_segments
        angle2 = ((i + 1) * 2 * math.pi) / num_segments
        
        x1 = player_radius * math.cos(angle1)
        y1 = player_radius * math.sin(angle1)
        x2 = player_radius * math.cos(angle2)
        y2 = player_radius * math.sin(angle2)
        
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
    
    glEnd()
    glPopMatrix()

def is_pokemon_visible(pokemon_index):
    """Check if Pokemon should be visible based on player radius intersection with bush"""
    if pokemon_index >= len(pokemon_list) or pokemon_index >= len(bush_list):
        return False
    
    pokemon = pokemon_list[pokemon_index]
    bush = bush_list[pokemon_index]
    
    if len(pokemon) < 7 or len(bush) < 5:
        return False
    
    if pokemon[6]:  # Pokemon is caught
        return False
    
    # Calculate distance between player and bush center
    bush_x, bush_y, bush_radius = bush[0], bush[1], bush[3]
    distance = math.sqrt(
        (player_pos[0] - bush_x)**2 + 
        (player_pos[1] - bush_y)**2
    )
    
    # Check if player radius intersects with bush radius
    return distance <= (player_radius + bush_radius)

def is_bush_visible(bush_index):
    """Check if bush should be visible - bushes disappear when player radius intersects"""
    if bush_index >= len(bush_list):
        return False
    
    bush = bush_list[bush_index]
    
    if len(bush) < 5:
        return False
    
    # Calculate distance between player and bush center
    bush_x, bush_y, bush_radius = bush[0], bush[1], bush[3]
    distance = math.sqrt(
        (player_pos[0] - bush_x)**2 + 
        (player_pos[1] - bush_y)**2
    )
    
    # Bush is visible when player radius does NOT intersect with bush radius
    return distance > (player_radius + bush_radius)

def draw_game_over_screen():
    """Draw game over screen with restart button"""
    # Semi-transparent overlay
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()
    
    # Game Over text
    glColor3f(1.0, 0.0, 0.0)  # Red
    draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 50, "GAME OVER!")
    
    # Restart button
    glColor3f(0.0, 1.0, 0.0)  # Green
    draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, "Press R to Restart")
    
    # Stats
    glColor3f(1.0, 1.0, 1.0)  # White
    draw_text(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 - 50, f"Pokemon Caught: {total_caught}")
    draw_text(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 - 80, f"Final Score: {experience_points}")

def draw_hud():
    """Draw game HUD"""
    # Health bar
    health_ratio = player_health / player_max_health
    
    # Health bar background
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex2f(20, WINDOW_HEIGHT - 40)
    glVertex2f(220, WINDOW_HEIGHT - 40)
    glVertex2f(220, WINDOW_HEIGHT - 20)
    glVertex2f(20, WINDOW_HEIGHT - 20)
    glEnd()
    
    # Health bar fill
    if health_ratio > 0.6:
        glColor3f(0.0, 1.0, 0.0)
    elif health_ratio > 0.3:
        glColor3f(1.0, 1.0, 0.0)
    else:
        glColor3f(1.0, 0.0, 0.0)
    
    glBegin(GL_QUADS)
    glVertex2f(22, WINDOW_HEIGHT - 38)
    glVertex2f(22 + (196 * health_ratio), WINDOW_HEIGHT - 38)
    glVertex2f(22 + (196 * health_ratio), WINDOW_HEIGHT - 22)
    glVertex2f(22, WINDOW_HEIGHT - 22)
    glEnd()
    
    # Game stats with better formatting
    draw_text(20, WINDOW_HEIGHT - 60, f"Health: {int(player_health)}/{player_max_health}")
    draw_text(20, WINDOW_HEIGHT - 80, f"Pokeballs: {pokeball_count}")
    draw_text(20, WINDOW_HEIGHT - 100, f"Level: {experience_points // 100 + 1}")
    draw_text(20, WINDOW_HEIGHT - 120, f"EXP: {experience_points}")
    draw_text(20, WINDOW_HEIGHT - 140, f"Coins: {shop_currency}")
    draw_text(20, WINDOW_HEIGHT - 160, f"Opponent Health: {opponent_health}/{opponent_max_health}")
    draw_text(20, WINDOW_HEIGHT - 180, f"Ultra Balls: {ultra_balls} (Press X to use)")
    
    # Pokemon count with type breakdown
    visible_pokemon = [p for p in pokemon_list if len(p) >= 7 and not p[6]]
    draw_text(20, WINDOW_HEIGHT - 180, f"Pokemon nearby: {len(visible_pokemon)}")
    draw_text(20, WINDOW_HEIGHT - 200, f"Total caught: {total_caught}")
    
    # Current pokeball type with color coding
    ball_name = pokeball_types[current_pokeball_type][0]
    ball_color = pokeball_types[current_pokeball_type]
    glColor3f(ball_color[1], ball_color[2], ball_color[3])  # Set color to pokeball color
    draw_text(20, WINDOW_HEIGHT - 220, f"Current: {ball_name}")
    glColor3f(1.0, 1.0, 1.0)  # Reset to white
    
    # Camera mode with better positioning
    mode_text = "1st Person" if is_first_person else "3rd Person"
    draw_text(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 30, f"Camera: {mode_text}")
    
    # Mouse control status
    mouse_text = "Enabled" if mouse_capture_enabled else "Disabled"
    draw_text(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 50, f"Mouse: {mouse_text}")
    
    # Show nearest Pokemon info
    nearest_pos = get_nearest_pokemon()
    if nearest_pos:
        distance = math.sqrt((nearest_pos[0] - player_pos[0])**2 + (nearest_pos[1] - player_pos[1])**2)
        draw_text(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 80, f"Nearest Pokemon: {int(distance)} units away")
    
    # Show Pokemon type distribution
    type_counts = {}
    for pokemon in visible_pokemon:
        if len(pokemon) >= 4:
            ptype = pokemon[3]
            if ptype < len(pokemon_types):
                pokemon_name = pokemon_types[ptype][0]
                type_counts[pokemon_name] = type_counts.get(pokemon_name, 0) + 1
    
    if type_counts:
        y_offset = WINDOW_HEIGHT - 220
        draw_text(20, y_offset, "Pokemon Types:")
        for pokemon_name, count in list(type_counts.items())[:3]:  # Show top 3
            y_offset -= 20
            draw_text(40, y_offset, f"{pokemon_name}: {count}")

    # Show last combat event message (lower-center) with drop shadow and bright color
    if last_event_timer > 0 and last_event_message:
        x = int(WINDOW_WIDTH * 0.5) - 250
        y = int(WINDOW_HEIGHT * 0.5) + 160
        
        # Shadow for retro style
        glColor3f(0.0, 0.0, 0.0)
        draw_text(x + 1, y - 1, last_event_message)
        
        # Main message - bright neon green for combat events
        glColor3f(0.0, 1.0, 0.0)
        draw_text(x, y, last_event_message)
    
    # Crosshair in center of screen
    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2
    crosshair_size = 10
    
    glColor3f(1.0, 1.0, 1.0)  # White crosshair
    glBegin(GL_LINES)
    # Horizontal line
    glVertex2f(center_x - crosshair_size, center_y)
    glVertex2f(center_x + crosshair_size, center_y)
    # Vertical line
    glVertex2f(center_x, center_y - crosshair_size)
    glVertex2f(center_x, center_y + crosshair_size)
    glEnd()
    
    # Controls
    draw_text(20, 100, "Controls: WASD - Move, Arrow Keys - Camera, C - Switch Camera")
    draw_text(20, 80, "Space - Jump, Left Click - Throw Rock, Right Click - Throw Pokeball")
    draw_text(20, 60, "R - Reset, M - Toggle Mouse, H - Heal, J - Damage, 1-4 - Select Pokeball")
    draw_text(20, 40, "X - Ultra Ball (instant opponent defeat), Catch 5 Pokemon to earn 1 Ultra Ball!")

def spawn_pokemon():
    """Spawn a new pokemon at random location with surrounding bushes, ensuring proper spacing"""
    if len(pokemon_list) >= max_pokemon:
        return
    
    # Minimum distance between Pokemon
    min_distance = 80  # Minimum spacing between Pokemon
    max_attempts = 20  # Maximum attempts to find a valid position
    
    for attempt in range(max_attempts):
        # Random position around player
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, 300)
        x = player_pos[0] + distance * math.cos(angle)
        y = player_pos[1] + distance * math.sin(angle)
        z = 0  # Ground level (will be adjusted in drawing)
        
        # Check distance to existing Pokemon
        valid_position = True
        for existing_pokemon in pokemon_list:
            if len(existing_pokemon) < 7 or existing_pokemon[6]:  # Skip if caught
                continue
            
            # Calculate distance using math functions from context file
            dx = x - existing_pokemon[0]
            dy = y - existing_pokemon[1]
            distance_to_existing = math.sqrt(dx * dx + dy * dy)
            
            if distance_to_existing < min_distance:
                valid_position = False
                break
        
        if valid_position:
            # Random pokemon type
            ptype = random.randint(0, len(pokemon_types) - 1)
            pdata = pokemon_types[ptype]
            
            # Create pokemon: [x, y, z, type, health, max_health, caught, being_caught, direction, move_timer]
            pokemon = [x, y, z, ptype, pdata[7], pdata[7], False, False, random.uniform(0, 360), 0]
            pokemon_index = len(pokemon_list)
            pokemon_list.append(pokemon)
            
            # Create bush around the pokemon: [x, y, z, radius, pokemon_index]
            bush_radius = 40  # Large bush radius
            bush = [x, y, z, bush_radius, pokemon_index]
            bush_list.append(bush)
            
            print(f"A wild {pdata[0]} appeared in the bushes!")
            return
    
    # If no valid position found after max attempts, spawn anyway but with warning
    print("Warning: Could not find optimal spacing for new Pokemon")
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(100, 300)
    x = player_pos[0] + distance * math.cos(angle)
    y = player_pos[1] + distance * math.sin(angle)
    z = 0
    
    ptype = random.randint(0, len(pokemon_types) - 1)
    pdata = pokemon_types[ptype]
    pokemon = [x, y, z, ptype, pdata[7], pdata[7], False, False, random.uniform(0, 360), 0]
    pokemon_index = len(pokemon_list)
    pokemon_list.append(pokemon)
    
    bush_radius = 40
    bush = [x, y, z, bush_radius, pokemon_index]
    bush_list.append(bush)
    
    print(f"A wild {pdata[0]} appeared in the bushes!")

def update_pokemon(dt):
    """Update pokemon AI with basic behaviors"""
    for i in range(len(pokemon_list)):
        if i >= len(pokemon_list):
            break
        pokemon = pokemon_list[i]
        if len(pokemon) < 10 or pokemon[6]:  # Skip if caught
            continue
        
        # Update animation timer
        pokemon[9] += dt
        
        # Basic Pokemon behaviors
        pdata = pokemon_types[pokemon[3]]
        pokemon_name = pdata[0]
        
        # Some Pokemon have special behaviors
        if pokemon_name == "Snorlax":
            # Snorlax occasionally "sleeps" (moves very slowly)
            if random.random() < 0.01:  # 1% chance per frame
                pokemon[0] += random.uniform(-2, 2)
                pokemon[1] += random.uniform(-2, 2)
        elif pokemon_name == "Gengar":
            # Gengar occasionally "teleports" (moves randomly)
            if random.random() < 0.005:  # 0.5% chance per frame
                pokemon[0] += random.uniform(-10, 10)
                pokemon[1] += random.uniform(-10, 10)
        elif pokemon_name in ["Pikachu", "Eevee"]:
            # Small Pokemon occasionally hop around
            if random.random() < 0.02:  # 2% chance per frame
                pokemon[0] += random.uniform(-5, 5)
                pokemon[1] += random.uniform(-5, 5)
        
        # Keep Pokemon within reasonable bounds
        pokemon[0] = max(-GRID_LENGTH + 50, min(GRID_LENGTH - 50, pokemon[0]))
        pokemon[1] = max(-GRID_LENGTH + 50, min(GRID_LENGTH - 50, pokemon[1]))

def throw_pokeball(target_x, target_y, target_z):
    """Throw a pokeball towards target with moderate speed in straight line"""
    global pokeball_count
    
    if pokeball_count <= 0:
        print("No Pokeballs left!")
        return
    
    # Determine throw origin: from eye in 1st person, from player's right shoulder/hand in 3rd person
    if is_first_person:
        origin_x = player_pos[0]
        origin_y = player_pos[1]
        origin_z = player_pos[2] + 20
    else:
        # Right shoulder/hand position relative to player facing
        shoulder_offset = 25
        forward_offset = 10
        hand_height = 20
        origin_x = player_pos[0] + shoulder_offset * math.cos(math.radians(player_rotation + 90)) + forward_offset * math.cos(math.radians(player_rotation))
        origin_y = player_pos[1] + shoulder_offset * math.sin(math.radians(player_rotation + 90)) + forward_offset * math.sin(math.radians(player_rotation))
        origin_z = player_pos[2] + hand_height
    
    # Calculate direct velocity vector for straight-line trajectory from origin
    dx = target_x - origin_x
    dy = target_y - origin_y
    dz = target_z - origin_z
    
    # Calculate distance and normalize direction
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance > 0:
        # Moderate speed for reliable connection
        speed = 300.0  # Same speed as rocks for consistent behavior
        vx = (dx / distance) * speed
        vy = (dy / distance) * speed
        vz = (dz / distance) * speed
    else:
        vx = vy = vz = 0
    
    # Nudge origin slightly along direction to avoid clipping with player model
    nudge = 5.0
    origin_x += (0 if distance == 0 else (dx / distance) * nudge)
    origin_y += (0 if distance == 0 else (dy / distance) * nudge)
    origin_z += (0 if distance == 0 else (dz / distance) * nudge)

    # Create pokeball: [x, y, z, vx, vy, vz, active, target_x, target_y, target_z]
    pokeball = [origin_x, origin_y, origin_z, vx, vy, vz, True, target_x, target_y, target_z]
    pokeballs_thrown.append(pokeball)
    pokeball_count -= 1
    
    print(f"Pokeball thrown! Remaining: {pokeball_count}")

def throw_rock(target_x, target_y, target_z):
    """Throw a rock towards target with moderate speed in straight line"""
    # Determine throw origin: from eye in 1st person, from player's right shoulder/hand in 3rd person
    if is_first_person:
        origin_x = player_pos[0]
        origin_y = player_pos[1]
        origin_z = player_pos[2] + 20
    else:
        # Right shoulder/hand position relative to player facing
        shoulder_offset = 25
        forward_offset = 10
        hand_height = 20
        origin_x = player_pos[0] + shoulder_offset * math.cos(math.radians(player_rotation + 90)) + forward_offset * math.cos(math.radians(player_rotation))
        origin_y = player_pos[1] + shoulder_offset * math.sin(math.radians(player_rotation + 90)) + forward_offset * math.sin(math.radians(player_rotation))
        origin_z = player_pos[2] + hand_height
    
    # Calculate direct velocity vector for straight-line trajectory from origin
    dx = target_x - origin_x
    dy = target_y - origin_y
    dz = target_z - origin_z
    
    # Calculate distance and normalize direction
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance > 0:
        # Moderate speed for reliable connection
        speed = 300.0  # Increased speed for faster travel
        vx = (dx / distance) * speed
        vy = (dy / distance) * speed
        vz = (dz / distance) * speed
    else:
        vx = vy = vz = 0
    
    # Nudge origin slightly along direction to avoid clipping with player model
    nudge = 5.0
    origin_x += (0 if distance == 0 else (dx / distance) * nudge)
    origin_y += (0 if distance == 0 else (dy / distance) * nudge)
    origin_z += (0 if distance == 0 else (dz / distance) * nudge)

    # Create rock: [x, y, z, vx, vy, vz, active, target_x, target_y, target_z]
    rock = [origin_x, origin_y, origin_z, vx, vy, vz, True, target_x, target_y, target_z]
    rocks_thrown.append(rock)
    
    print("Rock thrown!")

def update_pokeballs(dt):
    """Update pokeball physics with straight-line trajectory"""
    global total_caught, experience_points, shop_currency, ultra_balls, opponent_health, last_event_message, last_event_timer, player_health
    for i in range(len(pokeballs_thrown) - 1, -1, -1):
        pokeball = pokeballs_thrown[i]
        if not pokeball[6]:  # Not active
            continue
        
        # Update position with straight-line trajectory (no gravity)
        pokeball[0] += pokeball[3] * dt
        pokeball[1] += pokeball[4] * dt
        pokeball[2] += pokeball[5] * dt
        
        # Check ground collision
        if pokeball[2] <= 5:
            pokeball[2] = 5
            pokeball[6] = False
        
        # Check pokemon collision with improved detection
        for j in range(len(pokemon_list)):
            pokemon = pokemon_list[j]
            if len(pokemon) < 7 or pokemon[6]:  # Skip if caught
                continue
            
            distance = math.sqrt(
                (pokeball[0] - pokemon[0])**2 +
                (pokeball[1] - pokemon[1])**2 +
                (pokeball[2] - pokemon[2])**2
            )
            
            pdata = pokemon_types[pokemon[3]]
            collision_radius = pdata[4] + 8  # Larger collision radius for better hit detection
            if distance < collision_radius:  # Hit!
                # Immediate capture on hit
                pokeball[6] = False
                if not pokemon[6]:
                    pokemon[6] = True
                    try:
                        remove_bush_for_pokemon(j)
                    except Exception:
                        pass
                    total_caught += 1
                    experience_points += 10
                    shop_currency += 5
                    
                    # Give ultra ball every 5 Pokémon caught
                    if total_caught % 5 == 0:
                        ultra_balls += 1
                        print(f"Ultra Ball earned! Total: {ultra_balls}")
                    
                    try:
                        pname = pokemon_types[pokemon[3]][0]
                    except Exception:
                        pname = "Pokemon"
                    print(f"Captured {pname}!")
                break
        
        # Check opponent collision (player can throw pokeballs at opponent)
        dx = pokeball[0] - opponent_pos[0]
        dy = pokeball[1] - opponent_pos[1]
        dz = pokeball[2] - opponent_pos[2]
        opponent_distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if opponent_distance < 20:  # Opponent hitbox
            pokeball[6] = False
            # Damage opponent and restore player health
            damage = random.randint(15, 25)
            opponent_health = max(0, opponent_health - damage)
            
            # Check for victory
            if opponent_health <= 0:
                last_event_message = "VICTORY! You defeated the opponent!"
                last_event_timer = 5.0
                print("VICTORY! You defeated the opponent!")
                # Reset opponent for rematch
                opponent_health = opponent_max_health
                opponent_pokeballs = 10
            else:
                # Restore 20 health when hitting opponent
                if player_health < player_max_health:
                    player_health = min(player_max_health, player_health + 20)
                    last_event_message = f"Opponent hit for {damage} damage! You regained 20 health! Health: {player_health}/{player_max_health}"
                else:
                    last_event_message = f"Opponent hit for {damage} damage! Health: {opponent_health}/{opponent_max_health}"
                
                last_event_timer = 2.5
                print(f"You hit opponent for {damage} damage! Health: {player_health}/{player_max_health}")
        
        # Remove inactive pokeballs
        if not pokeball[6]:
            pokeballs_thrown.pop(i)

def update_opponent(dt):
    """Update opponent AI behavior"""
    global opponent_pos, opponent_direction, opponent_move_timer, opponent_throw_cooldown, opponent_pokeballs, opponent_pokeballs_thrown
    
    # Move around randomly
    opponent_move_timer += dt
    if opponent_move_timer > 3.0:  # Change direction every 3 seconds
        opponent_direction = random.uniform(0, 360)
        opponent_move_timer = 0.0
    
    # Move in current direction
    move_speed = 15.0
    opponent_pos[0] += math.cos(math.radians(opponent_direction)) * move_speed * dt
    opponent_pos[1] += math.sin(math.radians(opponent_direction)) * move_speed * dt
    
    # Keep opponent within bounds
    opponent_pos[0] = max(-GRID_LENGTH + 50, min(GRID_LENGTH - 50, opponent_pos[0]))
    opponent_pos[1] = max(-GRID_LENGTH + 50, min(GRID_LENGTH - 50, opponent_pos[1]))
    
    # Face player
    dx = player_pos[0] - opponent_pos[0]
    dy = player_pos[1] - opponent_pos[1]
    if dx != 0 or dy != 0:
        opponent_direction = math.atan2(dy, dx) * 180.0 / math.pi
    
    # Throw pokeball at player if cooldown is ready
    opponent_throw_cooldown -= dt
    if opponent_throw_cooldown <= 0 and opponent_pokeballs > 0:
        # Calculate direction to player
        dx = player_pos[0] - opponent_pos[0]
        dy = player_pos[1] - opponent_pos[1]
        dz = player_pos[2] - opponent_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 300:  # Only throw if player is within range
            # Create opponent pokeball
            speed = 200.0
            vx = (dx / distance) * speed if distance > 0 else 0
            vy = (dy / distance) * speed if distance > 0 else 0
            vz = (dz / distance) * speed if distance > 0 else 0
            
            opponent_pokeball = [opponent_pos[0], opponent_pos[1], opponent_pos[2] + 20, vx, vy, vz, True]
            opponent_pokeballs_thrown.append(opponent_pokeball)
            opponent_pokeballs -= 1
            opponent_throw_cooldown = 2.0  # 2 second cooldown

def update_opponent_pokeballs(dt):
    """Update opponent pokeball physics and handle player damage"""
    global opponent_pokeballs_thrown, player_health, last_event_message, last_event_timer
    
    for i in range(len(opponent_pokeballs_thrown) - 1, -1, -1):
        pokeball = opponent_pokeballs_thrown[i]
        if not pokeball[6]:  # Not active
            continue
        
        # Update position
        pokeball[0] += pokeball[3] * dt
        pokeball[1] += pokeball[4] * dt
        pokeball[2] += pokeball[5] * dt
        
        # Check ground collision
        if pokeball[2] <= 5:
            pokeball[6] = False
        
        # Check player collision
        dx = pokeball[0] - player_pos[0]
        dy = pokeball[1] - player_pos[1]
        dz = pokeball[2] - player_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 15:  # Player hitbox
            pokeball[6] = False
            # Damage player (exactly 20 damage)
            damage = 20
            global player_health
            player_health = max(0, player_health - damage)
            last_event_message = f"You were hit by opponent for {damage} damage! Health: {player_health}/{player_max_health}"
            last_event_timer = 2.5
            print(f"Opponent hit you for {damage} damage! Health: {player_health}/{player_max_health}")
            
            # Check if player died
            if player_health <= 0:
                global game_over
                game_over = True
                last_event_message = "GAME OVER! You were defeated by the opponent!"
                last_event_timer = 5.0
                print("GAME OVER! You were defeated by the opponent!")
                # Reset player health to prevent negative values
                player_health = 0
        
        # Remove inactive pokeballs
        if not pokeball[6]:
            opponent_pokeballs_thrown.pop(i)

def update_rocks(dt):
    """Update rock physics and handle Pokemon damage"""
    for i in range(len(rocks_thrown) - 1, -1, -1):
        rock = rocks_thrown[i]
        if not rock[6]:  # Not active
            continue
        
        # Update position with straight-line trajectory (no gravity)
        rock[0] += rock[3] * dt
        rock[1] += rock[4] * dt
        rock[2] += rock[5] * dt
        
        # Check ground collision
        if rock[2] <= 5:
            rock[2] = 5
            rock[6] = False
        
        # Check pokemon collision with improved detection
        for j in range(len(pokemon_list)):
            pokemon = pokemon_list[j]
            if len(pokemon) < 7 or pokemon[6]:  # Skip if caught
                continue
            
            distance = math.sqrt(
                (rock[0] - pokemon[0])**2 +
                (rock[1] - pokemon[1])**2 +
                (rock[2] - pokemon[2])**2
            )
            
            pdata = pokemon_types[pokemon[3]]
            collision_radius = pdata[4] + 10  # Slightly larger radius to catch all body parts/features
            if distance < collision_radius:  # Hit!
                rock[6] = False
                # Damage Pokemon (reduce health by 15-25 based on Pokemon type)
                damage = random.randint(15, 25)
                pokemon[4] -= damage
                pname = pdata[0]
                # On-screen message
                global last_event_message, last_event_timer
                last_event_message = f"{pname} hit by rock for {damage} damage! Health: {max(0, int(pokemon[4]))}/{int(pokemon[5])}"
                last_event_timer = 2.5
                print(last_event_message)
                
                # Remove Pokemon if health <= 0
                if pokemon[4] <= 0:
                    print(f"{pname} fainted!")
                    # Remove the bush associated with this Pokemon before removing Pokemon
                    remove_bush_for_pokemon(j)
                    pokemon_list.pop(j)
                    # Update bush indices for remaining Pokemon
                    update_bush_indices_after_removal(j)
                break
        
        # Remove inactive rocks
        if not rock[6]:
            rocks_thrown.pop(i)

def remove_bush_for_pokemon(pokemon_index):
    """Remove the bush associated with a specific Pokemon index"""
    for i in range(len(bush_list) - 1, -1, -1):
        bush = bush_list[i]
        if len(bush) >= 5 and bush[4] == pokemon_index:
            bush_list.pop(i)
            break

def update_bush_indices_after_removal(removed_index):
    """Update bush pokemon indices after a Pokemon is removed from the list"""
    for bush in bush_list:
        if len(bush) >= 5 and bush[4] > removed_index:
            bush[4] -= 1  # Decrease index by 1 since Pokemon was removed

def attempt_catch(pokemon_index):
    """Attempt to catch a pokemon"""
    global total_caught, experience_points, shop_currency, pokeball_count
    
    if pokemon_index >= len(pokemon_list):
        return
    
    pokemon = pokemon_list[pokemon_index]
    pdata = pokemon_types[pokemon[3]]
    
    # Calculate catch probability
    base_catch_rate = pdata[5]
    health_modifier = (pokemon[5] - pokemon[4]) / pokemon[5] * 0.3
    pokeball_bonus = pokeball_types[current_pokeball_type][4]
    catch_probability = min(0.98, base_catch_rate + health_modifier + pokeball_bonus)
    
    if random.random() < catch_probability:
        # Successful catch!
        print(f"Congratulations! You caught a {pdata[0]}!")
        pokemon[6] = True  # Mark as caught
        total_caught += 1
        
        # Remove the bush associated with this Pokemon
        remove_bush_for_pokemon(pokemon_index)
        
        # Rewards
        exp_reward = 10
        currency_reward = 5
        
        if pdata[0] in ["Dragonite", "Mewtwo"]:
            exp_reward = 25
            currency_reward = 15
        
        experience_points += exp_reward
        shop_currency += currency_reward
        pokeball_count += 2
        
        print(f"Gained {exp_reward} EXP and {currency_reward} coins!")
        print(f"You received 2 Pokeballs! Total: {pokeball_count}")
    else:
        # Failed catch
        print(f"Oh no! The {pdata[0]} broke free!")
        pokemon[4] = max(1, pokemon[4] - 10)  # Damage pokemon
        experience_points += 2
        shop_currency += 1

def get_nearest_pokemon():
    """Get nearest pokemon position"""
    nearest_dist = float('inf')
    nearest_pos = None
    
    for pokemon in pokemon_list:
        if len(pokemon) < 7 or pokemon[6]:  # Skip if caught
            continue
        
        dist = math.sqrt(
            (pokemon[0] - player_pos[0])**2 +
            (pokemon[1] - player_pos[1])**2
        )
        
        if dist < nearest_dist and dist < 150:
            nearest_dist = dist
            nearest_pos = [pokemon[0], pokemon[1], pokemon[2]]
    
    return nearest_pos

def setupCamera():
    """Setup camera based on mode with improved positioning"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
    gluPerspective(fovY, aspect_ratio, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if is_first_person:
        # First person camera with pitch support - improved positioning
        # Calculate look direction with both rotation and pitch
        look_distance = 200  # Increased for better visibility
        look_x = player_pos[0] + look_distance * math.cos(math.radians(player_rotation)) * math.cos(math.radians(player_pitch))
        look_y = player_pos[1] + look_distance * math.sin(math.radians(player_rotation)) * math.cos(math.radians(player_pitch))
        look_z = player_pos[2] + 20 + look_distance * math.sin(math.radians(player_pitch))  # Higher eye level
        
        gluLookAt(player_pos[0], player_pos[1], player_pos[2] + 20,  # Higher eye level
                  look_x, look_y, look_z,
                  0, 0, 1)
    else:
        # Over-the-shoulder camera (right shoulder) with improved positioning
        camera_distance = 60  # Slightly further for better view
        camera_height = 30    # Higher for better perspective
        shoulder_offset = 25  # More offset to the right side
        
        # Position camera behind and to the right of player
        cam_x = player_pos[0] - camera_distance * math.cos(math.radians(player_rotation)) + shoulder_offset * math.cos(math.radians(player_rotation + 90))
        cam_y = player_pos[1] - camera_distance * math.sin(math.radians(player_rotation)) + shoulder_offset * math.sin(math.radians(player_rotation + 90))
        cam_z = player_pos[2] + camera_height
        
        # Look ahead in the direction player is facing with pitch
        look_distance = 150  # Increased for better visibility
        look_x = player_pos[0] + look_distance * math.cos(math.radians(player_rotation)) * math.cos(math.radians(player_pitch))
        look_y = player_pos[1] + look_distance * math.sin(math.radians(player_rotation)) * math.cos(math.radians(player_pitch))
        look_z = player_pos[2] + 15 + look_distance * math.sin(math.radians(player_pitch))
        
        gluLookAt(cam_x, cam_y, cam_z,
                  look_x, look_y, look_z,
                  0, 0, 1)

def keyboardListener(key, x, y):
    """Handle keyboard input"""
    global player_pos, player_rotation, player_health, player_max_health
    global is_first_person, current_pokeball_type, shop_currency
    global is_walking, walk_cycle, mouse_capture_enabled
    global game_over, opponent_health, opponent_pokeballs, total_caught, experience_points
    global ultra_balls, pokeball_count, pokemon_list, pokeballs_thrown, rocks_thrown, opponent_pokeballs_thrown
    
    # Movement
    if key == b'w':
        player_pos[0] += player_speed * math.cos(math.radians(player_rotation))
        player_pos[1] += player_speed * math.sin(math.radians(player_rotation))
        is_walking = True
        walk_cycle += walk_speed
    elif key == b's':
        player_pos[0] -= player_speed * math.cos(math.radians(player_rotation))
        player_pos[1] -= player_speed * math.sin(math.radians(player_rotation))
        is_walking = True
        walk_cycle += walk_speed
    elif key == b'a':
        # Strafe left (perpendicular to current facing direction)
        player_pos[0] += player_speed * math.cos(math.radians(player_rotation + 90))
        player_pos[1] += player_speed * math.sin(math.radians(player_rotation + 90))
        is_walking = True
        walk_cycle += walk_speed
    elif key == b'd':
        # Strafe right (perpendicular to current facing direction)
        player_pos[0] += player_speed * math.cos(math.radians(player_rotation - 90))
        player_pos[1] += player_speed * math.sin(math.radians(player_rotation - 90))
        is_walking = True
        walk_cycle += walk_speed
    
    # Camera toggle
    elif key == b'c':
        is_first_person = not is_first_person
        print(f"Camera mode: {'1st Person' if is_first_person else '3rd Person'}")
    
    # Mouse capture toggle
    elif key == b'm':
        mouse_capture_enabled = not mouse_capture_enabled
        print(f"Mouse control: {'Enabled' if mouse_capture_enabled else 'Disabled'}")
    
    # Jump (apply impulse only if grounded)
    elif key == b' ':
        global player_vel_z, is_grounded
        if is_grounded:
            player_vel_z = 18.0
            is_grounded = False
    
    # Reset position or restart game
    elif key == b'r':
        if game_over:
            # Restart the entire game
            global player_health, opponent_health, opponent_pokeballs, total_caught, experience_points, shop_currency, ultra_balls, pokeball_count
            player_health = player_max_health
            opponent_health = opponent_max_health
            opponent_pokeballs = 10
            total_caught = 0
            experience_points = 0
            shop_currency = 0
            ultra_balls = 0
            pokeball_count = 10
            game_over = False
            
            # Clear all Pokémon and pokéballs
            global pokemon_list, pokeballs_thrown, rocks_thrown, opponent_pokeballs_thrown
            pokemon_list.clear()
            pokeballs_thrown.clear()
            rocks_thrown.clear()
            opponent_pokeballs_thrown.clear()
            
            print("Game restarted!")
        else:
            # Just reset position
            player_pos[0] = 0
            player_pos[1] = 0
            player_pos[2] = 30
            player_rotation = 0
            print("Position reset!")
    
    # Heal
    elif key == b'h':
        player_health = min(player_max_health, player_health + 20)
        print(f"Healed! Health: {player_health}/{player_max_health}")
    
    # Damage
    elif key == b'j':
        player_health = max(0, player_health - 10)
        print(f"Damaged! Health: {player_health}/{player_max_health}")
    
    # Pokeball selection
    elif key == b'1':
        current_pokeball_type = 0
        print(f"Selected: {pokeball_types[0][0]}")
    elif key == b'2' and shop_currency >= pokeball_types[1][5]:
        current_pokeball_type = 1
        print(f"Selected: {pokeball_types[1][0]}")
    elif key == b'3' and shop_currency >= pokeball_types[2][5]:
        current_pokeball_type = 2
        print(f"Selected: {pokeball_types[2][0]}")
    elif key == b'4' and shop_currency >= pokeball_types[3][5]:
        current_pokeball_type = 3
        print(f"Selected: {pokeball_types[3][0]}")
    
    # Ultra Ball (X key) - instant opponent defeat
    elif key == b'x' and ultra_balls > 0:
        ultra_balls -= 1
        opponent_health = 0
        last_event_message = "ULTRA BALL! Opponent defeated instantly!"
        last_event_timer = 3.0
        print(f"Ultra Ball used! Opponent defeated! Ultra Balls remaining: {ultra_balls}")

def specialKeyListener(key, x, y):
    """Handle special keys"""
    global player_rotation, player_pitch
    
    if key == GLUT_KEY_LEFT:
        player_rotation += 5
    elif key == GLUT_KEY_RIGHT:
        player_rotation -= 5
    elif key == GLUT_KEY_UP:
        player_pitch = min(90, player_pitch + 2)
    elif key == GLUT_KEY_DOWN:
        player_pitch = max(-90, player_pitch - 2)

def mouseListener(button, state, x, y):
    """Handle mouse input"""
    if state == GLUT_DOWN:
        # Calculate camera look direction for throwing
        if is_first_person:
            # In first person, cast a ray from eye using rotation and pitch
            look_distance = 200
            dir_x = math.cos(math.radians(player_rotation)) * math.cos(math.radians(player_pitch))
            dir_y = math.sin(math.radians(player_rotation)) * math.cos(math.radians(player_pitch))
            dir_z = math.sin(math.radians(player_pitch))
            target_x = player_pos[0] + dir_x * look_distance
            target_y = player_pos[1] + dir_y * look_distance
            target_z = player_pos[2] + 20 + dir_z * look_distance
        else:
            # In third person, calculate direction from camera to crosshair
            # Match camera params with setupCamera for consistency
            camera_distance = 60
            camera_height = 30
            shoulder_offset = 25
            
            cam_x = player_pos[0] - camera_distance * math.cos(math.radians(player_rotation)) + shoulder_offset * math.cos(math.radians(player_rotation + 90))
            cam_y = player_pos[1] - camera_distance * math.sin(math.radians(player_rotation)) + shoulder_offset * math.sin(math.radians(player_rotation + 90))
            cam_z = player_pos[2] + camera_height
            
            # Calculate look direction with pitch (same as camera)
            look_distance = 150
            look_x = player_pos[0] + look_distance * math.cos(math.radians(player_rotation)) * math.cos(math.radians(player_pitch))
            look_y = player_pos[1] + look_distance * math.sin(math.radians(player_rotation)) * math.cos(math.radians(player_pitch))
            look_z = player_pos[2] + 15 + look_distance * math.sin(math.radians(player_pitch))
            
            # Direction from camera to look point
            dir_x = look_x - cam_x
            dir_y = look_y - cam_y
            dir_z = look_z - cam_z
            
            # Normalize direction
            length = math.sqrt(dir_x*dir_x + dir_y*dir_y + dir_z*dir_z)
            if length > 0:
                dir_x /= length
                dir_y /= length
                dir_z /= length
            
            # Target point in look direction FROM CAMERA to align with crosshair
            target_x = cam_x + 200 * dir_x
            target_y = cam_y + 200 * dir_y
            target_z = cam_z + 200 * dir_z
        
        if button == GLUT_LEFT_BUTTON:
            # Left click - throw rock
            throw_rock(target_x, target_y, target_z)
        elif button == GLUT_RIGHT_BUTTON:
            # Right click - throw pokeball
            throw_pokeball(target_x, target_y, target_z)

def mouseMotionListener(x, y):
    """Handle mouse movement for character rotation"""
    global player_rotation, player_pitch, mouse_x, mouse_y, mouse_capture_enabled
    
    # Only process mouse movement if mouse capture is enabled
    if not mouse_capture_enabled:
        return
    
    # Calculate mouse movement delta
    delta_x = mouse_x - x
    delta_y = mouse_y - y
    
    # Update player rotation based on horizontal mouse movement
    player_rotation += delta_x * mouse_sensitivity
    
    # Update player pitch based on vertical mouse movement
    player_pitch += delta_y * mouse_sensitivity
    
    # Clamp vertical rotation to prevent camera flipping
    if player_pitch > 90:
        player_pitch = 90
    elif player_pitch < -90:
        player_pitch = -90
    
    # Keep rotation in 0-360 range
    if player_rotation >= 360:
        player_rotation -= 360
    elif player_rotation < 0:
        player_rotation += 360
    
    # Update mouse position
    mouse_x = x
    mouse_y = y

def idle():
    """Idle function for game updates"""
    global spawn_timer, last_time, last_event_timer, player_vel_z, is_grounded, level_time_left, level_caught_this_level, current_level
    
    current_time = time.time()
    if 'last_time' not in globals():
        last_time = current_time
    
    dt = current_time - last_time
    last_time = current_time
    
    # Spawn pokemon
    spawn_timer += dt
    if spawn_timer > spawn_interval:
        spawn_timer = 0
        spawn_pokemon()
    
    # Update game objects
    update_pokemon(dt)
    update_pokeballs(dt)
    update_rocks(dt)
    update_opponent(dt)
    update_opponent_pokeballs(dt)
    
    # Apply gravity and jump physics
    gravity = 40.0
    ground_z = 30.0
    # Integrate vertical velocity
    player_vel_z -= gravity * dt
    player_pos[2] += player_vel_z
    # Ground collision
    if player_pos[2] <= ground_z:
        player_pos[2] = ground_z
        player_vel_z = 0.0
        is_grounded = True

    # Decrement event message timer
    if last_event_timer > 0:
        last_event_timer = max(0.0, last_event_timer - dt)


    
    glutPostRedisplay()

def reshapeListener(width, height):
    """Handle window resizing"""
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    glViewport(0, 0, width, height)
    glutPostRedisplay()

def draw_clouds():
    """Draw clouds in the sky using spheres"""
    glPushMatrix()
    
    # Cloud positions and sizes
    cloud_data = [
        [-200, 300, 200, 30],   # x, y, z, size
        [150, 250, 180, 25],
        [-100, -200, 220, 35],
        [300, 100, 190, 28],
        [-350, -100, 210, 32],
        [200, -300, 170, 26],
        [0, 400, 200, 30],
        [-250, 150, 185, 29]
    ]
    
    # Draw each cloud as a group of spheres
    glColor3f(1.0, 1.0, 1.0)  # White clouds
    
    for cloud in cloud_data:
        x, y, z, size = cloud
        
        # Main cloud sphere
        glPushMatrix()
        glTranslatef(x, y, z)
        glutSolidSphere(size, 10, 10)
        glPopMatrix()
        
        # Additional spheres to make clouds more fluffy
        glPushMatrix()
        glTranslatef(x + size * 0.6, y, z - size * 0.2)
        glutSolidSphere(size * 0.8, 8, 8)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(x - size * 0.5, y + size * 0.3, z + size * 0.1)
        glutSolidSphere(size * 0.7, 8, 8)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(x + size * 0.2, y - size * 0.4, z + size * 0.3)
        glutSolidSphere(size * 0.6, 6, 6)
        glPopMatrix()
    
    glPopMatrix()

def showScreen():
    """Main rendering function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    setupCamera()
    
    # Draw 3D world
    draw_terrain()
    draw_clouds()
    if not is_first_person:
        draw_player()
    draw_bushes()  # Draw bushes around Pokemon
    draw_player_radius()  # Draw player detection radius
    draw_pokemon()  # Only visible Pokemon are drawn
    draw_pokeballs()
    draw_rocks()
    draw_opponent()  # Draw AI opponent
    draw_opponent_pokeballs()  # Draw opponent's pokeballs
    
    # Draw 2D HUD
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    if game_over:
        draw_game_over_screen()
    else:
        draw_hud()
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()

def main():
    """Main function"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Pokemon Catching Game - Simplified")
    
    glEnable(GL_DEPTH_TEST)
    # Enable basic lighting for better Pokemon visibility
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up lighting for better visibility
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 100, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
    
    glClearColor(0.5, 0.8, 1.0, 1.0)
    
    glutDisplayFunc(showScreen)
    glutReshapeFunc(reshapeListener)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMotionFunc(mouseMotionListener)
    glutPassiveMotionFunc(mouseMotionListener)
    glutIdleFunc(idle)
    
    print("=== Pokemon Catching Game - Simplified ===")
    print("Controls:")
    print("  WASD - Move player")
    print("  Arrow Keys - Rotate camera/player")
    print("  C - Switch between 1st/3rd person")
    print("  Space - Jump")
    print("  Left Click - Throw Pokeball")
    print("  R - Reset position")
    print("  H - Heal, J - Damage")
    print("  1-4 - Select Pokeball type")
    print("\nStarting game...")
    
    glutMainLoop()

if __name__ == "__main__":
    main()
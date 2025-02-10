import pygame
import math
import random
import sys

# Initialize pygame – this sets up all the modules in pygame.
pygame.init()

# ------------- SETUP -------------
# Define the dimensions of the window (width and height in pixels)
WIDTH, HEIGHT = 800, 600
# Create the display surface where we will draw everything.
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket Lander")

# Set up a clock to control the frame rate.
clock = pygame.time.Clock()

# ------------- CONSTANTS -------------
# Physics constants:
GRAVITY = 0.05       # Constant downward acceleration (pixels per frame^2)
THRUST = 0.15        # Acceleration added when the rocket's thruster is active

# Rotational physics:
ROTATIONAL_ACCELERATION = 0.2   # Acceleration applied to rotational velocity when turning
ROTATIONAL_DAMPING = 0.99       # Damping factor to slow down rotational velocity over time
SAFE_ROTATIONAL_SPEED = 2.0     # Maximum rotational velocity allowed for a safe landing

# Safe landing conditions for translation and angle:
SAFE_VERTICAL_SPEED = 2.5       # Maximum vertical speed allowed for a safe landing
SAFE_HORIZONTAL_SPEED = 2.0     # Maximum horizontal speed allowed for a safe landing
SAFE_ANGLE = 15                 # Maximum angle (in degrees from vertical) allowed for a safe landing

# Ground and landing pad settings:
GROUND_HEIGHT = 30              # Height of the ground from the bottom of the window
LANDING_PAD_WIDTH = 100         # Width of the landing pad (centered horizontally)

# The landing pad is drawn near the center of the ground.
landing_pad_x = (WIDTH - LANDING_PAD_WIDTH) / 2
landing_pad_y = HEIGHT - GROUND_HEIGHT

# ------------- ROCKET CLASS -------------
class Rocket:
    def __init__(self, pos, vel, angle):
        """
        Initialize the rocket with:
          pos: a tuple (x, y) for the starting position.
          vel: a tuple (vx, vy) for the starting velocity.
          angle: initial orientation in degrees (0 means the rocket is pointing upward).
        """
        self.x, self.y = pos           # Position (center of the rocket)
        self.vx, self.vy = vel         # Velocity components
        self.angle = angle             # Angle in degrees (0 = upward)
        self.rotational_velocity = 0   # Rotational velocity (degrees per frame)
        self.alive = True              # Whether the rocket is still active (flying)
        self.landed = False            # Set to True on a successful landing

    def update(self, keys):
        """
        Update the rocket's physics based on current velocity, gravity, and user input.
        """
        # Do nothing if the rocket is not active.
        if not self.alive:
            return

        # --- Rotational Control via Acceleration ---
        # Instead of directly adjusting the angle, apply rotational acceleration.
        if keys[pygame.K_LEFT]:
            self.rotational_velocity -= ROTATIONAL_ACCELERATION
        if keys[pygame.K_RIGHT]:
            self.rotational_velocity += ROTATIONAL_ACCELERATION

        # Update the angle based on the rotational velocity.
        self.angle += self.rotational_velocity
        # Apply damping to gradually reduce the rotational velocity.
        self.rotational_velocity *= ROTATIONAL_DAMPING

        # --- Thrust ---
        # When the up arrow is pressed, apply thrust in the direction the rocket is facing.
        if keys[pygame.K_UP]:
            # Convert the angle to radians.
            rad = math.radians(self.angle)
            # Calculate acceleration components (0° means upward).
            ax = math.sin(rad) * THRUST
            ay = -math.cos(rad) * THRUST
            self.vx += ax
            self.vy += ay

        # --- Gravity ---
        self.vy += GRAVITY

        # --- Update Position ---
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        """
        Draw the rocket on the given surface as a rotated triangle.
        """
        # Define the rocket's shape as a triangle.
        # Tip (nose) is at (0, -15) and the base corners at (-7, 10) and (7, 10).
        points = [(0, -15), (-7, 10), (7, 10)]
        # Rotate the points around the origin using the current angle.
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        rotated_points = []
        for x, y in points:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            rotated_points.append((self.x + rx, self.y + ry))
        # Draw the rocket as a filled red polygon.
        pygame.draw.polygon(surface, (255, 0, 0), rotated_points)

# ------------- SPAWN FUNCTION -------------
def spawn_rocket():
    """
    Spawn a rocket from one of three edges (left, right, or top).
    The rocket always spawns pointing straight up (angle = 0) and is given
    an initial velocity toward the center (landing pad).
    """
    # Randomly choose the spawn edge: 0 = left, 1 = right, 2 = top.
    side = random.choice([0, 1, 2])
    if side == 0:  # Left edge
        x = 0
        y = random.uniform(50, HEIGHT / 2)
    elif side == 1:  # Right edge
        x = WIDTH
        y = random.uniform(50, HEIGHT / 2)
    else:  # Top edge
        x = random.uniform(50, WIDTH - 50)
        y = 0

    # Determine the center of the landing pad.
    target_x = WIDTH / 2
    target_y = landing_pad_y

    # Calculate the vector from the spawn point to the landing pad.
    dx = target_x - x
    dy = target_y - y
    distance = math.hypot(dx, dy)
    if distance == 0:
        distance = 1

    # Choose a random speed (magnitude) between 1 and 3 pixels per frame.
    speed = random.uniform(1, 3)
    vx = (dx / distance) * speed
    vy = (dy / distance) * speed

    # Spawn the rocket with angle = 0 (pointing straight up).
    angle = 0

    return Rocket((x, y), (vx, vy), angle)

# Create our first rocket.
rocket = spawn_rocket()

# ------------- FONT SETUP -------------
font = pygame.font.Font(None, 24)

# ------------- MAIN GAME LOOP -------------
running = True       # Main loop flag.
game_over = False    # Flag indicating the rocket has landed/crashed.
message = ""         # End-of-game message.

while running:
    # Limit the frame rate to 60 frames per second.
    dt = clock.tick(60)

    # Handle events (e.g., closing the window).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the current state of the keyboard.
    keys = pygame.key.get_pressed()

    # Check for game reset when game is over.
    if game_over and keys[pygame.K_SPACE]:
        rocket = spawn_rocket()
        game_over = False
        message = ""

    # Update the rocket's physics if the game is not over.
    if not game_over:
        rocket.update(keys)

    # ------------- COLLISION CHECKS -------------
    # Check if the rocket has touched the ground.
    if rocket.alive and rocket.y >= landing_pad_y - 10:
        if landing_pad_x <= rocket.x <= landing_pad_x + LANDING_PAD_WIDTH:
            # Check all safe landing conditions including rotational velocity.
            if (abs(rocket.vy) <= SAFE_VERTICAL_SPEED and
                abs(rocket.vx) <= SAFE_HORIZONTAL_SPEED and
                abs(rocket.angle) <= SAFE_ANGLE and
                abs(rocket.rotational_velocity) <= SAFE_ROTATIONAL_SPEED):
                message = "Landed Successfully! Press SPACE to reset."
                rocket.landed = True
            else:
                message = "Crashed! Press SPACE to reset."
        else:
            message = "Crashed! Press SPACE to reset."
        rocket.alive = False
        game_over = True

    # Check if the rocket has flown off-screen.
    if rocket.alive:
        if rocket.x < -50 or rocket.x > WIDTH + 50 or rocket.y < -50 or rocket.y > HEIGHT + 50:
            message = "Crashed! (Out of bounds) Press SPACE to reset."
            rocket.alive = False
            game_over = True

    # ------------- DRAWING -------------
    # Clear the screen.
    screen.fill((0, 0, 0))

    # Draw the ground.
    pygame.draw.rect(screen, (50, 205, 50), (0, landing_pad_y, WIDTH, GROUND_HEIGHT))
    # Draw the landing pad.
    pygame.draw.rect(screen, (255, 255, 255), (landing_pad_x, landing_pad_y - 5, LANDING_PAD_WIDTH, 5))

    # Draw the rocket.
    rocket.draw(screen)

    # --- Draw Debug Text with Status Circles ---
    # Define starting coordinates and spacing.
    debug_start_x = 10
    debug_start_y = 10
    debug_line_spacing = 25
    # Create a list of debug items: each is a tuple of (label, value, safe_flag, special_flag)
    # For "Y Position", the special flag is "ypos" (safe if near the ground -> green; otherwise yellow)
    debug_items = [
        ("Horizontal Velocity", f"{rocket.vx:.2f}", abs(rocket.vx) <= SAFE_HORIZONTAL_SPEED, None),
        ("Vertical Velocity", f"{rocket.vy:.2f}", abs(rocket.vy) <= SAFE_VERTICAL_SPEED, None),
        ("Angle", f"{rocket.angle:.2f}", abs(rocket.angle) <= SAFE_ANGLE, None),
        ("Rotational Velocity", f"{rocket.rotational_velocity:.2f}", abs(rocket.rotational_velocity) <= SAFE_ROTATIONAL_SPEED, None),
        ("X Position", f"{rocket.x:.2f}", landing_pad_x <= rocket.x <= landing_pad_x + LANDING_PAD_WIDTH, None),
        ("Y Position", f"{rocket.y:.2f}", rocket.y >= landing_pad_y - 20, "ypos")
    ]

    for i, (label, value, is_safe, special) in enumerate(debug_items):
        # Determine the circle color.
        if special == "ypos":
            # For Y position, use green if close to the ground; yellow otherwise.
            circle_color = (0, 255, 0) if is_safe else (255, 255, 0)
        else:
            circle_color = (0, 255, 0) if is_safe else (255, 0, 0)
        # Draw a small circle (radius 5).
        circle_center = (debug_start_x, debug_start_y + i * debug_line_spacing + 10)
        pygame.draw.circle(screen, circle_color, circle_center, 5)
        # Prepare and draw the text.
        debug_text = font.render(f"{label}: {value}", True, (255, 255, 255))
        screen.blit(debug_text, (debug_start_x + 15, debug_start_y + i * debug_line_spacing))

    # If the game is over, show the message in the center.
    if game_over:
        msg_text = font.render(message, True, (255, 255, 0))
        text_rect = msg_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(msg_text, text_rect)

    # Update the display.
    pygame.display.flip()

# Quit pygame and exit.
pygame.quit()
sys.exit()

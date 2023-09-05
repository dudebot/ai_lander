import pygame
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
ROCKET_SIZE = 20
GROUND_HEIGHT = 50
FPS = 60

# Physics constants
GRAVITY = 0.03
SPEED_THRESHOLD = 2  # Speed threshold for a successful landing (adjust as needed)
ANGLE_THRESHOLD = 10  # Absolute angle threshold for a successful landing (adjust as needed)

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)


# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket Landing Simulator")
font = pygame.font.Font(None, 36)

# Rocket attributes
rocket_x = WIDTH // 2
rocket_y = 50
rocket_angle = 0
rocket_velocity_x = 0
rocket_velocity_y = 0
angular_velocity = 0
fuel = 100
fuel_rate = 0.5

# Define the rocket shape and size
ROCKET_WIDTH = 20
ROCKET_HEIGHT = 40

# Define the leg size
LEG_LENGTH = 10
LEG_WIDTH = 41

# Landing status
landing_status = None  # None: in progress, "landed": successfully landed, "crashed": crashed

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rocket_angle += 1
    if keys[pygame.K_RIGHT]:
        rocket_angle -= 1
    if keys[pygame.K_UP] and fuel > 0:
        # Calculate the change in velocity based on rocket angle
        angle_rad = math.radians(rocket_angle)
        rocket_velocity_y += -0.1 * math.cos(angle_rad)
        rocket_velocity_x += -0.1 * math.sin(angle_rad)
        fuel -= fuel_rate

    if landing_status is None:
        # Apply gravity
        rocket_velocity_y += GRAVITY

        # Update rocket physics
        rocket_x += rocket_velocity_x
        rocket_y += rocket_velocity_y
        rocket_angle += angular_velocity

        # Check for collision with the ground
        if rocket_y + ROCKET_SIZE >= HEIGHT - GROUND_HEIGHT:
            if math.sqrt(rocket_velocity_y*rocket_velocity_y+rocket_velocity_x*rocket_velocity_x) > SPEED_THRESHOLD:
                landing_status = "crashed (speed)"
            elif abs(rocket_angle) > ANGLE_THRESHOLD:
                landing_status = "crashed (angle)"
            else:
                landing_status = "landed!"

        # Clear the screen
        screen.fill(WHITE)

        # Draw the ground
        pygame.draw.rect(screen, GREEN, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

        # Rotate and draw the rocket
        rocket_image = pygame.Surface((ROCKET_WIDTH, ROCKET_HEIGHT), pygame.SRCALPHA)
        rocket_rect = rocket_image.get_rect()
        rocket_image.fill(RED)
        pygame.draw.polygon(rocket_image, ORANGE, [(ROCKET_WIDTH // 2, ROCKET_HEIGHT), (ROCKET_WIDTH // 2 - LEG_WIDTH // 2, ROCKET_HEIGHT + LEG_LENGTH), (ROCKET_WIDTH // 2 + LEG_WIDTH // 2, ROCKET_HEIGHT + LEG_LENGTH)])
        rotated_rocket = pygame.transform.rotate(rocket_image, rocket_angle)
        rotated_rect = rotated_rocket.get_rect(center=(rocket_x, rocket_y))
        screen.blit(rotated_rocket, rotated_rect)

        # draw the speed and angle on the top right corner
        text = font.render(f"Speed: {round(math.sqrt(rocket_velocity_y*rocket_velocity_y+rocket_velocity_x*rocket_velocity_x), 2)} Angle: {round(rocket_angle, 2)} Fuel: {round(fuel)}", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH - 200, 50))
        screen.blit(text, text_rect)

    # Display landing status
    else:
        font = pygame.font.Font(None, 36)
        text = font.render(landing_status.capitalize() + "!", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            landing_status = None
            rocket_x = WIDTH // 2
            rocket_y = 50
            rocket_velocity_x = 0
            rocket_velocity_y = 0
            angular_velocity = 0
            rocket_angle = 0
            fuel = 100

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

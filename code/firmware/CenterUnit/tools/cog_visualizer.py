import pygame
import serial

PORT = "COM6"   # change this
BAUD = 921600

ser = serial.Serial(PORT, BAUD, timeout=0.01)
ser.reset_input_buffer()

pygame.init()

WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CoG Visualizer")

center_x = WIDTH // 2
center_y = HEIGHT // 2

scale = 8.0

clock = pygame.time.Clock()

pitch = 0.0
roll = 0.0

# smoothed dot position
dot_x = float(center_x)
dot_y = float(center_y)
visual_alpha = 0.22   # lower = steadier, higher = faster

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    while ser.in_waiting:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            parts = line.split(",")

            if len(parts) == 2:
                pitch = float(parts[0])
                roll = float(parts[1])
        except:
            pass

    target_x = center_x + roll * scale
    target_y = center_y - pitch * scale

    # smooth visual motion
    dot_x = visual_alpha * target_x + (1.0 - visual_alpha) * dot_x
    dot_y = visual_alpha * target_y + (1.0 - visual_alpha) * dot_y

    screen.fill((30, 30, 30))

    pygame.draw.rect(screen, (200, 200, 200), (50, 50, 500, 500), 2)
    pygame.draw.circle(screen, (120, 120, 120), (center_x, center_y), 6)
    pygame.draw.circle(screen, (255, 80, 80), (int(dot_x), int(dot_y)), 12)

    pygame.display.flip()
    clock.tick(240)

pygame.quit()
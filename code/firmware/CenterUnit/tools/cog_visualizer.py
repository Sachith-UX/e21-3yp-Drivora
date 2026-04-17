import pygame
import serial

# ================= CONFIG =================
PORT = "COM6"   # change this
BAUD = 921600

ser = serial.Serial(PORT, BAUD, timeout=0.01)
ser.reset_input_buffer()

# ================= UI SETUP =================
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle Lean Monitor")

font = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()

# ================= STATE =================
roll = 0.0
pitch = 0.0
confidence = 1.0
risk = 0.0
level = 0

center_x = WIDTH // 2
center_y = HEIGHT // 2
scale = 6

dot_x = center_x
dot_y = center_y

# ================= HELPERS =================
def risk_color(level):
    if level == 0: return (0, 200, 0)
    if level == 1: return (255, 200, 0)
    if level == 2: return (255, 120, 0)
    return (255, 0, 0)

def risk_text(level):
    return ["SAFE", "CAUTION", "HIGH", "CRITICAL"][int(level)]

# ================= LOOP =================
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ===== READ SERIAL =====
    while ser.in_waiting:
        try:
            line = ser.readline().decode().strip()
            parts = line.split(",")

            if len(parts) == 6:
                roll = float(parts[0])
                pitch = float(parts[1])
                confidence = float(parts[2])
                risk = float(parts[3])
                level = int(parts[4])
        except:
            pass

    # ===== UPDATE DOT =====
    target_x = center_x + roll * scale
    target_y = center_y - pitch * scale

    # smooth UI movement
    dot_x = 0.4 * target_x + 0.6 * dot_x
    dot_y = 0.4 * target_y + 0.6 * dot_y

    # ===== DRAW =====
    screen.fill((25, 25, 30))

    # cross lines
    pygame.draw.line(screen, (80, 80, 80), (center_x, 0), (center_x, HEIGHT))
    pygame.draw.line(screen, (80, 80, 80), (0, center_y), (WIDTH, center_y))

    # center point
    pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), 5)

    # lean dot
    color = risk_color(level)
    pygame.draw.circle(screen, color, (int(dot_x), int(dot_y)), 12)

    # ===== TEXT =====
    screen.blit(font.render(f"Roll: {roll:.2f} deg", True, (220,220,220)), (20,20))
    screen.blit(font.render(f"Pitch: {pitch:.2f} deg", True, (220,220,220)), (20,50))

    screen.blit(font.render(f"Risk: {risk_text(level)}", True, color), (20,100))

    # ===== CONFIDENCE BAR =====
    bar_w = 200
    bar_h = 20
    bar_x = 20
    bar_y = 150

    pygame.draw.rect(screen, (80,80,80), (bar_x, bar_y, bar_w, bar_h))
    fill_w = int(bar_w * confidence)

    conf_color = (0,200,0) if confidence > 0.7 else (255,180,0) if confidence > 0.4 else (255,0,0)
    pygame.draw.rect(screen, conf_color, (bar_x, bar_y, fill_w, bar_h))

    screen.blit(font.render("Confidence", True, (220,220,220)), (20, 180))

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
ser.close()
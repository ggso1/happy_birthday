import math
import random
import sys
import webbrowser
import pygame 

WIDTH, HEIGHT = 1280, 720  # Зменшено для зручності екранів (можна повернути 2000, 1200)
BACKGROUND_COLOR = (0, 0, 0)
FPS = 60
SCALE = 16

WORDS = ["happy birthday", "Happy Birthday", "HAPPY BIRTHDAY"]
CENTER_TEXT = " Love You "
COLORS = [
    (70, 130, 180),
    (30, 144, 255),  
    (0, 191, 255),  
    (100, 149, 237), 
    (65, 105, 225)
]

# Налаштування перенаправлення на сайт
TARGET_URL = "https://www.python.org"  # Вкажіть ваше посилання
AUTO_OPEN_URL_AFTER_FRAMES = 500       # Через скільки кадрів після старту відкрити сайт


class Particle:
    __slots__ = ('x', 'y', 'order', 'kind', 'word', 'color', 'alpha', 'flicker', 'font', 'delay', 'size_mult')
    
    def __init__(self, x, y, order, kind):
        self.x = x
        self.y = y
        self.order = order
        self.kind = kind
        self.word = random.choice(WORDS)
        self.color = random.choice(COLORS)
        self.alpha = 0
        self.flicker = random.uniform(0, math.pi * 2)
        self.font = None
        self.delay = 0
        self.size_mult = random.uniform(0.85, 1.15)


def heart_xy(t):
    x = 16 * (math.sin(t) ** 3)
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return x, -y

def to_screen(x, y):
    return x * SCALE + WIDTH / 2, y * SCALE + HEIGHT / 2 

def build_outline_particles(n_outline, min_gap=24):
    particles = []
    placed = []
    for i in range(n_outline):
        t = (i / n_outline) * 2 * math.pi
        bx, by = heart_xy(t)
        sx, sy = to_screen(bx, by)
        if any(math.hypot(sx - px, sy - py) < min_gap for (px, py) in placed):
            continue
        placed.append((sx, sy))
        particles.append(Particle(sx, sy, i, "outline"))
    return particles

def build_fill_particles(n_fill, min_gap=32):
    particles = []
    placed = []
    attempts = 0
    max_attempts = n_fill * 80
    
    while len(particles) < n_fill and attempts < max_attempts:
        attempts += 1
        t = random.uniform(0, 2 * math.pi)
        r = random.uniform(0.0, 0.86)
        bx, by = heart_xy(t)
        px, py = bx * r, by * r
        sx, sy = to_screen(px, py)
        
        if any(math.hypot(sx - qx, sy - qy) < min_gap for (qx, qy) in placed):
            continue
            
        placed.append((sx, sy))
        particles.append(Particle(sx, sy, random.randint(0, 320), "fill"))
    
    return particles

def draw_glow_text(glow_layer, screen_layer, font, word, color, x, y, alpha, size_mult=1.0):
    if alpha <= 0:
        return
    
    if size_mult != 1.0:
        scaled_font = pygame.font.SysFont("arial", int(font.get_height() * size_mult), bold=True)
        txt = scaled_font.render(word, True, color)
    else:
        txt = font.render(word, True, color)
    
    txt.set_alpha(alpha)
    txt_rect = txt.get_rect(center=(x, y))
    
    if alpha > 10:
        glow_big = pygame.transform.smoothscale(txt, (int(txt.get_width() * 2.4), int(txt.get_height() * 2.4)))
        glow_big.set_alpha(max(0, alpha // 7))
        glow_rect = glow_big.get_rect(center=(x, y))
        glow_layer.blit(glow_big, glow_rect)
        
        glow_small = pygame.transform.smoothscale(txt, (int(txt.get_width() * 1.6), int(txt.get_height() * 1.6)))
        glow_small.set_alpha(max(0, alpha // 3))
        glow_rect = glow_small.get_rect(center=(x, y))
        glow_layer.blit(glow_small, glow_rect)
    
    screen_layer.blit(txt, txt_rect)


# Малювання модального вікна "Вірусу"
def draw_popup(screen, font_title, font_body, font_btn, btn_rect, is_hovered):
    # Темний фон із розмиттям/затемненням
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # Картка вікна
    card_rect = pygame.Rect(0, 0, 440, 260)
    card_rect.center = (WIDTH // 2, HEIGHT // 2)
    
    pygame.draw.rect(screen, (18, 18, 26), card_rect, border_radius=16)
    pygame.draw.rect(screen, (255, 77, 109), card_rect, width=2, border_radius=16)

    # Заголовок
    title_surf = font_title.render("⚠️ Виявлено загрозу!", True, (255, 255, 255))
    screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, card_rect.top + 45)))

    # Текст
    text1 = font_body.render("На вашому пристрої виявлено любовний вірус.", True, (160, 160, 175))
    text2 = font_body.render("Натисніть кнопку нижче для активації.", True, (160, 160, 175))
    screen.blit(text1, text1.get_rect(center=(WIDTH // 2, card_rect.top + 95)))
    screen.blit(text2, text2.get_rect(center=(WIDTH // 2, card_rect.top + 120)))

    # Кнопка
    btn_color = (255, 100, 130) if is_hovered else (255, 77, 109)
    pygame.draw.rect(screen, btn_color, btn_rect, border_radius=25)
    
    btn_text = font_btn.render("Підтвердити вірус 🚀", True, (255, 255, 255))
    screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Увага! Системне повідомлення")
    clock = pygame.time.Clock()
    
    font_outline = pygame.font.SysFont("arial", 18, bold=True)
    font_fill = pygame.font.SysFont("arial", 15, bold=True)
    font_center = pygame.font.SysFont("georgia", 48, bold=True)
    
    font_popup_title = pygame.font.SysFont("arial", 24, bold=True)
    font_popup_body = pygame.font.SysFont("arial", 15)
    font_popup_btn = pygame.font.SysFont("arial", 18, bold=True)

    btn_rect = pygame.Rect(0, 0, 280, 50)
    btn_rect.center = (WIDTH // 2, HEIGHT // 2 + 65)

    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BACKGROUND_COLOR)
    
    outline = build_outline_particles(n_outline=160)
    fill = build_fill_particles(n_fill=130)
    
    outline_span = max(p.order for p in outline) if outline else 0
    frames_per_step = 1.6
    fill_start_frame = int(outline_span * frames_per_step) + 30
    
    for p in fill:
        p.delay = fill_start_frame + p.order
    for p in outline:
        p.delay = int(p.order * frames_per_step)
    
    particles = outline + fill
    for p in particles:
        p.font = font_outline if p.kind == "outline" else font_fill
    
    running = True
    virus_confirmed = False  # Стан: чи натиснута кнопка
    url_opened = False
    frame = 0

    glow_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    text_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = btn_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            
            # Обробка кліку на кнопку "Підтвердити"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not virus_confirmed and is_hovered:
                    virus_confirmed = True
                    # Запуск музики ТІЛЬКИ після підтвердження
                    try:
                        pygame.mixer.music.load("gay_porn.mp3")
                        pygame.mixer.music.play()
                    except Exception as e:
                        print("Не вдалося завантажити/відтворити аудіо:", e)

        screen.blit(background, (0, 0))

        if not virus_confirmed:
            # Спочатку показуємо тільки модальне вікно підтвердження
            draw_popup(screen, font_popup_title, font_popup_body, font_popup_btn, btn_rect, is_hovered)
        else:
            # Після підтвердження запускаємо анімацію
            glow_layer.fill((0, 0, 0, 0))
            text_layer.fill((0, 0, 0, 0))
            frame += 1
            
            for p in particles:
                if frame > p.delay and p.alpha < 255:
                    p.alpha = min(255, p.alpha + 14 + random.randint(0, 4))
                
                if p.alpha >= 255:
                    flick = 0.75 + 0.25 * math.sin(frame * 0.04 + p.flicker)
                else:
                    flick = 1.0
                
                alpha = int(p.alpha * flick)
                if alpha <= 0:
                    continue
                
                draw_glow_text(glow_layer, text_layer, p.font, p.word, p.color, 
                              p.x, p.y, alpha, p.size_mult)
            
            screen.blit(glow_layer, (0, 0))
            screen.blit(text_layer, (0, 0))
            
            center_start = fill_start_frame + 200
            if frame > center_start:
                progress = min(1.0, (frame - center_start) / 60)
                center_alpha = int(255 * (1 - math.exp(-progress * 8)))
                
                pulse = 1.0 + 0.025 * math.sin(frame * 0.05)
                center_surf = font_center.render(CENTER_TEXT, True, (255, 250, 245))
                
                new_width = int(center_surf.get_width() * pulse)
                new_height = int(center_surf.get_height() * pulse)
                if new_width > 0 and new_height > 0:
                    center_surf = pygame.transform.smoothscale(center_surf, (new_width, new_height))
                
                center_surf.set_alpha(center_alpha)
                
                if center_alpha > 10:
                    glow_center = pygame.transform.smoothscale(
                        center_surf, (int(center_surf.get_width() * 1.4), int(center_surf.get_height() * 1.4))
                    )
                    glow_center.set_alpha(center_alpha // 5)
                    glow_rect = glow_center.get_rect(center=(WIDTH/2, HEIGHT/2))
                    screen.blit(glow_center, glow_rect)
                
                text_rect = center_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
                screen.blit(center_surf, text_rect)

            # (Опціонально) Відкриття сайту через декілька секунд анімації
            if frame >= AUTO_OPEN_URL_AFTER_FRAMES and not url_opened:
                webbrowser.open(TARGET_URL)
                url_opened = True

        pygame.display.flip()     
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("OCURRIO UN ERROR:", e)
        import traceback
        traceback.print_exc()
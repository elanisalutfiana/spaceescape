import pygame
import random
import os
import math

pygame.init()

WIDTH = 600
HEIGHT = 700

FPS = 60

HIGHSCORE_FILE = "highscore.txt"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 200, 255)
CYAN = (0, 255, 255)
PURPLE = (200, 0, 255)
ORANGE = (255, 100, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Escape: Ultimate Edition")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Impact", 72)
font_med = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 24)
font_tiny = pygame.font.SysFont("Arial", 18, bold=True)


def load_img(name, scale=None):
    path = os.path.join("assets", name)
    if os.path.exists(path):

        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    else:
        surface = pygame.Surface(scale if scale else (50, 50))
        surface.fill(RED)
        return surface

bg_img = load_img("background.png", (WIDTH, HEIGHT))
ship_img = load_img("ship.png", (60, 60))
asteroid_img = load_img("asteroid.png", (50, 50))
laser_img = load_img("laser.png", (10, 40))
coin_img = load_img("coin.png", (35, 35))
shield_img = load_img("shield.png", (45, 45))

# fungsi buat simpan & ambil highscore

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

# KELAS OBJEK

class Star:

    def __init__(self, speed_mult):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(1.0, 3.0) * speed_mult
        self.size = random.randint(1, 4)
        self.color = (random.randint(150, 255), random.randint(150, 255), 255)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surf, offset_x=0, offset_y=0):
        pygame.draw.circle(surf, self.color, (int(self.x + offset_x), int(self.y + offset_y)), self.size)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ship_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 8
        self.health = 100
        self.shield_active = False
        self.shield_time = 0
        self.score = 0
        self.last_shot = pygame.time.get_ticks() # waktu terakhir menembak
        self.shoot_delay = 200 # delay biar ga spam tembakan
        self.tilt = 0 # buat efek miring pas belok

    def update(self):
        keys = pygame.key.get_pressed()
        self.tilt = 0
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.tilt = 15 # Miring ke kanan (visual)
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.tilt = -15 # Miring ke kiri (visual)
        
        # biar pesawat keliatan miring pas gerak kiri kanan
        if self.tilt != 0:
            self.image = pygame.transform.rotate(ship_img, self.tilt)
        else:
            self.image = ship_img
        self.rect = self.image.get_rect(center=self.rect.center)

        # kalo tekan spasi, player nembak
        if keys[pygame.K_SPACE]:
            self.shoot()

            # ngecek shield masih aktif atau udah habis (5 detik)        if self.shield_active:
            if pygame.time.get_ticks() - self.shield_time > 5000:
                self.shield_active = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            laser = Laser(self.rect.centerx, self.rect.top)
            all_sprites.add(laser)
            lasers.add(laser)

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        # ukuran asteroid random
        size_val = random.randint(35, 75)
        self.image = pygame.transform.scale(asteroid_img, (size_val, size_val))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -100)
        # makin tinggi level makin cepet jatuh
        self.speedy = random.randrange(3, 7) + (level * 0.5)
        self.speedx = random.randrange(-2, 3) # gerak dikit ke samping biar ga lurus doang
        self.rot = 0 # buat efek muter
        self.rot_speed = random.randrange(-6, 7)
        self.original_image = self.image

    def update(self):
        self.rot = (self.rot + self.rot_speed) % 360
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.rot)
        self.rect = self.image.get_rect(center=old_center)
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # kalau lewat bawah, spawn lagi dari atas
        if self.rect.top > HEIGHT + 20:
            self.rect.y = random.randrange(-150, -50)
            self.rect.x = random.randrange(WIDTH - self.rect.width)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = laser_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -14 # laser gerak ke atas

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Powerup(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.image = coin_img if type == "coin" else shield_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 5 # kecepatan jatuh item

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class VFXParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size_range=(2, 6)):
        super().__init__()
        size = random.randint(*size_range)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=(x, y))

        # partikel nyebar random biar efek ledakan
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.alpha = 255
        self.fade_speed = random.randint(5, 12)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color, size=24):
        super().__init__()
        self.image = pygame.font.SysFont("Arial", size, bold=True).render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = -2
        self.timer = 40
    def update(self):
        self.rect.y += self.vy
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

class Game:

    def __init__(self):
        self.highscore = load_highscore()
        self.stars_far = [Star(0.5) for _ in range(30)]
        self.stars_near = [Star(1.2) for _ in range(15)]
        self.shake_time = 0
        self.shake_intensity = 0
        self.combo = 0
        self.last_kill_time = 0
        self.score_display = 0

        self.score_scale = 1.0
        self.combo_scale = 1.0

    def start_shake(self, duration, intensity):
        self.shake_time = duration
        self.shake_intensity = intensity

    def update_vfx(self):
        if self.score_scale > 1.0:
            self.score_scale -= 0.05
        if self.combo_scale > 1.0:
            self.combo_scale -= 0.08

        if self.shake_time > 0:
            self.shake_time -= 1

    def spawn_explosion(self, x, y, color, count=15):
        for _ in range(count):
            all_sprites.add(VFXParticle(x, y, color))

    def draw_hud(self, surf, player, level, start_time):
        now = pygame.time.get_ticks()

        ui_bar = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
        ui_bar.fill((0, 0, 0, 150))
        surf.blit(ui_bar, (0, 0))

        bar_width = 150
        bar_height = 15
        x, y = 20, 25
        pygame.draw.rect(surf, (50, 50, 50), (x, y, bar_width, bar_height), border_radius=5)
        health_pct = max(0, player.health / 100)

        fill_color = GREEN if health_pct > 0.4 else (ORANGE if health_pct > 0.2 else RED)
        if health_pct > 0:
            pygame.draw.rect(surf, fill_color, (x + 2, y + 2, (bar_width - 4) * health_pct, bar_height - 4), border_radius=3)
        surf.blit(font_tiny.render("HEALTH", True, WHITE), (x, y - 18))

        track_w = 180
        track_h = 6
        tx = WIDTH // 2 - track_w // 2 + 20 
        ty = 35
        # Menghitung durasi level (setiap 10 detik naik level)
        progress = ((now - start_time) % 10000) / 10000
        pygame.draw.rect(surf, (60, 60, 60), (tx, ty, track_w, track_h), border_radius=3)
        pygame.draw.rect(surf, CYAN, (tx, ty, track_w * progress, track_h), border_radius=3)
        
        # Menampilkan angka level saat ini dan level berikutnya
        draw_text(surf, str(level), 20, tx - 12, ty - 8, WHITE, font_small)
        draw_text(surf, str(level + 1), 20, tx + track_w + 12, ty - 8, YELLOW, font_small)
        draw_text(surf, "LEVEL", 14, tx + track_w//2, ty - 18, CYAN, font_tiny)

        # 4. Score
        if self.score_display < player.score:
            # biar skor naiknya ga langsung lompat
            diff = player.score - self.score_display
            self.score_display += max(1, diff // 10)
        
        score_txt = font_med.render(f"{self.score_display:05}", True, CYAN)
        if self.score_scale > 1.0:
            # Memperbesar teks jika skala di atas 1.0 (saat kena asteroid)
            sz = score_txt.get_size()
            score_txt = pygame.transform.scale(score_txt, (int(sz[0]*self.score_scale), int(sz[1]*self.score_scale)))
        
        score_rect = score_txt.get_rect(topright=(WIDTH - 20, 10))
        surf.blit(score_txt, score_rect)
        
        # Skor Tertinggi
        best_txt = font_tiny.render(f"BEST: {self.highscore:05}", True, YELLOW)
        best_rect = best_txt.get_rect(topright=(WIDTH - 20, 50))
        surf.blit(best_txt, best_rect)

        # 5. Combo
        if self.combo > 1:
            combo_txt = font_med.render(f"X{self.combo} COMBO", True, ORANGE)
            if self.combo_scale > 1.0:
                sz = combo_txt.get_size()
                combo_txt = pygame.transform.scale(combo_txt, (int(sz[0]*self.combo_scale), int(sz[1]*self.combo_scale)))
            
            combo_rect = combo_txt.get_rect(center=(WIDTH // 2, 110))
            surf.blit(combo_txt, combo_rect)

    def main_menu(self):
        menu_running = True
        pulse_time = 0

        original_speeds_far = [s.speed for s in self.stars_far]
        original_speeds_near = [s.speed for s in self.stars_near]
        for s in self.stars_far: s.speed *= 5
        for s in self.stars_near: s.speed *= 8
        
        while menu_running:
            clock.tick(FPS)
            pulse_time += 0.05
            
            screen.blit(bg_img, (0, 0))
            for s in self.stars_far: s.update(); s.draw(screen)
            for s in self.stars_near: s.update(); s.draw(screen)
            
            # gambar judul game
            title_text = "SPACE ESCAPE"
            title_txt = font_big.render(title_text, True, WHITE)
            title_rect = title_txt.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            
            # dikasih shadow biar keliatan lebih jelas
            shadow_txt = font_big.render(title_text, True, (0, 0, 0))
            screen.blit(shadow_txt, (title_rect.x + 5, title_rect.y + 5))
            screen.blit(title_txt, title_rect)
            
            draw_text(screen, "ULTIMATE EDITION", 24, WIDTH // 2, HEIGHT // 4 + 40, CYAN, font_small)
            
            # bagian intruksi
            inst_y_start = HEIGHT * 2 // 3 - 20
            
            # teks kedip biar lebih hidup
            alpha_blink = int(160 + math.sin(pulse_time * 2) * 95)
            start_txt = font_small.render("PRESS ANY KEY TO START", True, (alpha_blink, alpha_blink, alpha_blink))
            start_rect = start_txt.get_rect(midbottom=(WIDTH // 2, inst_y_start - 20))
            screen.blit(start_txt, start_rect)
            
            draw_text(screen, "KONTROL GAME", 18, WIDTH // 2, inst_y_start, CYAN, font_tiny)
            
            # posisi tulisan kontrol
            key_x = WIDTH // 2 - 25
            desc_x = WIDTH // 2 - 10
            line_skip = 32 
            first_row_y = inst_y_start + 25
            
            # list tombol kontrol
            t1 = font_small.render("↑ ↓ ← →", True, WHITE)
            screen.blit(t1, t1.get_rect(right=key_x, top=first_row_y))
            draw_text(screen, ":  Kontrol Pesawat", 22, desc_x, first_row_y, WHITE, font_small, align="topleft")
            
            t2 = font_small.render("SPACE", True, WHITE)
            screen.blit(t2, t2.get_rect(right=key_x, top=first_row_y + line_skip))
            draw_text(screen, ":  Tembak", 22, desc_x, first_row_y + line_skip, WHITE, font_small, align="topleft")
            
            t3 = font_small.render("P", True, YELLOW)
            screen.blit(t3, t3.get_rect(right=key_x, top=first_row_y + line_skip * 2))
            draw_text(screen, ":  Jeda", 22, desc_x, first_row_y + line_skip * 2, YELLOW, font_small, align="topleft")

            pygame.display.flip()

            # nunggu user pencet tombol buat mulai
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    menu_running = False

        # balikin speed bintang ke normal
        for i, s in enumerate(self.stars_far): s.speed = original_speeds_far[i]
        for i, s in enumerate(self.stars_near): s.speed = original_speeds_near[i]

    def game_over(self, player):
        # update skor tertinggi jika pemain memecahkan rekor
        if player.score > self.highscore:
            self.highscore = player.score
            save_highscore(self.highscore)
        
        waiting = True
        while waiting:
            clock.tick(FPS)
            screen.blit(bg_img, (0, 0))
            draw_text(screen, "MISSION FAILED", 72, WIDTH // 2, HEIGHT // 4, RED, font_big)
            draw_text(screen, f"YOUR SCORE: {player.score}", 36, WIDTH // 2, HEIGHT // 2, WHITE, font_med)
            draw_text(screen, f"HIGH SCORE: {self.highscore}", 24, WIDTH // 2, HEIGHT // 2 + 50, YELLOW, font_small)
            draw_text(screen, "PRESS ANY KEY TO RESTART", 24, WIDTH // 2, HEIGHT * 3 // 4, GREEN, font_small)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

def draw_text(surf, text, size, x, y, color, font_type, align="midtop"):
    text_surf = font_type.render(text, True, color)
    if align == "midtop":
        rect = text_surf.get_rect(midtop=(x, y))
    else:
        rect = text_surf.get_rect(topleft=(x, y))
    surf.blit(text_surf, rect)

# GLOBAL GAME OBJECTS
game = Game()
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
lasers = pygame.sprite.Group()
powerups = pygame.sprite.Group()
floating_texts = pygame.sprite.Group()

# MAIN LOOP

# LOOP UTAMA GAME

main_running = True
while main_running:
    # tampilkan menu utama dulu sebelum game mulai
    game.main_menu()
    
    # reset semua object biar fresh
    all_sprites.empty()
    asteroids.empty()
    lasers.empty()
    powerups.empty()
    floating_texts.empty()
    
    # buat player
    player = Player()
    all_sprites.add(player)
    
    # spawn asteroid awal
    for _ in range(8):
        a = Asteroid(1)
        all_sprites.add(a)
        asteroids.add(a)

    level = 1
    start_time = pygame.time.get_ticks()
    bg_y = 0
    game_active = True
    paused = False

    # loop utama game
    while game_active:
        clock.tick(FPS) # biar fps stabil 60
        now = pygame.time.get_ticks()

        # handle input keyboard
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_active = False
                main_running = False
            if event.type == pygame.KEYDOWN:
                # Menekan 'P' atau 'ESC' untuk jeda (Pause)
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    paused = not paused

        if paused:
            # kalau pause, stop update dulu
            draw_text(screen, "PAUSED", 64, WIDTH // 2, HEIGHT // 2 - 50, WHITE, font_big)
            pygame.display.flip()
            continue

        # sistem level naik otomatis tiap 10 detik
        level_sekarang = (now - start_time) // 10000 + 1
        if level_sekarang > level:
            level = level_sekarang

        # update semua object
        all_sprites.update()
        floating_texts.update()
        game.update_vfx() # update efek visual (shake, zoom, dll)
        for s in game.stars_far: s.update()
        for s in game.stars_near: s.update()

        # spawn powerup random
        if random.random() < 0.005:
            p_type = "coin" if random.random() < 0.8 else "shield"
            p = Powerup(p_type)
            all_sprites.add(p)
            powerups.add(p)

        # reset combo kalo lama ga nge kill selama 2 detik
        if now - game.last_kill_time > 2000:
            game.combo = 0

        # kalo llaser kna asteroid
        hits = pygame.sprite.groupcollide(asteroids, lasers, True, True)
        if hits:
            game.start_shake(10, 5) # Getaran layar kecil saat meledak
            for hit in hits:
                game.combo += 1
                game.last_kill_time = now
                # poin dikalikan dengan combo (sistem Hadiah / reward)
                points = 10 * game.combo
                player.score += points
                game.score_scale = 1.3 # efek zoom pada angka skor
                game.combo_scale = 1.6 # efek zoom pada angka combo
                game.spawn_explosion(hit.rect.centerx, hit.rect.centery, YELLOW)
                all_sprites.add(FloatingText(hit.rect.centerx, hit.rect.centery, f"+{points}", CYAN))
                
                # memunculkan asteroid baru sebagai pengganti yang hancur
                a = Asteroid(level)
                all_sprites.add(a)
                asteroids.add(a)

        # kalo player kena asteroid
        hits = pygame.sprite.spritecollide(player, asteroids, True)
        if hits:
            game.start_shake(20, 12) # Getaran layar kuat saat pesawat tertabrak
            for hit in hits:
                if not player.shield_active:
                    player.health -= 25 # mengurangi nyawa
                    game.spawn_explosion(player.rect.centerx, player.rect.centery, RED, 30)
                    if player.health <= 0:
                        game_active = False # pemain kalah
                else:
                    # jika perisai aktif, pemain terlindungi
                    game.spawn_explosion(hit.rect.centerx, hit.rect.centery, BLUE, 20)
                
                # memunculkan asteroid baru
                a = Asteroid(level)
                all_sprites.add(a)
                asteroids.add(a)

        # kalo player ambil item
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == "coin":
                player.score += 100
                game.score_scale = 1.5
                all_sprites.add(FloatingText(hit.rect.centerx, hit.rect.centery, "BONUS +100", YELLOW, 32))
            else:
                player.shield_active = True
                player.shield_time = now
                all_sprites.add(FloatingText(hit.rect.centerx, hit.rect.centery, "SHIELD ACTIVATED", BLUE))

        # gambar semua ke layar
        # efek getar (screen shake)
        off_x, off_y = 0, 0
        if game.shake_time > 0:
            off_x = random.randint(-game.shake_intensity, game.shake_intensity)
            off_y = random.randint(-game.shake_intensity, game.shake_intensity)
            game.shake_time -= 1

        # background scrolling
        bg_y += 1 + (level * 0.2)
        if bg_y >= HEIGHT: bg_y = 0
        screen.blit(bg_img, (off_x, bg_y + off_y))
        screen.blit(bg_img, (off_x, bg_y - HEIGHT + off_y))

        # gambar Bintang
        for s in game.stars_far: s.draw(screen, off_x, off_y)
        for s in game.stars_near: s.draw(screen, off_x, off_y)

        # efek api mesin
        thr_w = 20 + random.randint(0, 10)
        pygame.draw.circle(screen, ORANGE, (player.rect.centerx + off_x, player.rect.bottom + off_y), thr_w // 2)
        pygame.draw.circle(screen, YELLOW, (player.rect.centerx + off_x, player.rect.bottom + off_y), thr_w // 4)

        # gambar semua karakteer
        all_sprites.draw(screen)
        floating_texts.draw(screen)

        # gambar shield kalo aktif
        if player.shield_active:
            pygame.draw.circle(screen, BLUE, (player.rect.centerx + off_x, player.rect.centery + off_y), 45, 3)

        # gambar UI (health, skor, level)
        game.draw_hud(screen, player, level, start_time)
        
        # update tampilan ke layar

    if main_running:
        game.game_over(player)

pygame.quit()
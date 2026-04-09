import pygame
import random
import os
import math

# Inisialisasi Pygame (Mesin pembuat game) agar semua fitur bisa digunakan
pygame.init()

# --- KONFIGURASI GAME ---
# Ukuran layar game (Lebar 600 pixel, Tinggi 700 pixel)
WIDTH = 600
HEIGHT = 700
# Frames Per Second (Kecepatan update layar, 60 frame per detik agar mulus)
FPS = 60
# Nama file untuk menyimpan skor tertinggi
HIGHSCORE_FILE = "highscore.txt"

# Definisi Warna menggunakan kode RGB (Red, Green, Blue)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 200, 255)
CYAN = (0, 255, 255)
PURPLE = (200, 0, 255)
ORANGE = (255, 100, 0)

# Membuat jendela game dan mengatur judul serta waktu (clock)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Escape: Ultimate Edition")
clock = pygame.time.Clock()

# Pengaturan Font (Gaya tulisan) untuk berbagai teks di dalam game
font_big = pygame.font.SysFont("Impact", 72)
font_med = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 24)
font_tiny = pygame.font.SysFont("Arial", 18, bold=True)

# --- PENYIAPAN ASET (Gambar) ---

def load_img(name, scale=None):
    """
    Fungsi untuk mengambil gambar dari folder 'assets'.
    Jika gambar tidak ditemukan, akan dibuat kotak merah sebagai pengganti.
    """
    path = os.path.join("assets", name)
    if os.path.exists(path):
        # Memuat gambar dan mengubah formatnya agar lebih ringan dijalankan
        img = pygame.image.load(path).convert_alpha()
        if scale:
            # Mengubah ukuran gambar jika diinginkan
            img = pygame.transform.scale(img, scale)
        return img
    else:
        # Jika file gambar hilang, tampilkan kotak merah (fallback)
        surface = pygame.Surface(scale if scale else (50, 50))
        surface.fill(RED)
        return surface

# Memuat semua gambar objek yang dibutuhkan dalam game
bg_img = load_img("background.png", (WIDTH, HEIGHT))
ship_img = load_img("ship.png", (60, 60))
asteroid_img = load_img("asteroid.png", (50, 50))
laser_img = load_img("laser.png", (10, 40))
coin_img = load_img("coin.png", (35, 35))
shield_img = load_img("shield.png", (45, 45))

# --- FUNGSI PEMBANTU (Sistem Skor) ---

def save_highscore(score):
    """Fungsi untuk menyimpan skor tertinggi ke dalam file teks."""
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass # Mengabaikan error jika gagal menulis file

def load_highscore():
    """Fungsi untuk mengambil skor tertinggi yang tersimpan di file teks."""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

# --- KELAS OBJEK (OOP - Object Oriented Programming) ---

class Star:
    """
    Kelas Star digunakan untuk membuat efek latar belakang bintang yang bergerak.
    Ini memberikan kesan pesawat sedang terbang menembus luar angkasa.
    """
    def __init__(self, speed_mult):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(1.0, 3.0) * speed_mult
        self.size = random.randint(1, 4)
        self.color = (random.randint(150, 255), random.randint(150, 255), 255)

    def update(self):
        """Menggerakkan bintang ke bawah. Jika keluar layar, muncul lagi di atas."""
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surf, offset_x=0, offset_y=0):
        """Menggambar bintang sebagai lingkaran kecil di layar."""
        pygame.draw.circle(surf, self.color, (int(self.x + offset_x), int(self.y + offset_y)), self.size)

class Player(pygame.sprite.Sprite):
    """
    Kelas Player mewakili pesawat yang dikendalikan oleh pemain.
    Mengatur gerakan, nyawa, dan kemampuan menembak.
    """
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
        self.last_shot = pygame.time.get_ticks() # Catatan waktu terakhir menembak
        self.shoot_delay = 200 # Jeda antar tembakan (milidetik)
        self.tilt = 0 # Kemiringan pesawat saat belok

    def update(self):
        """Logika pergerakan pesawat berdasarkan tombol panah yang ditekan."""
        keys = pygame.key.get_pressed()
        self.tilt = 0
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.tilt = 15 # Miring ke kanan (visual)
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.tilt = -15 # Miring ke kiri (visual)
        
        # Mengubah gambar pesawat saat miring agar terlihat dinamis
        if self.tilt != 0:
            self.image = pygame.transform.rotate(ship_img, self.tilt)
        else:
            self.image = ship_img
        self.rect = self.image.get_rect(center=self.rect.center)

        # Menembak jika tombol SPACE ditekan
        if keys[pygame.K_SPACE]:
            self.shoot()

        # Timer Perisai: Jika aktif, periksa apakah sudah lewat 5 detik
        if self.shield_active:
            if pygame.time.get_ticks() - self.shield_time > 5000:
                self.shield_active = False

    def shoot(self):
        """Membuat objek Laser baru jika jeda waktu menembak sudah terpenuhi."""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            laser = Laser(self.rect.centerx, self.rect.top)
            all_sprites.add(laser)
            lasers.add(laser)

class Asteroid(pygame.sprite.Sprite):
    """
    Kelas Asteroid adalah hambatan/musuh yang jatuh dari atas layar.
    """
    def __init__(self, level):
        super().__init__()
        # Ukuran acak agar asteroid terlihat bervariasi
        size_val = random.randint(35, 75)
        self.image = pygame.transform.scale(asteroid_img, (size_val, size_val))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -100)
        # Kecepatan jatuh (semakin tinggi level, semakin cepat)
        self.speedy = random.randrange(3, 7) + (level * 0.5)
        self.speedx = random.randrange(-2, 3) # Gerakan menyamping sedikit
        self.rot = 0 # Rotasi/putaran asteroid
        self.rot_speed = random.randrange(-6, 7)
        self.original_image = self.image

    def update(self):
        """Mengupdate posisi asteroid dan memutarnya."""
        self.rot = (self.rot + self.rot_speed) % 360
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.rot)
        self.rect = self.image.get_rect(center=old_center)
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # Jika asteroid lolos ke bawah, munculkan lagi di atas layar
        if self.rect.top > HEIGHT + 20:
            self.rect.y = random.randrange(-150, -50)
            self.rect.x = random.randrange(WIDTH - self.rect.width)

class Laser(pygame.sprite.Sprite):
    """
    Kelas Laser mewakili proyektil yang ditembakkan oleh pesawat pemain.
    """
    def __init__(self, x, y):
        super().__init__()
        self.image = laser_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -14 # Kecepatan ke atas (negatif)

    def update(self):
        """Menggerakkan laser ke atas. Jika keluar layar, laser dihapus."""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill() # Menghapus objek dari memori agar game tidak berat

class Powerup(pygame.sprite.Sprite):
    """
    Kelas Powerup mewakili item yang bisa diambil (Koin atau Perisai).
    """
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.image = coin_img if type == "coin" else shield_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 5 # Kecepatan jatuh item

    def update(self):
        """Menggerakkan item ke bawah."""
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class VFXParticle(pygame.sprite.Sprite):
    """
    Kelas VFXParticle digunakan untuk membuat efek ledakan partikel.
    """
    def __init__(self, x, y, color, size_range=(2, 6)):
        super().__init__()
        size = random.randint(*size_range)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=(x, y))
        # Kecepatan menyebar ke segala arah (X dan Y acak)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.alpha = 255 # Tingkat transparansi (255 = terlihat jelas)
        self.fade_speed = random.randint(5, 12) # Kecepatan menghilang

    def update(self):
        """Menggerakkan partikel dan membuatnya memudar perlahan."""
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill() # Hapus jika sudah tidak terlihat
        else:
            self.image.set_alpha(self.alpha)

class FloatingText(pygame.sprite.Sprite):
    """
    Kelas FloatingText digunakan untuk menampilkan teks yang melayang (misal: '+50').
    Memberikan feedback visual saat pemain mendapatkan poin.
    """
    def __init__(self, x, y, text, color, size=24):
        super().__init__()
        self.image = pygame.font.SysFont("Arial", size, bold=True).render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = -2 # Melayang ke atas
        self.timer = 40 # Durasi teks muncul di layar

    def update(self):
        """Menggerakkan teks ke atas dan menghapusnya jika waktu habis."""
        self.rect.y += self.vy
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# --- GAME SYSTEM ---

# --- SISTEM INTI GAME ---

class Game:
    """
    Kelas Game mengelola alur utama permainan, termasuk menu,
    tampilan antarmuka (HUD), dan efek-efek visual global.
    """
    def __init__(self):
        self.highscore = load_highscore()
        # Membuat kumpulan bintang untuk latar belakang (jauh dan dekat)
        self.stars_far = [Star(0.5) for _ in range(30)]
        self.stars_near = [Star(1.2) for _ in range(15)]
        self.shake_time = 0
        self.shake_intensity = 0
        self.combo = 0
        self.last_kill_time = 0
        self.score_display = 0 # Untuk animasi skor yang merayap naik
        
        # Variabel skala untuk efek animasi zoom (skor & combo)
        self.score_scale = 1.0
        self.combo_scale = 1.0

    def start_shake(self, duration, intensity):
        """Memulai efek layar bergetar saat terjadi ledakan/tabrakan."""
        self.shake_time = duration
        self.shake_intensity = intensity

    def update_vfx(self):
        """Mengupdate status efek visual seperti getaran dan skala animasi."""
        # Mengembalikan ukuran teks ke normal (1.0) secara perlahan
        if self.score_scale > 1.0:
            self.score_scale -= 0.05
        if self.combo_scale > 1.0:
            self.combo_scale -= 0.08
        
        # Mengurangi durasi getaran layar
        if self.shake_time > 0:
            self.shake_time -= 1

    def spawn_explosion(self, x, y, color, count=15):
        """Memicu kumpulan partikel untuk membuat efek ledakan di koordinat (x,y)."""
        for _ in range(count):
            all_sprites.add(VFXParticle(x, y, color))

    def draw_hud(self, surf, player, level, start_time):
        """Menggambar semua antarmuka (Health, Skor, Level) di layar saat bermain."""
        now = pygame.time.get_ticks()
        
        # 1. Bar Atas Transparan (Latar belakang agar UI mudah dibaca)
        ui_bar = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
        ui_bar.fill((0, 0, 0, 150))
        surf.blit(ui_bar, (0, 0))

        # 2. Health Bar (Indikator Nyawa di Kiri Atas)
        bar_width = 150
        bar_height = 15
        x, y = 20, 25
        pygame.draw.rect(surf, (50, 50, 50), (x, y, bar_width, bar_height), border_radius=5)
        health_pct = max(0, player.health / 100)
        # Warna bar berubah sesuai sisa nyawa (Hijau -> Jingga -> Merah)
        fill_color = GREEN if health_pct > 0.4 else (ORANGE if health_pct > 0.2 else RED)
        if health_pct > 0:
            pygame.draw.rect(surf, fill_color, (x + 2, y + 2, (bar_width - 4) * health_pct, bar_height - 4), border_radius=3)
        surf.blit(font_tiny.render("HEALTH", True, WHITE), (x, y - 18))

        # 3. Level Track Line (Garis Progres Level di Tengah Atas)
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

        # 4. Score (Skor di Kanan Atas dengan Efek Zoom)
        if self.score_display < player.score:
            # Membuat angka skor bertambah secara bertahap (animasi)
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

        # 5. Combo (Teks Combo di Tengah Layar)
        if self.combo > 1:
            combo_txt = font_med.render(f"X{self.combo} COMBO", True, ORANGE)
            if self.combo_scale > 1.0:
                sz = combo_txt.get_size()
                combo_txt = pygame.transform.scale(combo_txt, (int(sz[0]*self.combo_scale), int(sz[1]*self.combo_scale)))
            
            combo_rect = combo_txt.get_rect(center=(WIDTH // 2, 110))
            surf.blit(combo_txt, combo_rect)

    def main_menu(self):
        """Menampilkan layar menu utama sebelum game dimulai."""
        menu_running = True
        pulse_time = 0
        
        # Meningkatkan kecepatan bintang untuk efek "Warp Speed" di menu
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
            
            # --- MENGGAMBAR JUDUL (SPACE ESCAPE) ---
            title_text = "SPACE ESCAPE"
            title_txt = font_big.render(title_text, True, WHITE)
            title_rect = title_txt.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            
            # Bayangan Teks agar judul terlihat lebih tajam
            shadow_txt = font_big.render(title_text, True, (0, 0, 0))
            screen.blit(shadow_txt, (title_rect.x + 5, title_rect.y + 5))
            screen.blit(title_txt, title_rect)
            
            draw_text(screen, "ULTIMATE EDITION", 24, WIDTH // 2, HEIGHT // 4 + 40, CYAN, font_small)
            
            # --- INSTRUKSI (BAGIAN TENGAH DAN BAWAH) ---
            inst_y_start = HEIGHT * 2 // 3 - 20
            
            # Animasi Berkedip pada teks "PRESS ANY KEY"
            alpha_blink = int(160 + math.sin(pulse_time * 2) * 95)
            start_txt = font_small.render("PRESS ANY KEY TO START", True, (alpha_blink, alpha_blink, alpha_blink))
            start_rect = start_txt.get_rect(midbottom=(WIDTH // 2, inst_y_start - 20))
            screen.blit(start_txt, start_rect)
            
            draw_text(screen, "KONTROL GAME", 18, WIDTH // 2, inst_y_start, CYAN, font_tiny)
            
            # Pengaturan Kolom Kontrol
            key_x = WIDTH // 2 - 25
            desc_x = WIDTH // 2 - 10
            line_skip = 32 
            first_row_y = inst_y_start + 25
            
            # Menampilkan daftar kontrol (Panah, Space, P)
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

            # Menunggu input pemain untuk memulai game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    menu_running = False

        # Mengembalikan kecepatan bintang ke semula setelah game dimulai
        for i, s in enumerate(self.stars_far): s.speed = original_speeds_far[i]
        for i, s in enumerate(self.stars_near): s.speed = original_speeds_near[i]

    def game_over(self, player):
        """Menampilkan skor akhir saat pemain kalah."""
        # Update skor tertinggi jika pemain memecahkan rekor
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
    """
    Fungsi utilitas untuk menggambar teks di layar dengan lebih mudah.
    Mendukung perataan 'midtop' (tengah) dan 'topleft' (kiri).
    """
    text_surf = font_type.render(text, True, color)
    if align == "midtop":
        rect = text_surf.get_rect(midtop=(x, y))
    else:
        rect = text_surf.get_rect(topleft=(x, y))
    surf.blit(text_surf, rect)

# --- GLOBAL GAME OBJECTS ---
game = Game()
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
lasers = pygame.sprite.Group()
powerups = pygame.sprite.Group()
floating_texts = pygame.sprite.Group()

# --- MAIN LOOP ---

# --- LOOP UTAMA GAME (Jantung dari program) ---

main_running = True
while main_running:
    # Menampilkan menu utama sebelum memulai permainan
    game.main_menu()
    
    # Reset Lingkungan Game (Membersihkan semua objek lama)
    all_sprites.empty()
    asteroids.empty()
    lasers.empty()
    powerups.empty()
    floating_texts.empty()
    
    # Inisialisasi Pemain
    player = Player()
    all_sprites.add(player)
    
    # Membuat gerombolan asteroid awal sebanyak 8 buah
    for _ in range(8):
        a = Asteroid(1)
        all_sprites.add(a)
        asteroids.add(a)

    level = 1
    start_time = pygame.time.get_ticks()
    bg_y = 0
    game_active = True
    paused = False # Status jeda permainan

    # --- LOOP GAMEPLAY (Saat sedang bertempur) ---
    while game_active:
        clock.tick(FPS) # Memastikan game berjalan pada 60 FPS konstannya
        now = pygame.time.get_ticks()

        # 1. MENANGANI INPUT (Keyboard/Mouse)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_active = False
                main_running = False
            if event.type == pygame.KEYDOWN:
                # Menekan 'P' atau 'ESC' untuk jeda (Pause)
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    paused = not paused

        if paused:
            # Jika sedang jeda, tampilkan teks PAUSE dan lewatkan logika update
            draw_text(screen, "PAUSED", 64, WIDTH // 2, HEIGHT // 2 - 50, WHITE, font_big)
            pygame.display.flip()
            continue

        # 2. LOGIKA LEVELING (Sistem Level Otomatis)
        # Level naik setiap 10 detik (10000 milidetik)
        level_sekarang = (now - start_time) // 10000 + 1
        if level_sekarang > level:
            level = level_sekarang

        # 3. UPDATE POSISI OBJEK (Semua objek bergerak di sini)
        all_sprites.update()
        floating_texts.update()
        game.update_vfx() # Mengupdate efek visual (getaran layar, dll)
        for s in game.stars_far: s.update()
        for s in game.stars_near: s.update()

        # Memunculkan Powerup secara acak (Koin/Perisai)
        if random.random() < 0.005:
            p_type = "coin" if random.random() < 0.8 else "shield"
            p = Powerup(p_type)
            all_sprites.add(p)
            powerups.add(p)

        # Reset Combo jika pemain tidak menghancurkan asteroid selama 2 detik
        if now - game.last_kill_time > 2000:
            game.combo = 0

        # COLLISION (Tabrakan): Laser mengenai Asteroid
        hits = pygame.sprite.groupcollide(asteroids, lasers, True, True)
        if hits:
            game.start_shake(10, 5) # Getaran layar kecil saat meledak
            for hit in hits:
                game.combo += 1
                game.last_kill_time = now
                # Poin dikalikan dengan combo (Sistem Hadiah / Reward)
                points = 10 * game.combo
                player.score += points
                game.score_scale = 1.3 # Efek zoom pada angka skor
                game.combo_scale = 1.6 # Efek zoom pada angka combo
                game.spawn_explosion(hit.rect.centerx, hit.rect.centery, YELLOW)
                all_sprites.add(FloatingText(hit.rect.centerx, hit.rect.centery, f"+{points}", CYAN))
                
                # Memunculkan asteroid baru sebagai pengganti yang hancur
                a = Asteroid(level)
                all_sprites.add(a)
                asteroids.add(a)

        # COLLISION (Tabrakan): Pemain menabrak Asteroid
        hits = pygame.sprite.spritecollide(player, asteroids, True)
        if hits:
            game.start_shake(20, 12) # Getaran layar kuat saat pesawat tertabrak
            for hit in hits:
                if not player.shield_active:
                    player.health -= 25 # Mengurangi nyawa
                    game.spawn_explosion(player.rect.centerx, player.rect.centery, RED, 30)
                    if player.health <= 0:
                        game_active = False # Pemain kalah
                else:
                    # Jika perisai aktif, pemain terlindungi
                    game.spawn_explosion(hit.rect.centerx, hit.rect.centery, BLUE, 20)
                
                # Memunculkan asteroid baru
                a = Asteroid(level)
                all_sprites.add(a)
                asteroids.add(a)

        # COLLISION (Tabrakan): Pemain mengambil Powerup
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

        # 4. RENDERING (Menggambar semuanya di layar)
        # Menghitung efek getaran layar (Screen Shake)
        off_x, off_y = 0, 0
        if game.shake_time > 0:
            off_x = random.randint(-game.shake_intensity, game.shake_intensity)
            off_y = random.randint(-game.shake_intensity, game.shake_intensity)
            game.shake_time -= 1

        # Gambar Latar Belakang (Scroll ke bawah terus menerus)
        bg_y += 1 + (level * 0.2)
        if bg_y >= HEIGHT: bg_y = 0
        screen.blit(bg_img, (off_x, bg_y + off_y))
        screen.blit(bg_img, (off_x, bg_y - HEIGHT + off_y))

        # Gambar Bintang (Parallax background untuk efek kedalaman)
        for s in game.stars_far: s.draw(screen, off_x, off_y)
        for s in game.stars_near: s.draw(screen, off_x, off_y)

        # Gambar Api Mesin (Thrusters Animasi)
        thr_w = 20 + random.randint(0, 10)
        pygame.draw.circle(screen, ORANGE, (player.rect.centerx + off_x, player.rect.bottom + off_y), thr_w // 2)
        pygame.draw.circle(screen, YELLOW, (player.rect.centerx + off_x, player.rect.bottom + off_y), thr_w // 4)

        # Menggambar semua karakter (Sprite) dan teks melayang
        all_sprites.draw(screen)
        floating_texts.draw(screen)

        # Gambar efek Perisai (Shield) jika aktif
        if player.shield_active:
            pygame.draw.circle(screen, BLUE, (player.rect.centerx + off_x, player.rect.centery + off_y), 45, 3)

        # Menggambar HUD (Health, Skor, Level)
        game.draw_hud(screen, player, level, start_time)
        
        # Tampilkan semua yang sudah digambar ke layar komputer
        pygame.display.flip()

    # Tampilkan layar Game Over setelah loop gameplay berhenti
    if main_running:
        game.game_over(player)

# Keluar dari Pygame jika loop utama berhenti
pygame.quit()


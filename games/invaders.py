import random

import pygame

from . import common, audio
from .common import t, get_font

W = common.SCREEN_W
H = common.SCREEN_H

# Healing palette
BG = (240, 245, 250)
PLAYER_COL = (180, 215, 190)
PLAYER_DARK = (130, 175, 145)
BULLET_COL = (245, 220, 130)
BOMB_COL = (235, 165, 165)
ALIEN_COLS = [
    (220, 180, 220),  # lavender
    (180, 215, 240),  # baby blue
    (240, 215, 175),  # peach
    (235, 195, 215),  # rose
]
TEXT = (95, 80, 75)

PLAYER_W = 50
PLAYER_H = 20
PLAYER_SPEED = 360
PLAYER_Y = H - 80
ALIEN_W = 38
ALIEN_H = 28
ALIEN_GAP_X = 14
ALIEN_GAP_Y = 18
ROWS = 4
COLS = 9
BULLET_W = 4
BULLET_H = 12
BULLET_SPEED = 580
BOMB_SPEED = 240
FIRE_COOLDOWN = 0.35


def _make_aliens(top_y):
    aliens = []
    grid_w = COLS * ALIEN_W + (COLS - 1) * ALIEN_GAP_X
    left = (W - grid_w) // 2
    for r in range(ROWS):
        for c in range(COLS):
            x = left + c * (ALIEN_W + ALIEN_GAP_X)
            y = top_y + r * (ALIEN_H + ALIEN_GAP_Y)
            kind = r % len(ALIEN_COLS)
            aliens.append({"rect": pygame.Rect(x, y, ALIEN_W, ALIEN_H), "kind": kind, "alive": True})
    return aliens


def _draw_alien(screen, a):
    rect = a["rect"]
    col = ALIEN_COLS[a["kind"]]
    # body
    pygame.draw.ellipse(screen, col, rect)
    dark = tuple(max(0, c - 40) for c in col)
    pygame.draw.ellipse(screen, dark, rect, 2)
    # antennae
    pygame.draw.line(screen, dark, (rect.left + 10, rect.top - 6), (rect.left + 14, rect.top), 2)
    pygame.draw.line(screen, dark, (rect.right - 10, rect.top - 6), (rect.right - 14, rect.top), 2)
    # eyes
    pygame.draw.circle(screen, (255, 255, 255), (rect.centerx - 7, rect.centery), 4)
    pygame.draw.circle(screen, (255, 255, 255), (rect.centerx + 7, rect.centery), 4)
    pygame.draw.circle(screen, TEXT, (rect.centerx - 7, rect.centery), 2)
    pygame.draw.circle(screen, TEXT, (rect.centerx + 7, rect.centery), 2)


def run(screen, clock):
    player = pygame.Rect((W - PLAYER_W) // 2, PLAYER_Y, PLAYER_W, PLAYER_H)
    aliens = _make_aliens(120)
    direction = 1
    alien_speed = 30.0  # px/sec sideways
    descend_pending = False
    bullets = []
    bombs = []
    fire_t = 0.0
    bomb_t = 0.0
    bomb_interval = 1.2
    score = 0
    lives = 3
    wave = 1
    game_over = False
    won_wave = False

    def reset(full=True):
        nonlocal player, aliens, direction, alien_speed, bullets, bombs, fire_t, bomb_t, score, lives, wave, game_over, won_wave
        player = pygame.Rect((W - PLAYER_W) // 2, PLAYER_Y, PLAYER_W, PLAYER_H)
        aliens = _make_aliens(120)
        direction = 1
        alien_speed = 30.0 + (wave - 1) * 10 if not full else 30.0
        bullets = []
        bombs = []
        fire_t = 0.0
        bomb_t = 0.0
        if full:
            score = 0
            lives = 3
            wave = 1
        game_over = False
        won_wave = False

    while True:
        dt = clock.tick(common.FPS) / 1000.0
        keys = pygame.key.get_pressed()
        fire_t = max(0, fire_t - dt)
        bomb_t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    audio.toggle_mute()
                    continue
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if game_over and event.key == pygame.K_r:
                    reset(full=True)
                elif won_wave and event.key == pygame.K_SPACE:
                    wave += 1
                    reset(full=False)
                elif not game_over and not won_wave and event.key == pygame.K_SPACE:
                    if fire_t <= 0:
                        bullets.append(pygame.Rect(player.centerx - BULLET_W // 2,
                                                   player.top - BULLET_H,
                                                   BULLET_W, BULLET_H))
                        fire_t = FIRE_COOLDOWN

        if not game_over and not won_wave:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.x = max(10, player.x - int(PLAYER_SPEED * dt))
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.x = min(W - PLAYER_W - 10, player.x + int(PLAYER_SPEED * dt))

            # Move aliens
            dx = direction * alien_speed * dt
            for a in aliens:
                if a["alive"]:
                    a["rect"].x += dx
            living = [a for a in aliens if a["alive"]]
            if living:
                leftmost = min(a["rect"].left for a in living)
                rightmost = max(a["rect"].right for a in living)
                if (direction == 1 and rightmost >= W - 10) or (direction == -1 and leftmost <= 10):
                    direction *= -1
                    for a in aliens:
                        a["rect"].y += 12

            # Aliens shoot bombs
            if living and bomb_t >= bomb_interval:
                bomb_t = 0
                shooter = random.choice(living)
                bombs.append({"x": float(shooter["rect"].centerx),
                              "y": float(shooter["rect"].bottom)})

            # Bullets up
            for b in bullets:
                b.y -= int(BULLET_SPEED * dt)
            bullets = [b for b in bullets if b.bottom > 0]
            # Bombs down
            for b in bombs:
                b["y"] += BOMB_SPEED * dt
            bombs = [b for b in bombs if b["y"] < H]

            # Bullet vs alien
            for b in bullets[:]:
                for a in aliens:
                    if a["alive"] and a["rect"].colliderect(b):
                        a["alive"] = False
                        try:
                            bullets.remove(b)
                        except ValueError:
                            pass
                        score += 10 * (ROWS - (a["kind"]))
                        break

            # Speed up as aliens are cleared
            remaining = sum(1 for a in aliens if a["alive"])
            if remaining > 0:
                alien_speed = 30.0 + (wave - 1) * 10 + (ROWS * COLS - remaining) * 1.6

            # Bomb vs player
            for b in bombs[:]:
                br = pygame.Rect(int(b["x"]) - 3, int(b["y"]) - 6, 6, 12)
                if br.colliderect(player):
                    bombs.remove(b)
                    lives -= 1
                    if lives <= 0:
                        game_over = True

            # Alien reached player
            for a in aliens:
                if a["alive"] and a["rect"].bottom >= PLAYER_Y:
                    game_over = True
                    break

            if remaining == 0:
                won_wave = True

        # Draw
        screen.fill(BG)

        for a in aliens:
            if a["alive"]:
                _draw_alien(screen, a)

        for b in bullets:
            pygame.draw.rect(screen, BULLET_COL, b, border_radius=2)
        for b in bombs:
            pygame.draw.circle(screen, BOMB_COL, (int(b["x"]), int(b["y"])), 5)

        # Player
        pygame.draw.rect(screen, PLAYER_COL, player, border_radius=6)
        pygame.draw.rect(screen, PLAYER_DARK, player, 2, border_radius=6)
        # cannon
        cannon = pygame.Rect(player.centerx - 4, player.top - 8, 8, 10)
        pygame.draw.rect(screen, PLAYER_DARK, cannon, border_radius=2)

        font = get_font(20, bold=True)
        small = get_font(14)
        s = font.render(f"{t('ui.score')}: {score}", True, TEXT)
        l = font.render(f"{t('ui.lives')}: {lives}", True, TEXT)
        w = font.render(f"{t('ui.wave')}: {wave}", True, TEXT)
        screen.blit(s, (20, 14))
        screen.blit(w, w.get_rect(midtop=(W // 2, 14)))
        screen.blit(l, (W - l.get_width() - 20, 14))

        help_t = small.render(t("invaders.help"), True, TEXT)
        screen.blit(help_t, help_t.get_rect(midbottom=(W // 2, H - 10)))

        if won_wave:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            cx, cy = W // 2, H // 2
            t1 = get_font(40, bold=True).render(t("ui.well_done"), True, TEXT)
            s1 = font.render(t("ui.score") + f": {score}", True, TEXT)
            r1 = small.render("Space   ESC: menu", True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 30)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 20)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 60)))
        elif game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            cx, cy = W // 2, H // 2
            t1 = get_font(40, bold=True).render(t("ui.try_again"), True, TEXT)
            s1 = font.render(f"{t('ui.score')}: {score}   {t('ui.wave')}: {wave}", True, TEXT)
            r1 = small.render(t("ui.restart_menu"), True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 30)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 20)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 60)))

        pygame.display.flip()

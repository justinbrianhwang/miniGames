import random

import pygame

from . import common, audio
from .common import t, get_font

W = common.SCREEN_W
H = common.SCREEN_H

# Healing palette (sky)
BG = (235, 240, 250)
BG_DARK = (215, 225, 245)
PLATFORM_NORMAL = (180, 215, 190)
PLATFORM_NORMAL_DARK = (140, 180, 150)
PLATFORM_MOVING = (200, 220, 240)
PLATFORM_MOVING_DARK = (155, 185, 220)
PLAYER_COL = (245, 200, 165)
PLAYER_DARK = (210, 165, 130)
TEXT = (95, 80, 75)
CLOUD_COL = (250, 250, 255)

GRAVITY = 1100
JUMP_V = -520
PLAYER_R = 18
PLAYER_SPEED = 340
PLAT_W = 80
PLAT_H = 14
SCROLL_THRESHOLD = H * 0.4


def _new_platform(min_y, max_y):
    type_ = "moving" if random.random() < 0.22 else "normal"
    vx = random.choice([-80, 80]) if type_ == "moving" else 0
    return {
        "x": float(random.randint(20, W - PLAT_W - 20)),
        "y": float(random.randint(int(min_y), int(max_y))),
        "type": type_,
        "vx": vx,
    }


def run(screen, clock):
    player_x = W / 2
    player_y = H - 100
    player_vx = 0.0
    player_vy = 0.0
    score = 0.0
    high_score = 0
    game_over = False
    platforms = []
    clouds = []

    def reset():
        nonlocal player_x, player_y, player_vx, player_vy, score, game_over, platforms, clouds
        player_x = W / 2
        player_y = H - 100
        player_vx = 0.0
        player_vy = 0.0
        score = 0.0
        game_over = False
        platforms = [{"x": (W - PLAT_W) / 2, "y": H - 60, "type": "normal", "vx": 0}]
        y = H - 60
        while y > -50:
            y -= random.randint(60, 110)
            platforms.append({
                "x": float(random.randint(20, W - PLAT_W - 20)),
                "y": float(y),
                "type": "moving" if random.random() < 0.2 else "normal",
                "vx": random.choice([-80, 80]) if random.random() < 0.2 else 0,
            })
        clouds = []
        for _ in range(4):
            clouds.append([random.randint(0, W), random.randint(40, H - 100), random.randint(45, 75)])

    reset()

    while True:
        dt = clock.tick(common.FPS) / 1000.0
        if dt > 0.05:
            dt = 0.05
        keys = pygame.key.get_pressed()

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
                    reset()

        if not game_over:
            move = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move += 1
            player_vx = move * PLAYER_SPEED
            player_x += player_vx * dt
            if player_x < -PLAYER_R:
                player_x = W + PLAYER_R
            elif player_x > W + PLAYER_R:
                player_x = -PLAYER_R

            player_vy += GRAVITY * dt
            player_y += player_vy * dt

            for p in platforms:
                if p["type"] == "moving":
                    p["x"] += p["vx"] * dt
                    if p["x"] < 0:
                        p["x"] = 0
                        p["vx"] = -p["vx"]
                    elif p["x"] + PLAT_W > W:
                        p["x"] = W - PLAT_W
                        p["vx"] = -p["vx"]

            if player_vy > 0:
                pl_bottom = player_y + PLAYER_R
                for p in platforms:
                    p_left = p["x"]
                    p_right = p["x"] + PLAT_W
                    p_top = p["y"]
                    if (player_x + PLAYER_R > p_left and player_x - PLAYER_R < p_right
                            and p_top - 10 < pl_bottom < p_top + 14):
                        player_y = p_top - PLAYER_R
                        player_vy = JUMP_V
                        break

            if player_y < SCROLL_THRESHOLD:
                delta = SCROLL_THRESHOLD - player_y
                player_y = SCROLL_THRESHOLD
                for p in platforms:
                    p["y"] += delta
                for c in clouds:
                    c[1] += delta * 0.3
                score += delta

            platforms = [p for p in platforms if p["y"] < H + 30]
            highest = min((p["y"] for p in platforms), default=0)
            while highest > -50:
                highest -= random.randint(55, 105)
                platforms.append({
                    "x": float(random.randint(20, W - PLAT_W - 20)),
                    "y": float(highest),
                    "type": "moving" if random.random() < 0.22 else "normal",
                    "vx": random.choice([-80, 80]) if random.random() < 0.22 else 0,
                })

            for c in clouds:
                c[0] -= 25 * dt
                if c[0] < -100:
                    c[0] = W + 50
                    c[1] = random.randint(40, H - 100)
                if c[1] > H + 20:
                    c[0] = random.randint(0, W)
                    c[1] = random.randint(-40, 0)

            if player_y > H + 60:
                game_over = True
                if int(score) > high_score:
                    high_score = int(score)

        # Draw
        screen.fill(BG)
        for cx, cy, cs in clouds:
            pygame.draw.circle(screen, CLOUD_COL, (int(cx), int(cy)), cs // 2)
            pygame.draw.circle(screen, CLOUD_COL, (int(cx + cs * 0.4), int(cy - cs * 0.2)), int(cs * 0.4))
            pygame.draw.circle(screen, CLOUD_COL, (int(cx - cs * 0.4), int(cy - cs * 0.1)), int(cs * 0.35))

        for p in platforms:
            col = PLATFORM_MOVING if p["type"] == "moving" else PLATFORM_NORMAL
            dark = PLATFORM_MOVING_DARK if p["type"] == "moving" else PLATFORM_NORMAL_DARK
            rect = pygame.Rect(int(p["x"]), int(p["y"]), PLAT_W, PLAT_H)
            pygame.draw.rect(screen, col, rect, border_radius=6)
            pygame.draw.rect(screen, dark, rect, 2, border_radius=6)

        # Player
        pygame.draw.circle(screen, PLAYER_COL, (int(player_x), int(player_y)), PLAYER_R)
        pygame.draw.circle(screen, PLAYER_DARK, (int(player_x), int(player_y)), PLAYER_R, 2)
        # eyes
        pygame.draw.circle(screen, TEXT, (int(player_x) - 5, int(player_y) - 4), 2)
        pygame.draw.circle(screen, TEXT, (int(player_x) + 5, int(player_y) - 4), 2)
        # smile
        pygame.draw.arc(screen, TEXT,
                        (int(player_x) - 6, int(player_y) - 2, 12, 10), 3.4, 6.0, 2)

        font = get_font(28, bold=True)
        small = get_font(14)
        h_t = font.render(f"{t('doodle.height')}: {int(score)}", True, TEXT)
        screen.blit(h_t, (20, 14))
        help_t = small.render(t("doodle.help"), True, TEXT)
        screen.blit(help_t, help_t.get_rect(midbottom=(W // 2, H - 8)))

        if game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            cx, cy = W // 2, H // 2
            t1 = get_font(40, bold=True).render(t("ui.try_again"), True, TEXT)
            s1 = get_font(22, bold=True).render(
                f"{t('doodle.height')}: {int(score)}  ({t('ui.best')}: {high_score})", True, TEXT)
            r1 = small.render(t("ui.restart_menu"), True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 30)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 20)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 60)))

        pygame.display.flip()

import random

import pygame

from . import common, audio
from .common import t, get_font

W = common.SCREEN_W
H = common.SCREEN_H

# Healing palette
BG_SKY = (208, 230, 245)
BG_FAR = (230, 240, 250)
CLOUD = (250, 250, 255)
GROUND = (220, 205, 175)
GROUND_DARK = (190, 175, 145)
PIPE = (170, 215, 165)
PIPE_DARK = (130, 180, 130)
BIRD_BODY = (245, 220, 130)
BIRD_BEAK = (240, 160, 90)
BIRD_DARK = (200, 165, 70)
TEXT = (95, 80, 75)

BIRD_X = 160
BIRD_R = 14
GRAVITY = 1500
JUMP_V = -420
PIPE_W = 70
PIPE_GAP = 200
PIPE_SPEED = 200
PIPE_INTERVAL = 1.7
GROUND_Y = H - 60


def _draw_bird(screen, x, y, angle):
    pygame.draw.circle(screen, BIRD_BODY, (int(x), int(y)), BIRD_R)
    pygame.draw.circle(screen, BIRD_DARK, (int(x), int(y)), BIRD_R, 2)
    # eye
    pygame.draw.circle(screen, (255, 255, 255), (int(x + 5), int(y - 4)), 4)
    pygame.draw.circle(screen, TEXT, (int(x + 6), int(y - 4)), 2)
    # beak
    pygame.draw.polygon(screen, BIRD_BEAK, [
        (x + BIRD_R - 2, y - 2),
        (x + BIRD_R + 8, y + 1),
        (x + BIRD_R - 2, y + 4),
    ])


def run(screen, clock):
    bird_y = H / 2
    bird_v = 0
    pipes = []  # list of {"x": float, "gap_y": int, "passed": bool}
    pipe_spawn_t = 0.0
    started = False
    game_over = False
    score = 0
    high_score = 0

    # decorative clouds
    clouds = []
    for _ in range(5):
        clouds.append([random.randint(0, W), random.randint(40, H // 2), random.randint(40, 80)])

    def reset():
        nonlocal bird_y, bird_v, pipes, pipe_spawn_t, started, game_over, score
        bird_y = H / 2
        bird_v = 0
        pipes = []
        pipe_spawn_t = 0.0
        started = False
        game_over = False
        score = 0

    def flap():
        nonlocal bird_v, started
        bird_v = JUMP_V
        started = True

    while True:
        dt = clock.tick(common.FPS) / 1000.0
        if dt > 0.05:
            dt = 0.05

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    audio.toggle_mute()
                    continue
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_r and game_over:
                    reset()
                elif event.key == pygame.K_SPACE and not game_over:
                    flap()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    reset()
                else:
                    flap()

        if started and not game_over:
            bird_v += GRAVITY * dt
            bird_y += bird_v * dt

            pipe_spawn_t += dt
            if pipe_spawn_t >= PIPE_INTERVAL:
                pipe_spawn_t -= PIPE_INTERVAL
                gap_y = random.randint(140, GROUND_Y - PIPE_GAP - 80)
                pipes.append({"x": float(W + 20), "gap_y": gap_y, "passed": False})

            for p in pipes:
                p["x"] -= PIPE_SPEED * dt
            pipes = [p for p in pipes if p["x"] + PIPE_W > -20]

            # collision + score
            bird_rect = pygame.Rect(int(BIRD_X - BIRD_R), int(bird_y - BIRD_R), BIRD_R * 2, BIRD_R * 2)
            if bird_y + BIRD_R >= GROUND_Y or bird_y - BIRD_R <= 0:
                game_over = True
            for p in pipes:
                top_rect = pygame.Rect(int(p["x"]), 0, PIPE_W, p["gap_y"])
                bot_rect = pygame.Rect(int(p["x"]), p["gap_y"] + PIPE_GAP, PIPE_W, GROUND_Y - (p["gap_y"] + PIPE_GAP))
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect):
                    game_over = True
                if not p["passed"] and p["x"] + PIPE_W < BIRD_X:
                    p["passed"] = True
                    score += 1

            if game_over and score > high_score:
                high_score = score

        # cloud drift
        for c in clouds:
            c[0] -= 20 * dt
            if c[0] < -100:
                c[0] = W + 50
                c[1] = random.randint(40, H // 2)
                c[2] = random.randint(40, 80)

        # Draw
        screen.fill(BG_SKY)
        # far gradient strip
        pygame.draw.rect(screen, BG_FAR, (0, 0, W, H // 3))

        for cx, cy, cs in clouds:
            pygame.draw.circle(screen, CLOUD, (int(cx), int(cy)), cs // 2)
            pygame.draw.circle(screen, CLOUD, (int(cx + cs * 0.4), int(cy - cs * 0.2)), int(cs * 0.4))
            pygame.draw.circle(screen, CLOUD, (int(cx - cs * 0.4), int(cy - cs * 0.1)), int(cs * 0.35))

        # pipes
        for p in pipes:
            pygame.draw.rect(screen, PIPE, (int(p["x"]), 0, PIPE_W, p["gap_y"]), border_radius=4)
            pygame.draw.rect(screen, PIPE_DARK, (int(p["x"]), 0, PIPE_W, p["gap_y"]), 2, border_radius=4)
            pygame.draw.rect(screen, PIPE, (int(p["x"]) - 4, p["gap_y"] - 20, PIPE_W + 8, 20), border_radius=4)
            bot_y = p["gap_y"] + PIPE_GAP
            pygame.draw.rect(screen, PIPE, (int(p["x"]), bot_y, PIPE_W, GROUND_Y - bot_y), border_radius=4)
            pygame.draw.rect(screen, PIPE_DARK, (int(p["x"]), bot_y, PIPE_W, GROUND_Y - bot_y), 2, border_radius=4)
            pygame.draw.rect(screen, PIPE, (int(p["x"]) - 4, bot_y, PIPE_W + 8, 20), border_radius=4)

        # ground
        pygame.draw.rect(screen, GROUND, (0, GROUND_Y, W, H - GROUND_Y))
        pygame.draw.rect(screen, GROUND_DARK, (0, GROUND_Y, W, 4))

        _draw_bird(screen, BIRD_X, bird_y, 0)

        # HUD
        font = get_font(40, bold=True)
        small = get_font(15)
        score_t = font.render(str(score), True, TEXT)
        screen.blit(score_t, score_t.get_rect(midtop=(W // 2, 30)))

        if not started and not game_over:
            tip = get_font(20, bold=True).render(t("flappy.start"), True, TEXT)
            screen.blit(tip, tip.get_rect(center=(W // 2, H // 2 + 80)))

        help_t = small.render(t("flappy.help"), True, TEXT)
        screen.blit(help_t, help_t.get_rect(midbottom=(W // 2, H - 10)))

        if game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            cx, cy = W // 2, H // 2
            t1 = get_font(44, bold=True).render(t("ui.try_again"), True, TEXT)
            s1 = get_font(22, bold=True).render(f"{score}   ({t('ui.best')}: {high_score})", True, TEXT)
            r1 = small.render(t("ui.restart_menu"), True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 30)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 20)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 60)))

        pygame.display.flip()

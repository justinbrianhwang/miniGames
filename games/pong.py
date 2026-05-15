import math
import random

import pygame

from . import common, audio
from .common import t, get_font

# Healing palette
BG = (250, 244, 232)
LINE = (220, 205, 185)
PLAYER_COL = (180, 215, 190)
AI_COL = (218, 208, 235)
BALL_COL = (235, 145, 145)
TEXT = (95, 80, 75)

PADDLE_W = 110
PADDLE_H = 14
BALL_R = 9
SPEED_START = 380
TARGET = 5

PLAYER_Y = common.SCREEN_H - 80
AI_Y = 70


def run(screen, clock):
    player = pygame.Rect((common.SCREEN_W - PADDLE_W) // 2, PLAYER_Y, PADDLE_W, PADDLE_H)
    ai = pygame.Rect((common.SCREEN_W - PADDLE_W) // 2, AI_Y, PADDLE_W, PADDLE_H)

    ball_x = common.SCREEN_W / 2
    ball_y = common.SCREEN_H / 2
    ball_vx = 0.0
    ball_vy = 0.0
    serving = True
    serve_to = 1  # 1 = down to player, -1 = up to AI
    serve_timer = 0.0

    player_score = 0
    ai_score = 0
    winner = None  # "player" / "ai" / None

    def serve(direction):
        nonlocal ball_x, ball_y, ball_vx, ball_vy, serving, serve_timer
        ball_x = common.SCREEN_W / 2
        ball_y = common.SCREEN_H / 2
        angle = random.uniform(-0.5, 0.5)
        ball_vx = math.sin(angle) * SPEED_START
        ball_vy = math.cos(angle) * SPEED_START * direction
        serving = False

    def reset_game():
        nonlocal player_score, ai_score, winner, serving, serve_timer, serve_to
        player_score = 0
        ai_score = 0
        winner = None
        serving = True
        serve_to = random.choice([-1, 1])
        serve_timer = 0.0

    serve_to = random.choice([-1, 1])

    while True:
        dt = clock.tick(common.FPS) / 1000.0
        mouse_x, _ = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    audio.toggle_mute()
                    continue
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if winner and event.key == pygame.K_r:
                    reset_game()

        player.centerx = mouse_x
        player.clamp_ip(pygame.Rect(0, 0, common.SCREEN_W, common.SCREEN_H))

        if not winner:
            # AI tracking, with a deadzone so it loses sometimes
            ai_speed = 280
            if ball_vy < 0:
                target_x = ball_x
            else:
                target_x = common.SCREEN_W / 2
            if ai.centerx < target_x - 8:
                ai.x = min(common.SCREEN_W - PADDLE_W, ai.x + ai_speed * dt)
            elif ai.centerx > target_x + 8:
                ai.x = max(0, ai.x - ai_speed * dt)

            if serving:
                serve_timer += dt
                ball_x = common.SCREEN_W / 2
                ball_y = common.SCREEN_H / 2
                if serve_timer > 0.8:
                    serve(serve_to)
            else:
                ball_x += ball_vx * dt
                ball_y += ball_vy * dt

                if ball_x - BALL_R < 0:
                    ball_x = BALL_R
                    ball_vx = abs(ball_vx)
                elif ball_x + BALL_R > common.SCREEN_W:
                    ball_x = common.SCREEN_W - BALL_R
                    ball_vx = -abs(ball_vx)

                # Paddle collisions
                ball_rect = pygame.Rect(int(ball_x - BALL_R), int(ball_y - BALL_R), BALL_R * 2, BALL_R * 2)
                if ball_vy > 0 and ball_rect.colliderect(player):
                    ball_y = player.top - BALL_R
                    offset = (ball_x - player.centerx) / (PADDLE_W / 2)
                    offset = max(-1.0, min(1.0, offset))
                    speed = math.hypot(ball_vx, ball_vy) * 1.03
                    angle = offset * (math.pi / 3)
                    ball_vx = math.sin(angle) * speed
                    ball_vy = -math.cos(angle) * speed
                elif ball_vy < 0 and ball_rect.colliderect(ai):
                    ball_y = ai.bottom + BALL_R
                    offset = (ball_x - ai.centerx) / (PADDLE_W / 2)
                    offset = max(-1.0, min(1.0, offset))
                    speed = math.hypot(ball_vx, ball_vy) * 1.03
                    angle = offset * (math.pi / 3)
                    ball_vx = math.sin(angle) * speed
                    ball_vy = math.cos(angle) * speed

                # Score
                if ball_y - BALL_R > common.SCREEN_H:
                    ai_score += 1
                    serve_to = 1
                    serving = True
                    serve_timer = 0.0
                elif ball_y + BALL_R < 0:
                    player_score += 1
                    serve_to = -1
                    serving = True
                    serve_timer = 0.0

                if player_score >= TARGET:
                    winner = "player"
                elif ai_score >= TARGET:
                    winner = "ai"

        # Draw
        screen.fill(BG)
        # center dashed line
        for y in range(0, common.SCREEN_H, 18):
            pygame.draw.rect(screen, LINE, (common.SCREEN_W // 2 - 2, y, 4, 10), border_radius=2)

        pygame.draw.rect(screen, PLAYER_COL, player, border_radius=8)
        pygame.draw.rect(screen, AI_COL, ai, border_radius=8)
        pygame.draw.circle(screen, BALL_COL, (int(ball_x), int(ball_y)), BALL_R)

        font = get_font(28, bold=True)
        small = get_font(15)
        font_big = get_font(46, bold=True)

        you = font.render(f"{t('pong.you')}: {player_score}", True, TEXT)
        cpu = font.render(f"{t('pong.cpu')}: {ai_score}", True, TEXT)
        screen.blit(cpu, (20, 16))
        screen.blit(you, (20, common.SCREEN_H - 50))

        tip = small.render(t("pong.help"), True, TEXT)
        screen.blit(tip, tip.get_rect(midbottom=(common.SCREEN_W // 2, common.SCREEN_H - 6)))

        if winner:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            msg = t("pong.you_win") if winner == "player" else t("pong.cpu_win")
            cx, cy = common.SCREEN_W // 2, common.SCREEN_H // 2
            t1 = font_big.render(msg, True, TEXT)
            sc = font.render(f"{player_score} - {ai_score}", True, TEXT)
            r1 = small.render(t("ui.restart_menu"), True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 30)))
            screen.blit(sc, sc.get_rect(center=(cx, cy + 20)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 60)))

        pygame.display.flip()

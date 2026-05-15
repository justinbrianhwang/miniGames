import math
import random

import pygame

from . import common, audio
from .common import t, get_font

BG = (20, 25, 40)
PADDLE_COLOR = (220, 220, 240)
BALL_COLOR = (255, 230, 100)
BRICK_COLORS = [
    (220, 70, 90),
    (240, 140, 60),
    (240, 200, 80),
    (130, 200, 100),
    (90, 170, 220),
    (160, 100, 220),
    (220, 130, 220),
    (160, 220, 200),
]
TEXT = (235, 235, 240)

PADDLE_W = 110
PADDLE_H = 16
PADDLE_Y = common.SCREEN_H - 50

BALL_R = 9
BASE_BALL_SPEED = 380

BRICK_COLS = 10
BRICK_AREA_W = common.SCREEN_W - 40
BRICK_W = BRICK_AREA_W / BRICK_COLS
BRICK_H = 24
BRICK_TOP = 90

# Each stage is a list of strings ('#' = brick, '.' = empty).
# Width must be BRICK_COLS chars.
STAGES = [
    # S1 — standard
    [
        "##########",
        "##########",
        "##########",
        "##########",
        "##########",
        "##########",
    ],
    # S2 — rounded edges
    [
        "..######..",
        ".########.",
        "##########",
        "##########",
        ".########.",
        "..######..",
    ],
    # S3 — gap in middle
    [
        "####..####",
        "####..####",
        "####..####",
        "####..####",
        "####..####",
        "####..####",
    ],
    # S4 — pyramid
    [
        "##########",
        ".########.",
        "..######..",
        "...####...",
        "....##....",
        "..........",
    ],
    # S5 — checkerboard
    [
        "#.#.#.#.#.",
        ".#.#.#.#.#",
        "#.#.#.#.#.",
        ".#.#.#.#.#",
        "#.#.#.#.#.",
        ".#.#.#.#.#",
    ],
    # S6 — diamond
    [
        "....##....",
        "...####...",
        "..######..",
        ".########.",
        "..######..",
        "...####...",
    ],
    # S7 — two bands
    [
        "##########",
        "##########",
        "..........",
        "..........",
        "##########",
        "##########",
    ],
    # S8 — heart
    [
        ".##....##.",
        "##########",
        "##########",
        ".########.",
        "..######..",
        "...####...",
    ],
    # S9 — diagonal stripes
    [
        "#...#...#.",
        "##...#...#",
        ".##...#...",
        "#.##...#..",
        "##.##...#.",
        "###.##...#",
    ],
    # S10 — fortress
    [
        "##########",
        "##########",
        "##########",
        "##.####.##",
        "##.####.##",
        "##.####.##",
        "##########",
        "##########",
    ],
]


def _make_bricks(stage_idx):
    pattern = STAGES[stage_idx % len(STAGES)]
    rows = len(pattern)
    bricks = []
    for r, row in enumerate(pattern):
        for c, ch in enumerate(row):
            if ch != "#":
                continue
            rect = pygame.Rect(
                int(20 + c * BRICK_W + 2),
                int(BRICK_TOP + r * (BRICK_H + 4) + 2),
                int(BRICK_W - 4),
                int(BRICK_H - 4),
            )
            bricks.append({"rect": rect, "color": BRICK_COLORS[r % len(BRICK_COLORS)]})
    return bricks


def run(screen, clock):
    paddle = pygame.Rect((common.SCREEN_W - PADDLE_W) // 2, PADDLE_Y, PADDLE_W, PADDLE_H)

    stage = 0
    bricks = _make_bricks(stage)
    ball_speed = BASE_BALL_SPEED

    ball_x = float(paddle.centerx)
    ball_y = float(paddle.top - BALL_R - 2)
    ball_vx = 0.0
    ball_vy = 0.0
    launched = False

    score = 0
    lives = 3
    game_over = False
    all_clear = False

    def reset_ball():
        nonlocal ball_x, ball_y, ball_vx, ball_vy, launched
        ball_x = float(paddle.centerx)
        ball_y = float(paddle.top - BALL_R - 2)
        ball_vx = 0.0
        ball_vy = 0.0
        launched = False

    def launch_ball():
        nonlocal ball_vx, ball_vy, launched
        angle = -math.pi / 2 + random.uniform(-0.4, 0.4)
        ball_vx = math.cos(angle) * ball_speed
        ball_vy = math.sin(angle) * ball_speed
        launched = True

    def next_stage():
        nonlocal stage, bricks, ball_speed, all_clear
        stage += 1
        if stage >= len(STAGES):
            all_clear = True
            return
        bricks = _make_bricks(stage)
        ball_speed = BASE_BALL_SPEED + stage * 25
        reset_ball()

    def reset():
        nonlocal stage, bricks, score, lives, game_over, all_clear, ball_speed
        stage = 0
        bricks = _make_bricks(stage)
        score = 0
        lives = 3
        game_over = False
        all_clear = False
        ball_speed = BASE_BALL_SPEED
        reset_ball()

    while True:
        dt = clock.tick(common.FPS) / 1000.0
        mouse_x, _ = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    audio.toggle_mute()
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
                elif event.key == pygame.K_r and (game_over or all_clear):
                    reset()
                elif event.key == pygame.K_SPACE and not launched and not game_over and not all_clear:
                    launch_ball()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not launched and not game_over and not all_clear:
                    launch_ball()

        paddle.centerx = mouse_x
        paddle.clamp_ip(pygame.Rect(0, 0, common.SCREEN_W, common.SCREEN_H))

        if not launched:
            ball_x = float(paddle.centerx)
            ball_y = float(paddle.top - BALL_R - 2)

        if launched and not game_over and not all_clear:
            ball_x += ball_vx * dt
            ball_y += ball_vy * dt

            if ball_x - BALL_R < 0:
                ball_x = BALL_R
                ball_vx = abs(ball_vx)
            elif ball_x + BALL_R > common.SCREEN_W:
                ball_x = common.SCREEN_W - BALL_R
                ball_vx = -abs(ball_vx)
            if ball_y - BALL_R < 0:
                ball_y = BALL_R
                ball_vy = abs(ball_vy)

            if (ball_vy > 0
                    and paddle.left - BALL_R <= ball_x <= paddle.right + BALL_R
                    and paddle.top - BALL_R <= ball_y <= paddle.bottom):
                ball_y = paddle.top - BALL_R
                offset = (ball_x - paddle.centerx) / (PADDLE_W / 2)
                offset = max(-1.0, min(1.0, offset))
                angle = -math.pi / 2 + offset * (math.pi / 3)
                speed = math.hypot(ball_vx, ball_vy)
                ball_vx = math.cos(angle) * speed
                ball_vy = math.sin(angle) * speed

            ball_rect = pygame.Rect(int(ball_x - BALL_R), int(ball_y - BALL_R), BALL_R * 2, BALL_R * 2)
            hit_idx = ball_rect.collidelist([b["rect"] for b in bricks])
            if hit_idx >= 0:
                br = bricks[hit_idx]["rect"]
                dx_left = abs(ball_rect.right - br.left)
                dx_right = abs(ball_rect.left - br.right)
                dy_top = abs(ball_rect.bottom - br.top)
                dy_bot = abs(ball_rect.top - br.bottom)
                min_pen = min(dx_left, dx_right, dy_top, dy_bot)
                if min_pen == dx_left or min_pen == dx_right:
                    ball_vx = -ball_vx
                else:
                    ball_vy = -ball_vy
                bricks.pop(hit_idx)
                score += 10
                if not bricks:
                    next_stage()

            if ball_y - BALL_R > common.SCREEN_H:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    reset_ball()

        # Draw
        screen.fill(BG)
        for b in bricks:
            pygame.draw.rect(screen, b["color"], b["rect"], border_radius=4)
        pygame.draw.rect(screen, PADDLE_COLOR, paddle, border_radius=8)
        pygame.draw.circle(screen, BALL_COLOR, (int(ball_x), int(ball_y)), BALL_R)

        font = get_font(22, bold=True)
        font_small = get_font(15)
        font_big = get_font(46, bold=True)

        hud = font.render(
            f"{t('ui.score')}: {score}   {t('ui.lives')}: {lives}   "
            f"{t('sokoban.level')}: {min(stage + 1, len(STAGES))}/{len(STAGES)}",
            True, TEXT)
        screen.blit(hud, (12, 12))

        tip = font_small.render(t("breakout.help"), True, TEXT)
        screen.blit(tip, tip.get_rect(midbottom=(common.SCREEN_W // 2, common.SCREEN_H - 6)))

        if not launched and not game_over and not all_clear:
            launch_tip = font_small.render(t("breakout.launch"), True, TEXT)
            screen.blit(launch_tip, launch_tip.get_rect(center=(common.SCREEN_W // 2, 60)))

        if game_over or all_clear:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            msg = t("ui.well_done") if all_clear else t("ui.try_again")
            cx, cy = common.SCREEN_W // 2, common.SCREEN_H // 2
            t1 = font_big.render(msg, True, common.TEXT_LIGHT)
            s1 = font.render(f"{t('ui.score')}: {score}", True, common.TEXT_LIGHT)
            r1 = font_small.render(t("ui.restart_menu"), True, common.TEXT_LIGHT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 40)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 10)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 50)))

        pygame.display.flip()

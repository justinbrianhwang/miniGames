import random

import pygame

from . import common, audio
from .common import t, get_font

CELL = 30
GRID_W = 20
HUD_H = 40
GRID_H = (common.SCREEN_H - HUD_H) // CELL  # 24

BG = (30, 35, 45)
HUD_BG = (20, 25, 35)
GRID_LINE = (40, 45, 55)
SNAKE_HEAD = (100, 220, 120)
SNAKE_BODY = (70, 180, 90)
FOOD = (235, 90, 100)
TEXT = (230, 230, 230)


def run(screen, clock):
    def new_food(snake):
        while True:
            p = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
            if p not in snake:
                return p

    snake = [(GRID_W // 2, GRID_H // 2)]
    direction = (1, 0)
    pending_dir = direction
    food = new_food(snake)
    score = 0
    high_score = 0
    game_over = False
    accum = 0
    move_interval = 130

    def reset():
        nonlocal snake, direction, pending_dir, food, score, game_over, accum, move_interval
        snake = [(GRID_W // 2, GRID_H // 2)]
        direction = (1, 0)
        pending_dir = direction
        food = new_food(snake)
        score = 0
        game_over = False
        accum = 0
        move_interval = 130

    while True:
        dt = clock.tick(common.FPS)

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
                elif not game_over:
                    if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                        pending_dir = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                        pending_dir = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                        pending_dir = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                        pending_dir = (1, 0)

        if not game_over:
            accum += dt
            while accum >= move_interval:
                accum -= move_interval
                direction = pending_dir
                head = snake[0]
                new_head = (head[0] + direction[0], head[1] + direction[1])
                if not (0 <= new_head[0] < GRID_W and 0 <= new_head[1] < GRID_H):
                    game_over = True
                    if score > high_score:
                        high_score = score
                    break
                if new_head in snake[:-1]:
                    game_over = True
                    if score > high_score:
                        high_score = score
                    break
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    food = new_food(snake)
                    move_interval = max(60, move_interval - 2)
                else:
                    snake.pop()

        # Draw
        screen.fill(HUD_BG, (0, 0, common.SCREEN_W, HUD_H))
        screen.fill(BG, (0, HUD_H, common.SCREEN_W, common.SCREEN_H - HUD_H))

        for gx in range(GRID_W + 1):
            x = gx * CELL
            pygame.draw.line(screen, GRID_LINE, (x, HUD_H), (x, common.SCREEN_H), 1)
        for gy in range(GRID_H + 1):
            y = HUD_H + gy * CELL
            pygame.draw.line(screen, GRID_LINE, (0, y), (common.SCREEN_W, y), 1)

        fx, fy = food
        pygame.draw.rect(screen, FOOD,
                         (fx * CELL + 3, HUD_H + fy * CELL + 3, CELL - 6, CELL - 6),
                         border_radius=6)

        for i, (sx, sy) in enumerate(snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(screen, color,
                             (sx * CELL + 2, HUD_H + sy * CELL + 2, CELL - 4, CELL - 4),
                             border_radius=4)

        font = get_font(22, bold=True)
        font_small = get_font(14)
        font_big = get_font(40, bold=True)

        s = font.render(f"{t('ui.score')}: {score}   {t('ui.best')}: {high_score}", True, TEXT)
        screen.blit(s, (12, 8))
        h = font_small.render(t("snake.help"), True, TEXT)
        screen.blit(h, h.get_rect(midright=(common.SCREEN_W - 12, HUD_H // 2)))

        if game_over:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            cx, cy = common.SCREEN_W // 2, common.SCREEN_H // 2
            t1 = font_big.render(t("ui.game_over"), True, common.TEXT_LIGHT)
            s1 = font.render(f"{t('ui.score')}: {score}   {t('ui.best')}: {high_score}", True, common.TEXT_LIGHT)
            r1 = get_font(18).render(t("ui.restart_menu"), True, common.TEXT_LIGHT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 40)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 10)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 50)))

        pygame.display.flip()

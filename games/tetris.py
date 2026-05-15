import random

import pygame

from . import common, audio
from .common import t, get_font

CELL = 30
COLS = 10
ROWS = 20
PLAY_W = COLS * CELL
PLAY_H = ROWS * CELL
PLAY_X = 60
PLAY_Y = 80

BG = (15, 18, 30)
GRID_BG = (25, 30, 50)
GRID_LINE = (35, 40, 55)
TEXT = (240, 240, 245)

COLORS = {
    "I": (100, 220, 230),
    "O": (240, 220, 100),
    "T": (190, 110, 220),
    "S": (100, 220, 130),
    "Z": (230, 100, 110),
    "J": (110, 140, 230),
    "L": (240, 170, 90),
}

SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    "T": [
        [(0, 1), (1, 1), (2, 1), (1, 0)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (1, 1), (1, 2), (0, 1)],
    ],
    "S": [
        [(0, 1), (1, 1), (1, 0), (2, 0)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(0, 2), (1, 2), (1, 1), (2, 1)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}


def _draw_cell(screen, x, y, color):
    pygame.draw.rect(screen, color, (x + 1, y + 1, CELL - 2, CELL - 2))
    light = tuple(min(255, c + 50) for c in color)
    dark = tuple(max(0, c - 60) for c in color)
    pygame.draw.line(screen, light, (x + 1, y + 1), (x + CELL - 2, y + 1), 2)
    pygame.draw.line(screen, light, (x + 1, y + 1), (x + 1, y + CELL - 2), 2)
    pygame.draw.line(screen, dark, (x + 1, y + CELL - 2), (x + CELL - 2, y + CELL - 2), 2)
    pygame.draw.line(screen, dark, (x + CELL - 2, y + 1), (x + CELL - 2, y + CELL - 2), 2)


def run(screen, clock):
    grid = [[None] * COLS for _ in range(ROWS)]
    bag = []

    def refill_bag():
        keys = list(SHAPES.keys())
        random.shuffle(keys)
        return keys

    def next_piece():
        nonlocal bag
        if not bag:
            bag = refill_bag()
        kind = bag.pop()
        return {"kind": kind, "rot": 0, "x": 3, "y": 0}

    piece = next_piece()
    next_p = next_piece()

    fall_interval = 600
    fall_accum = 0
    score = 0
    lines_cleared = 0
    level = 1
    game_over = False

    def cells_of(p):
        rots = SHAPES[p["kind"]]
        return [(p["x"] + dx, p["y"] + dy) for dx, dy in rots[p["rot"] % len(rots)]]

    def valid(p):
        for cx, cy in cells_of(p):
            if cx < 0 or cx >= COLS or cy >= ROWS:
                return False
            if cy >= 0 and grid[cy][cx] is not None:
                return False
        return True

    def lock():
        nonlocal piece, next_p, game_over, score, lines_cleared, level, fall_interval
        for cx, cy in cells_of(piece):
            if 0 <= cy < ROWS and 0 <= cx < COLS:
                grid[cy][cx] = COLORS[piece["kind"]]
        new_grid = [row for row in grid if any(c is None for c in row)]
        cleared = ROWS - len(new_grid)
        for _ in range(cleared):
            new_grid.insert(0, [None] * COLS)
        for r in range(ROWS):
            grid[r] = new_grid[r]
        if cleared:
            lines_cleared += cleared
            score += [0, 100, 300, 500, 800][cleared] * level
            level = 1 + lines_cleared // 10
            fall_interval = max(80, 600 - (level - 1) * 50)
        piece = next_p
        next_p = next_piece()
        if not valid(piece):
            game_over = True

    def reset():
        nonlocal piece, next_p, bag, score, lines_cleared, level, fall_interval, fall_accum, game_over
        for r in range(ROWS):
            grid[r] = [None] * COLS
        bag = refill_bag()
        piece = next_piece()
        next_p = next_piece()
        score = 0
        lines_cleared = 0
        level = 1
        fall_interval = 600
        fall_accum = 0
        game_over = False

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
                if game_over:
                    if event.key == pygame.K_r:
                        reset()
                    continue
                if event.key == pygame.K_LEFT:
                    piece["x"] -= 1
                    if not valid(piece):
                        piece["x"] += 1
                elif event.key == pygame.K_RIGHT:
                    piece["x"] += 1
                    if not valid(piece):
                        piece["x"] -= 1
                elif event.key == pygame.K_DOWN:
                    piece["y"] += 1
                    if not valid(piece):
                        piece["y"] -= 1
                    else:
                        score += 1
                elif event.key in (pygame.K_UP, pygame.K_x):
                    piece["rot"] += 1
                    if not valid(piece):
                        ok = False
                        for kick in (-1, 1, -2, 2):
                            piece["x"] += kick
                            if valid(piece):
                                ok = True
                                break
                            piece["x"] -= kick
                        if not ok:
                            piece["rot"] -= 1
                elif event.key == pygame.K_z:
                    piece["rot"] -= 1
                    if not valid(piece):
                        ok = False
                        for kick in (1, -1, 2, -2):
                            piece["x"] += kick
                            if valid(piece):
                                ok = True
                                break
                            piece["x"] -= kick
                        if not ok:
                            piece["rot"] += 1
                elif event.key == pygame.K_SPACE:
                    drops = 0
                    while valid(piece):
                        piece["y"] += 1
                        drops += 1
                    piece["y"] -= 1
                    drops = max(0, drops - 1)
                    score += drops * 2
                    lock()

        if not game_over:
            fall_accum += dt
            while fall_accum >= fall_interval:
                fall_accum -= fall_interval
                piece["y"] += 1
                if not valid(piece):
                    piece["y"] -= 1
                    lock()
                    break

        # Draw
        screen.fill(BG)
        pygame.draw.rect(screen, GRID_BG, (PLAY_X - 4, PLAY_Y - 4, PLAY_W + 8, PLAY_H + 8))
        pygame.draw.rect(screen, BG, (PLAY_X, PLAY_Y, PLAY_W, PLAY_H))

        for c in range(COLS + 1):
            x = PLAY_X + c * CELL
            pygame.draw.line(screen, GRID_LINE, (x, PLAY_Y), (x, PLAY_Y + PLAY_H), 1)
        for r in range(ROWS + 1):
            y = PLAY_Y + r * CELL
            pygame.draw.line(screen, GRID_LINE, (PLAY_X, y), (PLAY_X + PLAY_W, y), 1)

        for r in range(ROWS):
            for c in range(COLS):
                if grid[r][c]:
                    _draw_cell(screen, PLAY_X + c * CELL, PLAY_Y + r * CELL, grid[r][c])

        if not game_over:
            color = COLORS[piece["kind"]]
            for cx, cy in cells_of(piece):
                if cy >= 0:
                    _draw_cell(screen, PLAY_X + cx * CELL, PLAY_Y + cy * CELL, color)

        font = get_font(22, bold=True)
        font_small = get_font(15)
        font_big = get_font(40, bold=True)

        hud_x = PLAY_X + PLAY_W + 30
        screen.blit(font.render(f"{t('ui.score')}: {score}", True, TEXT), (hud_x, PLAY_Y))
        screen.blit(font.render(f"{t('ui.lines')}: {lines_cleared}", True, TEXT), (hud_x, PLAY_Y + 40))
        screen.blit(font.render(f"{t('ui.level')}: {level}", True, TEXT), (hud_x, PLAY_Y + 80))

        screen.blit(font.render(t("ui.next"), True, TEXT), (hud_x, PLAY_Y + 150))
        ncolor = COLORS[next_p["kind"]]
        for dx, dy in SHAPES[next_p["kind"]][0]:
            nx = hud_x + dx * 22
            ny = PLAY_Y + 190 + dy * 22
            pygame.draw.rect(screen, ncolor, (nx, ny, 20, 20), border_radius=2)

        screen.blit(font_small.render(t("tetris.help1"), True, TEXT), (hud_x, PLAY_Y + 330))
        screen.blit(font_small.render(t("tetris.help2"), True, TEXT), (hud_x, PLAY_Y + 354))
        screen.blit(font_small.render(t("tetris.help3"), True, TEXT), (hud_x, PLAY_Y + 378))

        if game_over:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            cx, cy = common.SCREEN_W // 2, common.SCREEN_H // 2
            t1 = font_big.render(t("ui.game_over"), True, common.TEXT_LIGHT)
            s1 = font.render(f"{t('ui.score')}: {score}", True, common.TEXT_LIGHT)
            r1 = font_small.render(t("ui.restart_menu"), True, common.TEXT_LIGHT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 40)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 10)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 50)))

        pygame.display.flip()

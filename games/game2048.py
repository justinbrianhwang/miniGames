import random

import pygame

from . import common, audio
from .common import t, get_font

GRID = 4
PADDING = 14
TILE_SIZE = 110
BOARD_SIZE = GRID * TILE_SIZE + (GRID + 1) * PADDING
BOARD_X = (common.SCREEN_W - BOARD_SIZE) // 2
BOARD_Y = 190

BG = (250, 248, 240)
BOARD_COLOR = (190, 175, 160)
TEXT_DARK = (115, 105, 95)
TEXT_TITLE = (60, 50, 40)
TEXT_LIGHT = (250, 248, 240)

TILE_COLORS = {
    0: (205, 192, 178),
    2: (240, 230, 220),
    4: (235, 222, 200),
    8: (245, 175, 120),
    16: (245, 150, 100),
    32: (245, 125, 95),
    64: (245, 95, 60),
    128: (235, 210, 115),
    256: (235, 205, 95),
    512: (235, 200, 80),
    1024: (235, 195, 65),
    2048: (235, 190, 50),
}


def _slide_left(row):
    filtered = [x for x in row if x != 0]
    merged = []
    gained = 0
    i = 0
    while i < len(filtered):
        if i + 1 < len(filtered) and filtered[i] == filtered[i + 1]:
            v = filtered[i] * 2
            merged.append(v)
            gained += v
            i += 2
        else:
            merged.append(filtered[i])
            i += 1
    while len(merged) < GRID:
        merged.append(0)
    changed = merged != row
    return merged, gained, changed


def run(screen, clock):
    grid = [[0] * GRID for _ in range(GRID)]
    score = 0
    high_score = 0
    game_over = False
    won = False
    keep_playing = False

    def spawn():
        empties = [(r, c) for r in range(GRID) for c in range(GRID) if grid[r][c] == 0]
        if not empties:
            return
        r, c = random.choice(empties)
        grid[r][c] = 4 if random.random() < 0.1 else 2

    def can_move():
        for r in range(GRID):
            for c in range(GRID):
                if grid[r][c] == 0:
                    return True
                if c + 1 < GRID and grid[r][c] == grid[r][c + 1]:
                    return True
                if r + 1 < GRID and grid[r][c] == grid[r + 1][c]:
                    return True
        return False

    def reset():
        nonlocal score, game_over, won, keep_playing
        for r in range(GRID):
            grid[r] = [0] * GRID
        score = 0
        game_over = False
        won = False
        keep_playing = False
        spawn()
        spawn()

    def move(dx, dy):
        nonlocal score, won, game_over
        changed = False
        gained_total = 0
        if dx == -1:
            for r in range(GRID):
                new_row, g, ch = _slide_left(grid[r])
                grid[r] = new_row
                gained_total += g
                changed |= ch
        elif dx == 1:
            for r in range(GRID):
                rev = list(reversed(grid[r]))
                new_row, g, ch = _slide_left(rev)
                grid[r] = list(reversed(new_row))
                gained_total += g
                changed |= ch
        elif dy == -1:
            for c in range(GRID):
                col = [grid[r][c] for r in range(GRID)]
                new_col, g, ch = _slide_left(col)
                for r in range(GRID):
                    grid[r][c] = new_col[r]
                gained_total += g
                changed |= ch
        elif dy == 1:
            for c in range(GRID):
                col = [grid[r][c] for r in range(GRID)]
                rev = list(reversed(col))
                new_col, g, ch = _slide_left(rev)
                new_col = list(reversed(new_col))
                for r in range(GRID):
                    grid[r][c] = new_col[r]
                gained_total += g
                changed |= ch
        if changed:
            score += gained_total
            spawn()
            if not won and any(grid[r][c] == 2048 for r in range(GRID) for c in range(GRID)):
                won = True
            if not can_move():
                game_over = True

    reset()

    while True:
        clock.tick(common.FPS)

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
                if won and not keep_playing:
                    if event.key == pygame.K_r:
                        reset()
                        continue
                    elif event.key == pygame.K_c:
                        keep_playing = True
                        continue
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    move(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    move(1, 0)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    move(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    move(0, 1)
                if score > high_score:
                    high_score = score

        # Draw
        screen.fill(BG)

        title = get_font(50, bold=True).render("2048", True, TEXT_TITLE)
        screen.blit(title, (BOARD_X, 60))

        small = get_font(16)
        font = get_font(24, bold=True)
        font_big = get_font(54, bold=True)

        sbox = pygame.Rect(BOARD_X + BOARD_SIZE - 230, 60, 110, 60)
        hbox = pygame.Rect(BOARD_X + BOARD_SIZE - 110, 60, 110, 60)
        pygame.draw.rect(screen, BOARD_COLOR, sbox, border_radius=6)
        pygame.draw.rect(screen, BOARD_COLOR, hbox, border_radius=6)
        st = small.render(t("ui.score"), True, TEXT_LIGHT)
        sv = font.render(str(score), True, TEXT_LIGHT)
        ht = small.render(t("ui.best"), True, TEXT_LIGHT)
        hv = font.render(str(high_score), True, TEXT_LIGHT)
        screen.blit(st, st.get_rect(midtop=(sbox.centerx, sbox.y + 4)))
        screen.blit(sv, sv.get_rect(midbottom=(sbox.centerx, sbox.bottom - 4)))
        screen.blit(ht, ht.get_rect(midtop=(hbox.centerx, hbox.y + 4)))
        screen.blit(hv, hv.get_rect(midbottom=(hbox.centerx, hbox.bottom - 4)))

        pygame.draw.rect(screen, BOARD_COLOR, (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE), border_radius=8)
        for r in range(GRID):
            for c in range(GRID):
                tx = BOARD_X + PADDING + c * (TILE_SIZE + PADDING)
                ty = BOARD_Y + PADDING + r * (TILE_SIZE + PADDING)
                v = grid[r][c]
                tile_color = TILE_COLORS.get(v, (60, 50, 40))
                pygame.draw.rect(screen, tile_color, (tx, ty, TILE_SIZE, TILE_SIZE), border_radius=6)
                if v:
                    txt_color = TEXT_TITLE if v <= 4 else TEXT_LIGHT
                    if v < 100:
                        tf = get_font(48, bold=True)
                    elif v < 1000:
                        tf = get_font(38, bold=True)
                    else:
                        tf = get_font(30, bold=True)
                    ts = tf.render(str(v), True, txt_color)
                    screen.blit(ts, ts.get_rect(center=(tx + TILE_SIZE // 2, ty + TILE_SIZE // 2)))

        help_t = small.render(t("2048.help"), True, TEXT_DARK)
        screen.blit(help_t, help_t.get_rect(center=(common.SCREEN_W // 2, BOARD_Y + BOARD_SIZE + 25)))

        if won and not keep_playing:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((255, 230, 100, 110))
            screen.blit(overlay, (0, 0))
            cx, cy = common.SCREEN_W // 2, common.SCREEN_H // 2
            t1 = font_big.render("2048!", True, TEXT_TITLE)
            r1 = font.render(t("2048.continue"), True, TEXT_TITLE)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 20)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 40)))
        elif game_over:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            cx, cy = common.SCREEN_W // 2, common.SCREEN_H // 2
            t1 = font_big.render(t("ui.game_over"), True, common.TEXT_LIGHT)
            s1 = font.render(f"{t('ui.score')}: {score}", True, common.TEXT_LIGHT)
            r1 = small.render(t("ui.restart_menu"), True, common.TEXT_LIGHT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 40)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 10)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 50)))

        pygame.display.flip()

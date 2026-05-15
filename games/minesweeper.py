import random

import pygame

from . import common, audio
from .common import t, get_font

GRID_W = 10
GRID_H = 10
MINES = 12
CELL = 48
BOARD_PX = GRID_W * CELL
BOARD_X = (common.SCREEN_W - BOARD_PX) // 2
BOARD_Y = 150

# Healing palette
BG = (250, 244, 232)
CELL_HIDDEN = (215, 230, 215)
CELL_HIDDEN_HOVER = (230, 240, 225)
CELL_REVEALED = (245, 235, 215)
CELL_BORDER = (190, 175, 155)
MINE_BG = (245, 215, 215)
FLAG_COL = (235, 145, 145)
TEXT = (95, 80, 75)

NUMBER_COLORS = {
    1: (110, 150, 200),
    2: (130, 180, 130),
    3: (220, 130, 140),
    4: (160, 130, 200),
    5: (190, 140, 100),
    6: (110, 180, 180),
    7: (140, 110, 90),
    8: (160, 110, 130),
}


def run(screen, clock):
    cells = [[{"mine": False, "revealed": False, "flagged": False, "adj": 0}
              for _ in range(GRID_W)] for _ in range(GRID_H)]
    first_click = True
    game_over = False
    won = False
    start_ms = 0
    elapsed_ms = 0

    def place_mines(exclude_r, exclude_c):
        safe = {(exclude_r + dr, exclude_c + dc)
                for dr in (-1, 0, 1) for dc in (-1, 0, 1)}
        placed = 0
        while placed < MINES:
            r = random.randint(0, GRID_H - 1)
            c = random.randint(0, GRID_W - 1)
            if (r, c) in safe or cells[r][c]["mine"]:
                continue
            cells[r][c]["mine"] = True
            placed += 1
        for r in range(GRID_H):
            for c in range(GRID_W):
                if cells[r][c]["mine"]:
                    continue
                n = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < GRID_H and 0 <= cc < GRID_W and cells[rr][cc]["mine"]:
                            n += 1
                cells[r][c]["adj"] = n

    def reveal(r, c):
        if not (0 <= r < GRID_H and 0 <= c < GRID_W):
            return
        cell = cells[r][c]
        if cell["revealed"] or cell["flagged"]:
            return
        cell["revealed"] = True
        if cell["adj"] == 0 and not cell["mine"]:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    reveal(r + dr, c + dc)

    def check_win():
        for r in range(GRID_H):
            for c in range(GRID_W):
                cell = cells[r][c]
                if not cell["mine"] and not cell["revealed"]:
                    return False
        return True

    def reset():
        nonlocal cells, first_click, game_over, won, start_ms, elapsed_ms
        cells = [[{"mine": False, "revealed": False, "flagged": False, "adj": 0}
                  for _ in range(GRID_W)] for _ in range(GRID_H)]
        first_click = True
        game_over = False
        won = False
        start_ms = 0
        elapsed_ms = 0

    def cell_at(pos):
        x, y = pos
        if not (BOARD_X <= x < BOARD_X + BOARD_PX and BOARD_Y <= y < BOARD_Y + GRID_H * CELL):
            return None
        c = (x - BOARD_X) // CELL
        r = (y - BOARD_Y) // CELL
        return int(r), int(c)

    while True:
        clock.tick(common.FPS)
        now = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        if start_ms and not game_over and not won:
            elapsed_ms = now - start_ms

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    audio.toggle_mute()
                    continue
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_r:
                    reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_over or won:
                    continue
                rc = cell_at(event.pos)
                if rc is None:
                    continue
                r, c = rc
                cell = cells[r][c]
                if event.button == 1:
                    if cell["flagged"] or cell["revealed"]:
                        continue
                    if first_click:
                        place_mines(r, c)
                        first_click = False
                        start_ms = now
                    if cell["mine"]:
                        cell["revealed"] = True
                        game_over = True
                        for rr in range(GRID_H):
                            for cc in range(GRID_W):
                                if cells[rr][cc]["mine"]:
                                    cells[rr][cc]["revealed"] = True
                    else:
                        reveal(r, c)
                        if check_win():
                            won = True
                elif event.button == 3:
                    if not cell["revealed"]:
                        cell["flagged"] = not cell["flagged"]

        # Draw
        screen.fill(BG)

        title = get_font(34, bold=True).render(t("game.minesweeper.name"), True, TEXT)
        screen.blit(title, (BOARD_X, 60))

        font = get_font(20, bold=True)
        flags = sum(1 for row in cells for cell_ in row if cell_["flagged"])
        mines_t = font.render(f"{t('minesweeper.mines')}: {flags}/{MINES}", True, TEXT)
        secs = elapsed_ms // 1000
        time_t = font.render(f"{t('ui.time')}: {secs}s", True, TEXT)
        screen.blit(mines_t, (BOARD_X + BOARD_PX - mines_t.get_width(), 62))
        screen.blit(time_t, (BOARD_X + BOARD_PX - time_t.get_width(), 90))

        # Cells
        hover_rc = cell_at(mouse_pos)
        for r in range(GRID_H):
            for c in range(GRID_W):
                cell = cells[r][c]
                rect = pygame.Rect(BOARD_X + c * CELL, BOARD_Y + r * CELL, CELL, CELL)
                if cell["revealed"]:
                    bg = MINE_BG if cell["mine"] else CELL_REVEALED
                else:
                    hover = hover_rc == (r, c) and not game_over and not won
                    bg = CELL_HIDDEN_HOVER if hover else CELL_HIDDEN
                pygame.draw.rect(screen, bg, rect.inflate(-2, -2), border_radius=4)
                pygame.draw.rect(screen, CELL_BORDER, rect.inflate(-2, -2), 1, border_radius=4)

                if cell["revealed"]:
                    if cell["mine"]:
                        pygame.draw.circle(screen, (110, 90, 90), rect.center, CELL // 4)
                    elif cell["adj"] > 0:
                        n_color = NUMBER_COLORS.get(cell["adj"], TEXT)
                        nf = get_font(24, bold=True)
                        s = nf.render(str(cell["adj"]), True, n_color)
                        screen.blit(s, s.get_rect(center=rect.center))
                elif cell["flagged"]:
                    # flag triangle
                    cx, cy = rect.center
                    pygame.draw.polygon(screen, FLAG_COL, [
                        (cx - 8, cy - 8), (cx + 10, cy), (cx - 8, cy + 2)
                    ])
                    pygame.draw.line(screen, TEXT, (cx - 8, cy - 12), (cx - 8, cy + 12), 2)

        help_t = get_font(14).render(t("minesweeper.help"), True, TEXT)
        screen.blit(help_t, help_t.get_rect(midbottom=(common.SCREEN_W // 2, common.SCREEN_H - 10)))

        if game_over or won:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            cx, cy = common.SCREEN_W // 2, common.SCREEN_H // 2
            msg = t("minesweeper.cleared") if won else t("ui.try_again")
            t1 = get_font(44, bold=True).render(msg, True, TEXT)
            s1 = font.render(f"{t('ui.time')}: {secs}s", True, TEXT)
            r1 = get_font(15).render(t("ui.restart_menu"), True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 30)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 20)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 60)))

        pygame.display.flip()

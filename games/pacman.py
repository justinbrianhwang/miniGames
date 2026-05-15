import random

import pygame

from . import common, audio
from .common import t, get_font

W = common.SCREEN_W
H = common.SCREEN_H

# Healing palette
BG = (250, 244, 232)
WALL = (200, 215, 240)
WALL_DARK = (155, 170, 210)
DOT_COL = (220, 175, 105)
PAC_COL = (245, 220, 110)
PAC_DARK = (210, 180, 70)
GHOST_COL = (245, 180, 195)
GHOST_DARK = (210, 145, 165)
TEXT = (95, 80, 75)

MAZES = [
    # M1 — classic-ish
    [
        "#############",
        "#...........#",
        "#.##.###.##.#",
        "#...........#",
        "#.##.#.#.##.#",
        "#....#.#....#",
        "###..#.#..###",
        "#...........#",
        "###..#.#..###",
        "#....#.#....#",
        "#.##.#.#.##.#",
        "#...........#",
        "#.##.###.##.#",
        "#...........#",
        "#############",
    ],
    # M2 — horizontal bands
    [
        "#############",
        "#...........#",
        "#.####.####.#",
        "#...........#",
        "#.####.####.#",
        "#...........#",
        "###...#...###",
        "#...........#",
        "###...#...###",
        "#...........#",
        "#.####.####.#",
        "#...........#",
        "#.####.####.#",
        "#...........#",
        "#############",
    ],
    # M3 — island arena
    [
        "#############",
        "#...........#",
        "#...........#",
        "#..##...##..#",
        "#..##...##..#",
        "#...........#",
        "#.....#.....#",
        "#.....#.....#",
        "#.....#.....#",
        "#...........#",
        "#..##...##..#",
        "#..##...##..#",
        "#...........#",
        "#...........#",
        "#############",
    ],
    # M4 — corridors
    [
        "#############",
        "#...........#",
        "#.#.#.#.#.#.#",
        "#.#.#.#.#.#.#",
        "#...........#",
        "#.#########.#",
        "#...........#",
        "#####...#####",
        "#...........#",
        "#.#########.#",
        "#...........#",
        "#.#.#.#.#.#.#",
        "#.#.#.#.#.#.#",
        "#...........#",
        "#############",
    ],
]

MOVE_DURATION = 0.16
GHOST_MOVE_DURATION = 0.18


def run(screen, clock):
    maze_idx = 0
    maze = MAZES[maze_idx]
    rows = len(maze)
    cols = len(maze[0])
    cell = min(32, (W - 80) // cols, (H - 220) // rows)
    maze_w = cols * cell
    maze_h = rows * cell
    ox = (W - maze_w) // 2
    oy = 130

    def is_wall(cx, cy):
        if not (0 <= cx < cols and 0 <= cy < rows):
            return True
        return maze[cy][cx] == "#"

    def find_start():
        # Pac start: top-left non-wall; ghost start: bottom-right non-wall
        pac = None
        ghost = None
        for r in range(rows):
            for c in range(cols):
                if maze[r][c] == ".":
                    if pac is None:
                        pac = (c, r)
        for r in range(rows - 1, -1, -1):
            for c in range(cols - 1, -1, -1):
                if maze[r][c] == ".":
                    if ghost is None:
                        ghost = (c, r)
                        break
            if ghost:
                break
        return pac, ghost

    def init_state():
        nonlocal pac_cx, pac_cy, pac_dir, pending, pac_t
        nonlocal ghost_cx, ghost_cy, ghost_dir, ghost_t, dots, total_dots, eaten, won, lost
        dots = set()
        for r in range(rows):
            for c in range(cols):
                if maze[r][c] == ".":
                    dots.add((c, r))
        pac, ghost = find_start()
        pac_cx, pac_cy = pac
        ghost_cx, ghost_cy = ghost
        dots.discard((pac_cx, pac_cy))
        pac_dir = (0, 0)
        pending = (0, 0)
        pac_t = 0.0
        ghost_dir = (0, 0)
        ghost_t = 0.0
        total_dots = len(dots)
        eaten = 0
        won = False
        lost = False

    def load_maze(idx):
        nonlocal maze_idx, maze, rows, cols, cell, maze_w, maze_h, ox, oy
        maze_idx = idx % len(MAZES)
        maze = MAZES[maze_idx]
        rows = len(maze)
        cols = len(maze[0])
        cell = min(32, (W - 80) // cols, (H - 220) // rows)
        maze_w = cols * cell
        maze_h = rows * cell
        ox = (W - maze_w) // 2
        oy = 130
        init_state()

    def pick_ghost_dir(gx, gy, gdir, px, py):
        options = []
        for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if gdir != (0, 0) and d == (-gdir[0], -gdir[1]):
                continue
            nx, ny = gx + d[0], gy + d[1]
            if not is_wall(nx, ny):
                options.append(d)
        if not options:
            return (-gdir[0], -gdir[1])
        if random.random() < 0.65:
            return min(options, key=lambda d: (gx + d[0] - px) ** 2 + (gy + d[1] - py) ** 2)
        return random.choice(options)

    # Initialize state
    pac_cx = pac_cy = 0
    pac_dir = (0, 0)
    pending = (0, 0)
    pac_t = 0.0
    ghost_cx = ghost_cy = 0
    ghost_dir = (0, 0)
    ghost_t = 0.0
    dots = set()
    total_dots = 0
    eaten = 0
    won = False
    lost = False
    init_state()

    while True:
        dt = clock.tick(common.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    audio.toggle_mute()
                    continue
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if won:
                    if event.key in (pygame.K_n, pygame.K_SPACE):
                        load_maze(maze_idx + 1)
                    elif event.key == pygame.K_r:
                        load_maze(0)
                    continue
                if lost and event.key == pygame.K_r:
                    init_state()
                    continue
                if not (won or lost):
                    if event.key in (pygame.K_UP, pygame.K_w):
                        pending = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        pending = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        pending = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        pending = (1, 0)

        if not won and not lost:
            if pac_dir == (0, 0):
                if pending != (0, 0) and not is_wall(pac_cx + pending[0], pac_cy + pending[1]):
                    pac_dir = pending
                    pac_t = 0.0
            else:
                pac_t += dt
                if pac_t >= MOVE_DURATION:
                    pac_t -= MOVE_DURATION
                    pac_cx += pac_dir[0]
                    pac_cy += pac_dir[1]
                    if (pac_cx, pac_cy) in dots:
                        dots.discard((pac_cx, pac_cy))
                        eaten += 1
                    if not dots:
                        won = True
                    if pending != (0, 0) and not is_wall(pac_cx + pending[0], pac_cy + pending[1]):
                        pac_dir = pending
                    elif is_wall(pac_cx + pac_dir[0], pac_cy + pac_dir[1]):
                        pac_dir = (0, 0)

            if ghost_dir == (0, 0):
                ghost_dir = pick_ghost_dir(ghost_cx, ghost_cy, ghost_dir, pac_cx, pac_cy)
                ghost_t = 0.0
            else:
                ghost_t += dt
                if ghost_t >= GHOST_MOVE_DURATION:
                    ghost_t -= GHOST_MOVE_DURATION
                    ghost_cx += ghost_dir[0]
                    ghost_cy += ghost_dir[1]
                    ghost_dir = pick_ghost_dir(ghost_cx, ghost_cy, ghost_dir, pac_cx, pac_cy)

            pac_progress = pac_t / MOVE_DURATION if pac_dir != (0, 0) else 0
            px = (pac_cx + pac_dir[0] * pac_progress + 0.5) * cell + ox
            py = (pac_cy + pac_dir[1] * pac_progress + 0.5) * cell + oy
            g_progress = ghost_t / GHOST_MOVE_DURATION if ghost_dir != (0, 0) else 0
            gx = (ghost_cx + ghost_dir[0] * g_progress + 0.5) * cell + ox
            gy = (ghost_cy + ghost_dir[1] * g_progress + 0.5) * cell + oy
            if (px - gx) ** 2 + (py - gy) ** 2 < (cell * 0.7) ** 2:
                lost = True

        # Draw
        screen.fill(BG)

        title = get_font(24, bold=True).render(t("game.pacman.name"), True, TEXT)
        screen.blit(title, (40, 50))
        font = get_font(18, bold=True)
        lvl_t = font.render(f"{t('sokoban.level')}: {maze_idx + 1}/{len(MAZES)}", True, TEXT)
        screen.blit(lvl_t, (40, 90))
        dot_t = font.render(f"{t('pacman.dots')}: {eaten}/{total_dots}", True, TEXT)
        screen.blit(dot_t, (W - dot_t.get_width() - 40, 90))

        for r in range(rows):
            for c in range(cols):
                if maze[r][c] == "#":
                    rect = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell)
                    pygame.draw.rect(screen, WALL, rect.inflate(-2, -2), border_radius=6)
                    pygame.draw.rect(screen, WALL_DARK, rect.inflate(-2, -2), 2, border_radius=6)

        for (c, r) in dots:
            cx = ox + c * cell + cell // 2
            cy = oy + r * cell + cell // 2
            pygame.draw.circle(screen, DOT_COL, (cx, cy), max(3, cell // 8))

        pac_progress = pac_t / MOVE_DURATION if pac_dir != (0, 0) else 0
        px = (pac_cx + pac_dir[0] * pac_progress + 0.5) * cell + ox
        py = (pac_cy + pac_dir[1] * pac_progress + 0.5) * cell + oy
        pr = cell // 2 - 4
        pygame.draw.circle(screen, PAC_COL, (int(px), int(py)), pr)
        pygame.draw.circle(screen, PAC_DARK, (int(px), int(py)), pr, 2)
        if pac_dir != (0, 0):
            ex = int(px - 3 * pac_dir[1])
            ey = int(py - 6 + 3 * pac_dir[0])
        else:
            ex, ey = int(px), int(py - 6)
        pygame.draw.circle(screen, TEXT, (ex, ey), 2)

        g_progress = ghost_t / GHOST_MOVE_DURATION if ghost_dir != (0, 0) else 0
        gx = (ghost_cx + ghost_dir[0] * g_progress + 0.5) * cell + ox
        gy = (ghost_cy + ghost_dir[1] * g_progress + 0.5) * cell + oy
        gx, gy = int(gx), int(gy)
        gr = cell // 2 - 4
        pygame.draw.circle(screen, GHOST_COL, (gx, gy - 2), gr)
        pygame.draw.rect(screen, GHOST_COL, (gx - gr, gy - 2, gr * 2, gr))
        for i in range(4):
            cxw = gx - gr + (gr * 2 // 4) * i + gr // 4
            pygame.draw.circle(screen, GHOST_COL, (cxw, gy + gr - 2), gr // 4)
        pygame.draw.circle(screen, (255, 255, 255), (gx - 5, gy - 4), 4)
        pygame.draw.circle(screen, (255, 255, 255), (gx + 5, gy - 4), 4)
        pygame.draw.circle(screen, TEXT, (gx - 5, gy - 4), 2)
        pygame.draw.circle(screen, TEXT, (gx + 5, gy - 4), 2)

        help_t = get_font(14).render(t("pacman.help"), True, TEXT)
        screen.blit(help_t, help_t.get_rect(midbottom=(W // 2, H - 10)))

        if won or lost:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            cx2, cy2 = W // 2, H // 2
            is_last = maze_idx == len(MAZES) - 1
            if won:
                head = t("ui.well_done") if is_last else t("sokoban.complete")
            else:
                head = t("ui.try_again")
            t1 = get_font(34, bold=True).render(head, True, TEXT)
            s1 = font.render(f"{t('pacman.dots')}: {eaten}/{total_dots}", True, TEXT)
            r1 = get_font(14).render(t("ui.restart_menu"), True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx2, cy2 - 30)))
            screen.blit(s1, s1.get_rect(center=(cx2, cy2 + 20)))
            screen.blit(r1, r1.get_rect(center=(cx2, cy2 + 60)))

        pygame.display.flip()

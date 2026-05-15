import pygame

from . import common, audio
from .common import t, get_font

# Healing palette
BG = (250, 244, 232)
FLOOR = (245, 230, 200)
WALL = (185, 165, 140)
WALL_DARK = (155, 138, 115)
PLAYER_COL = (170, 205, 230)
PLAYER_DARK = (130, 170, 200)
BOX_COL = (220, 180, 140)
BOX_DONE = (180, 215, 140)
BOX_DARK = (180, 145, 105)
TARGET_COL = (235, 145, 145)
TEXT = (95, 80, 75)

# Standard sokoban notation:
#   '#' wall    '.' floor   'o' empty target
#   '$' box on floor   '*' box on target
#   '@' player on floor   '+' player on target
#   ' ' outside (not part of level)
LEVELS = [
    # --- Beginner ---
    [
        "########",
        "#......#",
        "#.o..@.#",
        "#..$...#",
        "#......#",
        "########",
    ],
    [
        "########",
        "#......#",
        "#@$..o.#",
        "#......#",
        "########",
    ],
    [
        "########",
        "#......#",
        "#.@....#",
        "#.$....#",
        "#......#",
        "#.o....#",
        "########",
    ],
    [
        "########",
        "#.o.o..#",
        "#......#",
        "#.$.$..#",
        "#......#",
        "#..@...#",
        "########",
    ],
    [
        "########",
        "#......#",
        "#.@$.o.#",
        "#......#",
        "#......#",
        "########",
    ],

    # --- Easy ---
    [
        "  ######",
        "###....#",
        "#.o..o.#",
        "#......#",
        "#.$.$..#",
        "#......#",
        "#..@..##",
        "#######.",
    ],
    [
        "########",
        "#......#",
        "#..o...#",
        "#......#",
        "#..$...#",
        "#..@...#",
        "########",
    ],
    [
        "##########",
        "#........#",
        "#@$.$.o.o#",
        "#........#",
        "##########",
    ],
    [
        "##########",
        "#........#",
        "#.o.o.o..#",
        "#........#",
        "#.$.$.$..#",
        "#........#",
        "#...@....#",
        "##########",
    ],
    [
        "########",
        "#.o....#",
        "#......#",
        "#..$...#",
        "#......#",
        "#.@..o.#",
        "#..$...#",
        "########",
    ],

    # --- Medium ---
    [
        "  #####  ",
        "###...###",
        "#.o...o.#",
        "#.$...$.#",
        "#...@...#",
        "#.$...$.#",
        "#.o...o.#",
        "###...###",
        "  #####  ",
    ],
    [
        "##########",
        "#o......o#",
        "#........#",
        "#.$....$.#",
        "#........#",
        "#....@...#",
        "##########",
    ],
    [
        "##########",
        "#........#",
        "#.######.#",
        "#.#@...#.#",
        "#.#.$..#.#",
        "#.#....#.#",
        "#.#..o.#.#",
        "#.######.#",
        "#........#",
        "##########",
    ],
    [
        "###########",
        "#o.o.o.o.o#",
        "#.........#",
        "#$.$.$.$.$#",
        "#.........#",
        "#....@....#",
        "###########",
    ],
    [
        "##########",
        "#........#",
        "#.o.o....#",
        "#.$.$....#",
        "#........#",
        "#.$.$....#",
        "#.o.o....#",
        "#...@....#",
        "##########",
    ],

    # --- Harder ---
    [
        "##########",
        "#........#",
        "#.o......#",
        "#.$......#",
        "#........#",
        "#....@...#",
        "#........#",
        "#.....$.o#",
        "#.....$..#",
        "#.....o..#",
        "##########",
    ],
    [
        "############",
        "#..........#",
        "#.o..o..o..#",
        "#..........#",
        "#..........#",
        "#.$..$..$..#",
        "#..........#",
        "#.....@....#",
        "#..........#",
        "#.$..$..$..#",
        "#..........#",
        "#.o..o..o..#",
        "#..........#",
        "############",
    ],
    [
        "##########",
        "#........#",
        "#.######.#",
        "#.#.o..#.#",
        "#.#....#.#",
        "#.#.$..#.#",
        "#.#..@.#.#",
        "#.#.$..#.#",
        "#.#....#.#",
        "#.#.o..#.#",
        "#.######.#",
        "#........#",
        "##########",
    ],
    [
        "############",
        "#..........#",
        "#.$......$.#",
        "#..........#",
        "#....o.....#",
        "#....@.....#",
        "#....o.....#",
        "#..........#",
        "#.$......$.#",
        "#..........#",
        "#....o.....#",
        "#..........#",
        "#....o.....#",
        "#..........#",
        "############",
    ],
    [
        "##############",
        "#............#",
        "#.o.o.o.o.o..#",
        "#............#",
        "#.$.$.$.$.$..#",
        "#............#",
        "#............#",
        "#.....@......#",
        "#............#",
        "##############",
    ],
]


def _parse(level_idx):
    grid = LEVELS[level_idx]
    walls = set()
    floor = set()
    boxes = []
    targets = set()
    player = None
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == "#":
                walls.add((c, r))
            elif ch == ".":
                floor.add((c, r))
            elif ch == "o":
                floor.add((c, r))
                targets.add((c, r))
            elif ch == "$":
                floor.add((c, r))
                boxes.append([c, r])
            elif ch == "*":
                floor.add((c, r))
                targets.add((c, r))
                boxes.append([c, r])
            elif ch == "@":
                floor.add((c, r))
                player = [c, r]
            elif ch == "+":
                floor.add((c, r))
                targets.add((c, r))
                player = [c, r]
    return walls, floor, boxes, player, targets


def run(screen, clock):
    level_idx = 0
    walls, floor, boxes, player, targets = _parse(level_idx)
    moves = 0
    complete = False

    def load_level(i):
        nonlocal walls, floor, boxes, player, targets, moves, complete, level_idx
        level_idx = i % len(LEVELS)
        walls, floor, boxes, player, targets = _parse(level_idx)
        moves = 0
        complete = False

    def check_complete():
        return all((b[0], b[1]) in targets for b in boxes)

    def try_move(dx, dy):
        nonlocal moves, complete
        if complete:
            return
        nx, ny = player[0] + dx, player[1] + dy
        if (nx, ny) in walls or (nx, ny) not in floor:
            return
        for b in boxes:
            if b[0] == nx and b[1] == ny:
                bx, by = nx + dx, ny + dy
                if (bx, by) in walls or (bx, by) not in floor:
                    return
                if any(other is not b and other[0] == bx and other[1] == by for other in boxes):
                    return
                b[0], b[1] = bx, by
                break
        player[0], player[1] = nx, ny
        moves += 1
        if check_complete():
            complete = True

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
                elif event.key == pygame.K_r:
                    load_level(level_idx)
                elif event.key == pygame.K_n:
                    load_level((level_idx + 1) % len(LEVELS))
                elif event.key == pygame.K_p:
                    load_level((level_idx - 1) % len(LEVELS))
                elif event.key in (pygame.K_UP, pygame.K_w):
                    try_move(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    try_move(0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    try_move(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    try_move(1, 0)

        all_pts = walls | floor
        max_c = max(c for c, _ in all_pts)
        max_r = max(r for _, r in all_pts)
        cell = min(60, (common.SCREEN_W - 80) // (max_c + 1), (common.SCREEN_H - 220) // (max_r + 1))
        grid_w = (max_c + 1) * cell
        grid_h = (max_r + 1) * cell
        ox = (common.SCREEN_W - grid_w) // 2
        oy = 150

        screen.fill(BG)

        title = get_font(28, bold=True).render(t("game.sokoban.name"), True, TEXT)
        screen.blit(title, (40, 50))
        font = get_font(20, bold=True)
        lvl_t = font.render(f"{t('sokoban.level')}: {level_idx + 1} / {len(LEVELS)}", True, TEXT)
        screen.blit(lvl_t, (40, 95))
        mv_t = font.render(f"{t('ui.moves')}: {moves}", True, TEXT)
        screen.blit(mv_t, (common.SCREEN_W - mv_t.get_width() - 40, 95))

        for (c, r) in floor:
            rect = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell)
            pygame.draw.rect(screen, FLOOR, rect)
        for (c, r) in walls:
            rect = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell)
            pygame.draw.rect(screen, WALL, rect)
            pygame.draw.rect(screen, WALL_DARK, rect, 2)
        for (c, r) in targets:
            cx = ox + c * cell + cell // 2
            cy = oy + r * cell + cell // 2
            pygame.draw.circle(screen, TARGET_COL, (cx, cy), cell // 6)
            pygame.draw.circle(screen, (200, 110, 110), (cx, cy), cell // 6, 2)
        for b in boxes:
            on_target = (b[0], b[1]) in targets
            col = BOX_DONE if on_target else BOX_COL
            rect = pygame.Rect(ox + b[0] * cell + 4, oy + b[1] * cell + 4, cell - 8, cell - 8)
            pygame.draw.rect(screen, col, rect, border_radius=6)
            pygame.draw.rect(screen, BOX_DARK, rect, 2, border_radius=6)
            inner = rect.inflate(-cell // 3, -cell // 3)
            pygame.draw.rect(screen, BOX_DARK, inner, 2, border_radius=4)
        cx = ox + player[0] * cell + cell // 2
        cy = oy + player[1] * cell + cell // 2
        pygame.draw.circle(screen, PLAYER_COL, (cx, cy), cell // 2 - 6)
        pygame.draw.circle(screen, PLAYER_DARK, (cx, cy), cell // 2 - 6, 2)
        pygame.draw.circle(screen, TEXT, (cx - 4, cy - 2), 2)
        pygame.draw.circle(screen, TEXT, (cx + 4, cy - 2), 2)

        h1 = get_font(14).render(t("sokoban.help1"), True, TEXT)
        h2 = get_font(14).render(t("sokoban.help2"), True, TEXT)
        screen.blit(h1, h1.get_rect(midbottom=(common.SCREEN_W // 2, common.SCREEN_H - 28)))
        screen.blit(h2, h2.get_rect(midbottom=(common.SCREEN_W // 2, common.SCREEN_H - 10)))

        if complete:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            cx2, cy2 = common.SCREEN_W // 2, common.SCREEN_H // 2
            is_last = level_idx == len(LEVELS) - 1
            msg = t("sokoban.all_done") if is_last else t("sokoban.complete")
            t1 = get_font(34, bold=True).render(t("ui.well_done"), True, TEXT)
            s1 = get_font(20).render(msg, True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx2, cy2 - 20)))
            screen.blit(s1, s1.get_rect(center=(cx2, cy2 + 30)))

        pygame.display.flip()

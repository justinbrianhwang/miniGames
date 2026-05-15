import math
import random

import pygame

from . import common, audio
from .common import t, get_font

# Healing palette
BG = (250, 244, 232)
CARD_BACK = (200, 222, 240)
CARD_BACK_HOVER = (220, 235, 248)
CARD_FACE = (250, 240, 225)
CARD_MATCH = (210, 240, 215)
CARD_BORDER = (180, 165, 145)
TEXT = (95, 80, 75)

# 12 pastel icon colors
ICON_COLORS = [
    (235, 145, 145),  # 0 coral
    (245, 195, 110),  # 1 amber
    (240, 220, 110),  # 2 yellow
    (180, 215, 145),  # 3 sage
    (140, 200, 200),  # 4 mint
    (160, 195, 235),  # 5 blue
    (200, 175, 230),  # 6 lavender
    (240, 175, 210),  # 7 rose
    (245, 215, 175),  # 8 peach
    (210, 230, 140),  # 9 lime
    (180, 220, 235),  # 10 sky
    (215, 175, 200),  # 11 plum
]

# Stages: (rows, cols). Each stage uses (rows*cols)//2 pairs from the icon set (max 12).
STAGES = [
    (2, 3),   # 3 pairs
    (3, 4),   # 6 pairs
    (4, 4),   # 8 pairs
    (4, 5),   # 10 pairs
    (4, 6),   # 12 pairs
]

GRID_TOP = 130
GRID_BOTTOM = common.SCREEN_H - 70
GRID_LEFT = 30
GRID_RIGHT = common.SCREEN_W - 30
PAD = 10


def _draw_icon(screen, kind, cx, cy, color, s):
    s = max(4, s)
    if kind == 0:  # heart
        pygame.draw.circle(screen, color, (cx - s // 2, cy - s // 4), s // 2)
        pygame.draw.circle(screen, color, (cx + s // 2, cy - s // 4), s // 2)
        pygame.draw.polygon(screen, color, [
            (cx - s, cy - s // 6), (cx + s, cy - s // 6), (cx, cy + s)
        ])
    elif kind == 1:  # star
        pts = []
        for i in range(10):
            r = s if i % 2 == 0 else s // 2
            a = math.pi / 2 + i * math.pi / 5
            pts.append((cx + math.cos(a) * r, cy - math.sin(a) * r))
        pygame.draw.polygon(screen, color, pts)
    elif kind == 2:  # circle
        pygame.draw.circle(screen, color, (cx, cy), s)
    elif kind == 3:  # square
        pygame.draw.rect(screen, color, (cx - s, cy - s, 2 * s, 2 * s), border_radius=max(2, s // 4))
    elif kind == 4:  # triangle
        pygame.draw.polygon(screen, color, [
            (cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)
        ])
    elif kind == 5:  # diamond
        pygame.draw.polygon(screen, color, [
            (cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)
        ])
    elif kind == 6:  # hexagon
        pts = []
        for i in range(6):
            a = i * math.pi / 3
            pts.append((cx + math.cos(a) * s, cy + math.sin(a) * s))
        pygame.draw.polygon(screen, color, pts)
    elif kind == 7:  # flower
        for i in range(5):
            a = math.pi / 2 + i * 2 * math.pi / 5
            px = cx + math.cos(a) * s * 0.6
            py = cy - math.sin(a) * s * 0.6
            pygame.draw.circle(screen, color, (int(px), int(py)), s // 2)
        pygame.draw.circle(screen, (250, 240, 225), (cx, cy), max(2, s // 3))
    elif kind == 8:  # cloud
        pygame.draw.circle(screen, color, (cx - s // 2, cy + s // 4), int(s * 0.6))
        pygame.draw.circle(screen, color, (cx + s // 2, cy + s // 4), int(s * 0.6))
        pygame.draw.circle(screen, color, (cx, cy - s // 3), int(s * 0.7))
    elif kind == 9:  # drop
        pygame.draw.circle(screen, color, (cx, cy + s // 3), max(3, int(s * 0.7)))
        pygame.draw.polygon(screen, color, [
            (cx - int(s * 0.6), cy + s // 3),
            (cx + int(s * 0.6), cy + s // 3),
            (cx, cy - s)
        ])
    elif kind == 10:  # ring
        pygame.draw.circle(screen, color, (cx, cy), s, max(3, s // 3))
    elif kind == 11:  # bow tie
        pygame.draw.polygon(screen, color, [
            (cx - s, cy - s), (cx, cy), (cx - s, cy + s),
        ])
        pygame.draw.polygon(screen, color, [
            (cx + s, cy - s), (cx, cy), (cx + s, cy + s),
        ])


def _build_grid(rows, cols):
    avail_w = GRID_RIGHT - GRID_LEFT
    avail_h = GRID_BOTTOM - GRID_TOP
    card_w = (avail_w - (cols + 1) * PAD) / cols
    card_h = (avail_h - (rows + 1) * PAD) / rows
    grid_w = cols * card_w + (cols + 1) * PAD
    grid_h = rows * card_h + (rows + 1) * PAD
    ox = (common.SCREEN_W - grid_w) // 2
    oy = GRID_TOP + (avail_h - grid_h) // 2
    rects = []
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(
                int(ox + PAD + c * (card_w + PAD)),
                int(oy + PAD + r * (card_h + PAD)),
                int(card_w),
                int(card_h),
            )
            rects.append(rect)
    return rects, int(card_w), int(card_h)


def run(screen, clock):
    stage_idx = 0
    cards = []
    rects = []
    card_w = card_h = 0
    pairs = 0
    first_idx = None
    second_idx = None
    mismatch_until = 0
    moves = 0
    matches = 0
    stage_clear = False
    all_done = False
    start_ms = 0

    def load_stage(idx):
        nonlocal stage_idx, cards, rects, card_w, card_h, pairs
        nonlocal first_idx, second_idx, mismatch_until, moves, matches, stage_clear, all_done, start_ms
        stage_idx = idx % len(STAGES)
        rows, cols = STAGES[stage_idx]
        rects, card_w, card_h = _build_grid(rows, cols)
        pairs = (rows * cols) // 2
        values = list(range(pairs)) * 2
        random.shuffle(values)
        cards = []
        for i, v in enumerate(values):
            cards.append({"value": v, "rect": rects[i], "revealed": False, "matched": False})
        first_idx = None
        second_idx = None
        mismatch_until = 0
        moves = 0
        matches = 0
        stage_clear = False
        all_done = False
        start_ms = pygame.time.get_ticks()

    load_stage(0)

    while True:
        clock.tick(common.FPS)
        now = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

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
                    load_stage(stage_idx)
                elif event.key in (pygame.K_n, pygame.K_SPACE) and stage_clear:
                    if stage_idx + 1 < len(STAGES):
                        load_stage(stage_idx + 1)
                    else:
                        load_stage(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not stage_clear:
                if mismatch_until > now:
                    continue
                for i, card in enumerate(cards):
                    if card["matched"] or card["revealed"]:
                        continue
                    if card["rect"].collidepoint(mouse_pos):
                        card["revealed"] = True
                        if first_idx is None:
                            first_idx = i
                        else:
                            second_idx = i
                            moves += 1
                            a = cards[first_idx]
                            b = cards[second_idx]
                            if a["value"] == b["value"]:
                                a["matched"] = True
                                b["matched"] = True
                                matches += 1
                                first_idx = None
                                second_idx = None
                                if matches == pairs:
                                    stage_clear = True
                                    if stage_idx == len(STAGES) - 1:
                                        all_done = True
                            else:
                                mismatch_until = now + 700
                        break

        if (mismatch_until and now >= mismatch_until and first_idx is not None
                and second_idx is not None):
            cards[first_idx]["revealed"] = False
            cards[second_idx]["revealed"] = False
            first_idx = None
            second_idx = None
            mismatch_until = 0

        # Draw
        screen.fill(BG)

        title = get_font(28, bold=True).render(t("game.memory.name"), True, TEXT)
        screen.blit(title, (GRID_LEFT, 50))

        font = get_font(18, bold=True)
        small = get_font(13)
        lvl = font.render(f"{t('sokoban.level')}: {stage_idx + 1}/{len(STAGES)}", True, TEXT)
        screen.blit(lvl, (GRID_LEFT, 88))

        if stage_clear:
            elapsed = (start_ms or now) // 1000  # placeholder
            elapsed = max(0, (now - start_ms) // 1000)
        else:
            elapsed = max(0, (now - start_ms) // 1000)
        moves_t = font.render(f"{t('ui.moves')}: {moves}", True, TEXT)
        time_t = font.render(f"{t('ui.time')}: {elapsed}s", True, TEXT)
        screen.blit(moves_t, (common.SCREEN_W - moves_t.get_width() - GRID_LEFT, 50))
        screen.blit(time_t, (common.SCREEN_W - time_t.get_width() - GRID_LEFT, 78))

        icon_scale = min(card_w, card_h) * 0.32

        for i, card in enumerate(cards):
            r = card["rect"]
            if card["matched"]:
                bg = CARD_MATCH
            elif card["revealed"]:
                bg = CARD_FACE
            else:
                hover = r.collidepoint(mouse_pos) and mismatch_until <= now
                bg = CARD_BACK_HOVER if hover else CARD_BACK
            pygame.draw.rect(screen, bg, r, border_radius=8)
            pygame.draw.rect(screen, CARD_BORDER, r, 2, border_radius=8)
            if card["revealed"] or card["matched"]:
                color = ICON_COLORS[card["value"] % len(ICON_COLORS)]
                _draw_icon(screen, card["value"] % 12, r.centerx, r.centery, color, int(icon_scale))

        help_t = small.render(t("memory.help"), True, TEXT)
        screen.blit(help_t, help_t.get_rect(midbottom=(common.SCREEN_W // 2, common.SCREEN_H - 10)))

        if stage_clear:
            overlay = pygame.Surface((common.SCREEN_W, common.SCREEN_H), pygame.SRCALPHA)
            overlay.fill((250, 244, 232, 200))
            screen.blit(overlay, (0, 0))
            cx, cy = common.SCREEN_W // 2, common.SCREEN_H // 2
            head = t("memory.cleared") if all_done else t("ui.well_done")
            t1 = get_font(42, bold=True).render(head, True, TEXT)
            s1 = font.render(f"{t('ui.moves')}: {moves}   {t('ui.time')}: {elapsed}s", True, TEXT)
            hint = "R / N / ESC"
            r1 = small.render(hint, True, TEXT)
            screen.blit(t1, t1.get_rect(center=(cx, cy - 30)))
            screen.blit(s1, s1.get_rect(center=(cx, cy + 20)))
            screen.blit(r1, r1.get_rect(center=(cx, cy + 60)))

        pygame.display.flip()

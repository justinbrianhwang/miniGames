"""Mini Game Arcade launcher."""
import os
import sys

import pygame

from games import common, audio
from games.common import t, get_font, get_font_for, set_lang, get_lang, LANGUAGES, LANGUAGE_LABELS
from games import (
    suika, snake, breakout, tetris, game2048,
    pong, memory, minesweeper, flappy, sokoban, invaders, doodle, pacman,
)


HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC_FILE = os.path.join(HERE, "별 헤는 오르골.mp3")

GAMES = [
    ("game.suika.name",       "game.suika.desc",       suika.run),
    ("game.snake.name",       "game.snake.desc",       snake.run),
    ("game.breakout.name",    "game.breakout.desc",    breakout.run),
    ("game.tetris.name",      "game.tetris.desc",      tetris.run),
    ("game.2048.name",        "game.2048.desc",        game2048.run),
    ("game.pong.name",        "game.pong.desc",        pong.run),
    ("game.memory.name",      "game.memory.desc",      memory.run),
    ("game.minesweeper.name", "game.minesweeper.desc", minesweeper.run),
    ("game.flappy.name",      "game.flappy.desc",      flappy.run),
    ("game.sokoban.name",     "game.sokoban.desc",     sokoban.run),
    ("game.invaders.name",    "game.invaders.desc",    invaders.run),
    ("game.doodle.name",      "game.doodle.desc",      doodle.run),
    ("game.pacman.name",      "game.pacman.desc",      pacman.run),
]

# 2-column card grid
CARD_COLS = 2
CARD_W = 270
CARD_H = 62
CARD_H_GAP = 14
CARD_V_GAP = 8
GRID_START_Y = 130

MUTE_BTN_RECT = pygame.Rect(common.SCREEN_W - 56, 16, 40, 40)


def _build_layout():
    grid_w = CARD_COLS * CARD_W + (CARD_COLS - 1) * CARD_H_GAP
    start_x = (common.SCREEN_W - grid_w) // 2
    cards = []
    for i in range(len(GAMES)):
        r = i // CARD_COLS
        c = i % CARD_COLS
        rect = pygame.Rect(
            start_x + c * (CARD_W + CARD_H_GAP),
            GRID_START_Y + r * (CARD_H + CARD_V_GAP),
            CARD_W,
            CARD_H,
        )
        cards.append({"rect": rect, "index": i})

    lang_btn_w = 100
    lang_btn_h = 32
    lang_gap = 8
    total_w = len(LANGUAGES) * lang_btn_w + (len(LANGUAGES) - 1) * lang_gap
    lang_x0 = (common.SCREEN_W - total_w) // 2
    lang_y = common.SCREEN_H - 50
    lang_buttons = []
    for i, lang in enumerate(LANGUAGES):
        rect = pygame.Rect(lang_x0 + i * (lang_btn_w + lang_gap), lang_y, lang_btn_w, lang_btn_h)
        lang_buttons.append({"rect": rect, "lang": lang})
    return cards, lang_buttons


def run_menu(screen, clock):
    cards, lang_buttons = _build_layout()

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    audio.toggle_mute()
                elif event.key == pygame.K_ESCAPE:
                    return "quit", None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if MUTE_BTN_RECT.collidepoint(mouse_pos):
                    audio.toggle_mute()
                    continue
                for lb in lang_buttons:
                    if lb["rect"].collidepoint(mouse_pos):
                        set_lang(lb["lang"])
                for c in cards:
                    if c["rect"].collidepoint(mouse_pos):
                        return "game", c["index"]

        # Draw
        screen.fill(common.BG)

        title = get_font(40, bold=True).render(t("app.title"), True, common.TEXT)
        screen.blit(title, title.get_rect(center=(common.SCREEN_W // 2, 56)))

        sub = get_font(15).render(t("app.subtitle"), True, common.DIM)
        screen.blit(sub, sub.get_rect(center=(common.SCREEN_W // 2, 92)))

        name_font = get_font(20, bold=True)
        desc_font = get_font(12)
        for c in cards:
            hover = c["rect"].collidepoint(mouse_pos)
            col = common.PANEL_HOVER if hover else common.PANEL
            pygame.draw.rect(screen, col, c["rect"], border_radius=10)
            pygame.draw.rect(screen, common.TEXT, c["rect"], 2, border_radius=10)
            name_key, desc_key, _ = GAMES[c["index"]]
            name = name_font.render(t(name_key), True, common.TEXT)
            desc = desc_font.render(t(desc_key), True, common.TEXT)
            screen.blit(name, (c["rect"].x + 14, c["rect"].y + 8))
            screen.blit(desc, (c["rect"].x + 14, c["rect"].y + 38))

        lang_label = get_font(13).render(t("app.language"), True, common.DIM)
        screen.blit(lang_label, lang_label.get_rect(midbottom=(common.SCREEN_W // 2, lang_buttons[0]["rect"].y - 4)))
        current = get_lang()
        for lb in lang_buttons:
            active = (lb["lang"] == current)
            hover = lb["rect"].collidepoint(mouse_pos)
            if active:
                bg = common.ACCENT
                fg = common.TEXT_LIGHT
                border = common.ACCENT_DARK
            elif hover:
                bg = common.PANEL_HOVER
                fg = common.TEXT
                border = common.TEXT
            else:
                bg = common.PANEL
                fg = common.TEXT
                border = common.DIM
            pygame.draw.rect(screen, bg, lb["rect"], border_radius=6)
            pygame.draw.rect(screen, border, lb["rect"], 2, border_radius=6)
            label_font = get_font_for(lb["lang"], 14, bold=True)
            label = label_font.render(LANGUAGE_LABELS[lb["lang"]], True, fg)
            screen.blit(label, label.get_rect(center=lb["rect"].center))

        audio.draw_speaker_icon(screen, MUTE_BTN_RECT, hover=MUTE_BTN_RECT.collidepoint(mouse_pos))
        hint = get_font(11).render("M", True, common.DIM)
        screen.blit(hint, hint.get_rect(midtop=(MUTE_BTN_RECT.centerx, MUTE_BTN_RECT.bottom + 1)))

        pygame.display.flip()
        clock.tick(common.FPS)


def main():
    pygame.init()
    screen = pygame.display.set_mode((common.SCREEN_W, common.SCREEN_H))
    pygame.display.set_caption(t("app.title"))
    clock = pygame.time.Clock()

    audio.init(MUSIC_FILE)

    while True:
        action, payload = run_menu(screen, clock)
        if action == "quit":
            break
        if action == "game":
            name_key, _, run_fn = GAMES[payload]
            pygame.display.set_caption(t(name_key))
            result = run_fn(screen, clock)
            pygame.display.set_caption(t("app.title"))
            if result == "quit":
                break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

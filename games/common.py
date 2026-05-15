"""Shared screen size, colors, and small widgets."""
import pygame

from .i18n import get_font, get_font_for, t, set_lang, get_lang, LANGUAGES, LANGUAGE_LABELS

SCREEN_W = 600
SCREEN_H = 760
FPS = 60

# Palette
BG = (245, 235, 220)
PANEL = (220, 205, 185)
PANEL_HOVER = (240, 225, 205)
TEXT = (60, 50, 40)
TEXT_LIGHT = (255, 245, 230)
ACCENT = (220, 100, 100)
ACCENT_DARK = (170, 60, 60)
DIM = (160, 145, 130)


def post_quit():
    pygame.event.post(pygame.event.Event(pygame.QUIT))


__all__ = [
    "SCREEN_W",
    "SCREEN_H",
    "FPS",
    "BG",
    "PANEL",
    "PANEL_HOVER",
    "TEXT",
    "TEXT_LIGHT",
    "ACCENT",
    "ACCENT_DARK",
    "DIM",
    "get_font",
    "get_font_for",
    "t",
    "set_lang",
    "get_lang",
    "LANGUAGES",
    "LANGUAGE_LABELS",
    "post_quit",
]

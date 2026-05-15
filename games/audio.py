"""Background music. Loaded once at app start and looped across menu + games."""
import os

import pygame

_loaded = False
_muted = False
_volume = 0.5


def init(music_path):
    """Initialize mixer and load music. Safe to call once at app start."""
    global _loaded
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error:
            return False
    if not os.path.exists(music_path):
        return False
    try:
        pygame.mixer.music.load(music_path)
        _loaded = True
        pygame.mixer.music.set_volume(0.0 if _muted else _volume)
        pygame.mixer.music.play(loops=-1)
    except pygame.error:
        _loaded = False
    return _loaded


def is_loaded():
    return _loaded


def is_muted():
    return _muted


def toggle_mute():
    global _muted
    _muted = not _muted
    if _loaded:
        pygame.mixer.music.set_volume(0.0 if _muted else _volume)


def set_volume(v):
    global _volume
    _volume = max(0.0, min(1.0, v))
    if _loaded and not _muted:
        pygame.mixer.music.set_volume(_volume)


def get_volume():
    return _volume


def draw_speaker_icon(screen, rect, hover=False):
    """Draw a clickable speaker icon inside rect. Reads mute state from this module."""
    from .common import PANEL, PANEL_HOVER, TEXT, ACCENT
    bg = PANEL_HOVER if hover else PANEL
    pygame.draw.rect(screen, bg, rect, border_radius=8)
    pygame.draw.rect(screen, TEXT, rect, 2, border_radius=8)

    cx, cy = rect.center
    s = min(rect.width, rect.height) // 5
    fg = TEXT
    # body (rectangle, left of cone)
    pygame.draw.rect(screen, fg, (cx - s * 2, cy - s, s, s * 2))
    # cone (trapezoid)
    pygame.draw.polygon(screen, fg, [
        (cx - s, cy - s),
        (cx, cy - s * 2),
        (cx, cy + s * 2),
        (cx - s, cy + s),
    ])
    if _muted:
        red = ACCENT
        pygame.draw.line(screen, red, (cx + 2, cy - s * 2), (cx + s * 2 + 2, cy + s * 2), 3)
        pygame.draw.line(screen, red, (cx + 2, cy + s * 2), (cx + s * 2 + 2, cy - s * 2), 3)
    else:
        # two arcs as sound waves
        pygame.draw.arc(screen, fg, (cx, cy - s * 2, s * 2, s * 4), -0.9, 0.9, 2)
        pygame.draw.arc(screen, fg, (cx + s, cy - s * 2 - 2, s * 2, s * 4 + 4), -0.9, 0.9, 2)

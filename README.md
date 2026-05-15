# Mini Game Arcade

파이게임으로 만든 미니 게임 모음. 13개 게임을 하나의 런처에서 실행할 수 있고, 4개 언어(영/한/일/스)와 BGM을 지원합니다.

A pygame-based mini game collection. 13 games launched from a single menu, with 4-language UI (EN / KO / JA / ES) and shared background music.

![Made with pygame](https://img.shields.io/badge/Made%20with-pygame-1f6feb)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776ab)

---

## Games (13)

| # | Name | Genre | Stages |
|---|---|---|---|
| 1 | Suika Game (수박 게임) | Physics merge | ∞ |
| 2 | Snake (스네이크) | Arcade | ∞ |
| 3 | Breakout (벽돌깨기) | Arcade | **10** |
| 4 | Tetris (테트리스) | Puzzle | Level-based |
| 5 | 2048 | Puzzle | ∞ |
| 6 | Pong (퐁) | Arcade vs AI | First to 5 |
| 7 | Memory Cards (메모리 카드) | Memory | **5** (3→6→8→10→12 pairs) |
| 8 | Minesweeper (지뢰찾기) | Logic | 10×10 |
| 9 | Flappy (플래피) | Reaction | ∞ |
| 10 | Sokoban (창고지기) | Puzzle | **20** |
| 11 | Space Invaders (스페이스 인베이더) | Shooter | Waves ∞ |
| 12 | Doodle Jump (두들 점프) | Platformer | ∞ |
| 13 | Pac Walk (팩 워크) | Maze | **4 mazes** |

## Install

Requires Python 3.10+.

```bash
pip install pygame pymunk
```

`pymunk` is only used by the Suika game (2D rigid-body physics); the rest run on plain `pygame`.

## Run

```bash
python main.py
```

A 600×760 window opens with the launcher. Click any card to start a game.

## Controls

**Universal**
- `ESC` — back to menu (or quit from menu)
- `M` — toggle background music
- `R` — restart current game / level (where applicable)

**Per game**
- *Suika / Breakout / Pong / Memory / Minesweeper* — mouse
- *Snake / 2048 / Tetris / Pac Walk / Sokoban / Doodle Jump / Space Invaders* — arrow keys / WASD
- *Flappy* — space or click
- *Sokoban* — `N` next level, `P` previous level
- *Pac Walk / Memory* — `N` next stage after clear

## Languages

Switch from the language buttons at the bottom of the menu. Strings live in [games/i18n.py](games/i18n.py). Per-language font stacks:

| Language | Font stack |
|---|---|
| English / Español | Segoe UI → Arial |
| 한국어 | Malgun Gothic → Gulim → Arial |
| 日本語 | Yu Gothic UI → Meiryo → MS Gothic → Arial |

## Project layout

```
.
├── main.py              # Launcher menu + game dispatch
├── 별 헤는 오르골.mp3   # Background music (looped across menu and games)
└── games/
    ├── __init__.py
    ├── i18n.py          # Translation strings + language-aware fonts
    ├── common.py        # Shared palette, screen size, helpers
    ├── audio.py         # BGM player + mute toggle
    ├── suika.py
    ├── snake.py
    ├── breakout.py
    ├── tetris.py
    ├── game2048.py
    ├── pong.py
    ├── memory.py
    ├── minesweeper.py
    ├── flappy.py
    ├── sokoban.py
    ├── invaders.py
    ├── doodle.py
    └── pacman.py
```

Each game module exposes a single `run(screen, clock)` function. It runs its own event loop and returns `"menu"` (ESC) or `"quit"` (window close); the launcher does the rest.

## Adding a new game

1. Create `games/your_game.py` with `def run(screen, clock): ...` that returns `"menu"` or `"quit"`.
2. Add name/description keys to `games/i18n.py` under all four languages.
3. Register it in the `GAMES` list in [main.py](main.py).

## License

Source code is MIT licensed — see [LICENSE](LICENSE).

The bundled audio file is third-party content with separate rights; see the Audio Asset Notice at the bottom of [LICENSE](LICENSE).

import random

import pygame
import pymunk

from . import common, audio
from .common import t, get_font

WIDTH = common.SCREEN_W
HEIGHT = common.SCREEN_H

WALL_LEFT = 100
WALL_RIGHT = 500
WALL_BOTTOM = 730
CEILING_Y = 160
DROP_Y = 95

GRAVITY = 1200
DROP_COOLDOWN_MS = 350
GRACE_PERIOD_MS = 1500
GAME_OVER_TIME = 2.0

CONTAINER_COLOR = (200, 170, 140)
LINE_COLOR = (220, 100, 100)

FRUITS = [
    {"radius": 14,  "color": (220, 35, 50)},
    {"radius": 20,  "color": (235, 90, 110)},
    {"radius": 28,  "color": (140, 70, 180)},
    {"radius": 36,  "color": (245, 180, 35)},
    {"radius": 46,  "color": (235, 130, 30)},
    {"radius": 58,  "color": (220, 50, 60)},
    {"radius": 70,  "color": (215, 225, 110)},
    {"radius": 82,  "color": (255, 185, 195)},
    {"radius": 96,  "color": (245, 220, 70)},
    {"radius": 110, "color": (160, 215, 100)},
    {"radius": 130, "color": (40, 140, 60)},
]


class Fruit:
    def __init__(self, space, x, y, tier):
        self.tier = tier
        info = FRUITS[tier]
        self.radius = info["radius"]
        self.color = info["color"]
        self.alive = True
        self.merging = False
        self.spawn_ticks = pygame.time.get_ticks()
        self.above_time = 0.0

        mass = 1 + self.radius * 0.05
        moment = pymunk.moment_for_circle(mass, 0, self.radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.2
        self.shape.friction = 0.6
        space.add(self.body, self.shape)

    def remove(self, space):
        if self.alive:
            space.remove(self.body, self.shape)
            self.alive = False

    def draw(self, screen):
        x, y = self.body.position
        pos = (int(x), int(y))
        pygame.draw.circle(screen, self.color, pos, self.radius)
        outline = tuple(max(0, c - 70) for c in self.color)
        pygame.draw.circle(screen, outline, pos, self.radius, 2)
        hl_r = max(2, self.radius // 4)
        hl_pos = (pos[0] - self.radius // 3, pos[1] - self.radius // 3)
        light = tuple(min(255, c + 70) for c in self.color)
        pygame.draw.circle(screen, light, hl_pos, hl_r)


def _make_walls(space):
    for p1, p2 in [
        ((WALL_LEFT, CEILING_Y), (WALL_LEFT, WALL_BOTTOM)),
        ((WALL_RIGHT, CEILING_Y), (WALL_RIGHT, WALL_BOTTOM)),
        ((WALL_LEFT, WALL_BOTTOM), (WALL_RIGHT, WALL_BOTTOM)),
    ]:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, p1, p2, 4)
        shape.elasticity = 0.2
        shape.friction = 0.9
        space.add(body, shape)


def run(screen, clock):
    space = pymunk.Space()
    space.gravity = (0, GRAVITY)
    _make_walls(space)

    fruits = []

    def random_tier():
        return random.randint(0, 4)

    current_tier = random_tier()
    next_tier = random_tier()
    last_drop_ms = -DROP_COOLDOWN_MS
    score = 0
    high_score = 0
    game_over = False

    def reset():
        nonlocal fruits, current_tier, next_tier, last_drop_ms, score, game_over
        for f in fruits:
            f.remove(space)
        fruits = []
        current_tier = random_tier()
        next_tier = random_tier()
        last_drop_ms = -DROP_COOLDOWN_MS
        score = 0
        game_over = False

    while True:
        dt = clock.tick(common.FPS) / 1000.0
        now = pygame.time.get_ticks()
        mouse_x, _ = pygame.mouse.get_pos()
        cur_r = FRUITS[current_tier]["radius"]
        drop_x = max(WALL_LEFT + cur_r + 2, min(WALL_RIGHT - cur_r - 2, mouse_x))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    audio.toggle_mute()
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
                elif event.key == pygame.K_r and game_over:
                    reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if event.button == 1 and now - last_drop_ms > DROP_COOLDOWN_MS:
                    fruits.append(Fruit(space, drop_x, DROP_Y, current_tier))
                    current_tier = next_tier
                    next_tier = random_tier()
                    last_drop_ms = now

        if not game_over:
            space.step(1 / common.FPS)

        # Merge same-tier fruits in contact
        if not game_over:
            n = len(fruits)
            handled = set()
            for i in range(n):
                a = fruits[i]
                if not a.alive or a.merging or id(a) in handled:
                    continue
                for j in range(i + 1, n):
                    b = fruits[j]
                    if not b.alive or b.merging or id(b) in handled:
                        continue
                    if a.tier != b.tier:
                        continue
                    dx = a.body.position.x - b.body.position.x
                    dy = a.body.position.y - b.body.position.y
                    target = a.radius + b.radius + 1
                    if dx * dx + dy * dy <= target * target:
                        a.merging = True
                        b.merging = True
                        handled.add(id(a))
                        handled.add(id(b))
                        mx = (a.body.position.x + b.body.position.x) / 2
                        my = (a.body.position.y + b.body.position.y) / 2
                        if a.tier + 1 < len(FRUITS):
                            new_tier = a.tier + 1
                            fruits.append(Fruit(space, mx, my, new_tier))
                            score += new_tier * (new_tier + 1) // 2
                        else:
                            score += 100
                        break
            for f in fruits:
                if f.merging:
                    f.remove(space)
            fruits = [f for f in fruits if f.alive]

        # Game over check
        if not game_over:
            for f in fruits:
                if now - f.spawn_ticks < GRACE_PERIOD_MS:
                    continue
                if f.body.position.y - f.radius < CEILING_Y:
                    f.above_time += dt
                    if f.above_time >= GAME_OVER_TIME:
                        game_over = True
                        if score > high_score:
                            high_score = score
                        break
                else:
                    f.above_time = max(0.0, f.above_time - dt * 0.5)

        # Draw
        screen.fill(common.BG)

        pygame.draw.line(screen, CONTAINER_COLOR, (WALL_LEFT, CEILING_Y), (WALL_LEFT, WALL_BOTTOM), 6)
        pygame.draw.line(screen, CONTAINER_COLOR, (WALL_RIGHT, CEILING_Y), (WALL_RIGHT, WALL_BOTTOM), 6)
        pygame.draw.line(screen, CONTAINER_COLOR, (WALL_LEFT, WALL_BOTTOM), (WALL_RIGHT, WALL_BOTTOM), 6)
        pygame.draw.line(screen, LINE_COLOR, (WALL_LEFT, CEILING_Y), (WALL_RIGHT, CEILING_Y), 2)

        for f in fruits:
            f.draw(screen)

        if not game_over:
            info = FRUITS[current_tier]
            preview_pos = (int(drop_x), DROP_Y)
            pygame.draw.circle(screen, info["color"], preview_pos, info["radius"])
            outline = tuple(max(0, c - 70) for c in info["color"])
            pygame.draw.circle(screen, outline, preview_pos, info["radius"], 2)
            pygame.draw.line(screen, (200, 180, 160),
                             (int(drop_x), DROP_Y + info["radius"]),
                             (int(drop_x), CEILING_Y), 1)

        font_big = get_font(36, bold=True)
        font = get_font(22)
        font_small = get_font(16)

        score_text = font_big.render(f"{t('ui.score')}: {score}", True, common.TEXT)
        screen.blit(score_text, (12, 10))

        nxt_label = font_small.render(t("ui.next"), True, common.TEXT)
        screen.blit(nxt_label, (WIDTH - 95, 14))
        nxt = FRUITS[next_tier]
        pygame.draw.circle(screen, nxt["color"], (WIDTH - 35, 50), 20)
        outline = tuple(max(0, c - 70) for c in nxt["color"])
        pygame.draw.circle(screen, outline, (WIDTH - 35, 50), 20, 2)

        tip = font_small.render(t("suika.help"), True, common.TEXT)
        screen.blit(tip, tip.get_rect(midbottom=(WIDTH // 2, HEIGHT - 6)))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            t1 = font_big.render(t("ui.game_over"), True, common.TEXT_LIGHT)
            s1 = font.render(f"{t('ui.score')}: {score}", True, common.TEXT_LIGHT)
            h1 = font.render(f"{t('ui.best')}: {high_score}", True, common.TEXT_LIGHT)
            r1 = font_small.render(t("ui.restart_menu"), True, common.TEXT_LIGHT)
            screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
            screen.blit(s1, s1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))
            screen.blit(h1, h1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
            screen.blit(r1, r1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))

        pygame.display.flip()

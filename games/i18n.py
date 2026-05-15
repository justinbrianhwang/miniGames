"""Translations + language-aware fonts."""
import pygame


LANGUAGES = ["en", "ko", "ja", "es"]
LANGUAGE_LABELS = {
    "en": "English",
    "ko": "한국어",
    "ja": "日本語",
    "es": "Español",
}

# System font stack per language (pygame.font.SysFont picks the first available).
LANG_FONTS = {
    "en": "segoeui,arial,helvetica",
    "es": "segoeui,arial,helvetica",
    "ko": "malgungothic,malgun gothic,gulim,arial",
    "ja": "yugothicui,yu gothic ui,yugothic,meiryo,msgothic,arial",
}

_current = "en"
_font_cache = {}


def set_lang(lang):
    global _current
    if lang in LANGUAGES:
        _current = lang


def get_lang():
    return _current


def get_font_for(lang, size, bold=False):
    key = (lang, size, bold)
    if key not in _font_cache:
        name = LANG_FONTS.get(lang, "arial")
        _font_cache[key] = pygame.font.SysFont(name, size, bold=bold)
    return _font_cache[key]


def get_font(size, bold=False):
    return get_font_for(_current, size, bold)


# --- Translations ---
_strings = {
    # App / launcher
    "app.title": {
        "en": "Mini Game Arcade",
        "ko": "미니 게임 아케이드",
        "ja": "ミニゲームアーケード",
        "es": "Arcade de Mini Juegos",
    },
    "app.subtitle": {
        "en": "Choose a game  ·  ESC to quit",
        "ko": "플레이할 게임을 선택하세요  ·  ESC: 종료",
        "ja": "ゲームを選んでください  ·  ESC: 終了",
        "es": "Elige un juego  ·  ESC para salir",
    },
    "app.language": {
        "en": "Language",
        "ko": "언어",
        "ja": "言語",
        "es": "Idioma",
    },

    # Game names
    "game.suika.name": {
        "en": "Suika Game",
        "ko": "수박 게임",
        "ja": "スイカゲーム",
        "es": "Juego de Sandía",
    },
    "game.suika.desc": {
        "en": "Drop fruits, merge same kinds, make a watermelon",
        "ko": "과일을 떨어뜨려 합치고 수박을 만들어보세요",
        "ja": "果物を落として合成し、スイカを作ろう",
        "es": "Suelta frutas, fusiona iguales y crea una sandía",
    },
    "game.snake.name": {
        "en": "Snake",
        "ko": "스네이크",
        "ja": "スネーク",
        "es": "Serpiente",
    },
    "game.snake.desc": {
        "en": "Steer the snake, eat food, grow longer",
        "ko": "뱀을 조종해 먹이를 먹고 길어지세요",
        "ja": "ヘビを操作してエサを食べ、長く伸ばそう",
        "es": "Mueve la serpiente, come comida y crece",
    },
    "game.breakout.name": {
        "en": "Breakout",
        "ko": "벽돌깨기",
        "ja": "ブロック崩し",
        "es": "Rompeladrillos",
    },
    "game.breakout.desc": {
        "en": "Bounce the ball with the paddle to clear bricks",
        "ko": "공을 튕겨 벽돌을 모두 깨세요",
        "ja": "ボールを跳ね返してブロックを全部壊そう",
        "es": "Rebota la pelota con la paleta y rompe los ladrillos",
    },
    "game.tetris.name": {
        "en": "Tetris",
        "ko": "테트리스",
        "ja": "テトリス",
        "es": "Tetris",
    },
    "game.tetris.desc": {
        "en": "Stack blocks and clear lines",
        "ko": "블록을 쌓아 줄을 완성하세요",
        "ja": "ブロックを積んでラインを消そう",
        "es": "Apila bloques y completa líneas",
    },
    "game.2048.name": {
        "en": "2048",
        "ko": "2048",
        "ja": "2048",
        "es": "2048",
    },
    "game.2048.desc": {
        "en": "Combine matching tiles to reach 2048",
        "ko": "같은 숫자 타일을 합쳐 2048을 만드세요",
        "ja": "同じ数字のタイルを合わせて2048を作ろう",
        "es": "Combina fichas iguales para llegar a 2048",
    },

    # Common UI
    "ui.score": {"en": "Score", "ko": "점수", "ja": "スコア", "es": "Puntaje"},
    "ui.best": {"en": "Best", "ko": "최고", "ja": "ベスト", "es": "Récord"},
    "ui.next": {"en": "Next", "ko": "다음", "ja": "次", "es": "Siguiente"},
    "ui.lives": {"en": "Lives", "ko": "목숨", "ja": "ライフ", "es": "Vidas"},
    "ui.level": {"en": "Level", "ko": "레벨", "ja": "レベル", "es": "Nivel"},
    "ui.lines": {"en": "Lines", "ko": "줄", "ja": "ライン", "es": "Líneas"},
    "ui.game_over": {
        "en": "Game Over",
        "ko": "게임 오버",
        "ja": "ゲームオーバー",
        "es": "Fin del Juego",
    },
    "ui.clear": {"en": "Clear!", "ko": "클리어!", "ja": "クリア!", "es": "¡Completado!"},
    "ui.restart_menu": {
        "en": "R: Restart   ESC: Menu",
        "ko": "R: 다시 시작   ESC: 메뉴",
        "ja": "R: リスタート   ESC: メニュー",
        "es": "R: Reiniciar   ESC: Menú",
    },

    # Suika help
    "suika.help": {
        "en": "Mouse: aim  ·  Click: drop  ·  ESC: menu",
        "ko": "마우스: 조준  ·  클릭: 드롭  ·  ESC: 메뉴",
        "ja": "マウス: 狙う  ·  クリック: ドロップ  ·  ESC: メニュー",
        "es": "Ratón: apuntar  ·  Clic: soltar  ·  ESC: menú",
    },

    # Snake help
    "snake.help": {
        "en": "Arrows / WASD to move  ·  ESC: menu",
        "ko": "화살표 / WASD 이동  ·  ESC: 메뉴",
        "ja": "矢印 / WASD で移動  ·  ESC: メニュー",
        "es": "Flechas / WASD para mover  ·  ESC: menú",
    },

    # Breakout help / hints
    "breakout.help": {
        "en": "Mouse: move paddle  ·  ESC: menu",
        "ko": "마우스: 패들 이동  ·  ESC: 메뉴",
        "ja": "マウス: パドル移動  ·  ESC: メニュー",
        "es": "Ratón: mover paleta  ·  ESC: menú",
    },
    "breakout.launch": {
        "en": "Space or Click to launch",
        "ko": "스페이스 또는 클릭으로 발사",
        "ja": "スペースまたはクリックで発射",
        "es": "Espacio o clic para lanzar",
    },

    # Tetris help (two lines)
    "tetris.help1": {
        "en": "←→ move  ·  ↑/X rotate  ·  Z counter",
        "ko": "←→ 이동  ·  ↑/X 회전  ·  Z 역회전",
        "ja": "←→ 移動  ·  ↑/X 回転  ·  Z 逆回転",
        "es": "←→ mover  ·  ↑/X girar  ·  Z reverso",
    },
    "tetris.help2": {
        "en": "↓ soft drop  ·  Space hard drop",
        "ko": "↓ 소프트 드롭  ·  스페이스 하드 드롭",
        "ja": "↓ ソフトドロップ  ·  スペース ハードドロップ",
        "es": "↓ caída suave  ·  Espacio caída dura",
    },
    "tetris.help3": {
        "en": "ESC: menu",
        "ko": "ESC: 메뉴",
        "ja": "ESC: メニュー",
        "es": "ESC: menú",
    },

    # 2048 help
    "2048.help": {
        "en": "Arrows / WASD: move  ·  R: new game  ·  ESC: menu",
        "ko": "화살표 / WASD: 이동  ·  R: 새 게임  ·  ESC: 메뉴",
        "ja": "矢印 / WASD: 移動  ·  R: 新しいゲーム  ·  ESC: メニュー",
        "es": "Flechas / WASD: mover  ·  R: nuevo juego  ·  ESC: menú",
    },
    "2048.continue": {
        "en": "C: Continue   R: New game",
        "ko": "C: 계속하기   R: 새 게임",
        "ja": "C: 続ける   R: 新しいゲーム",
        "es": "C: Continuar   R: Nuevo juego",
    },

    # Healing-tone shared strings
    "ui.try_again": {
        "en": "Try again?", "ko": "다시 해볼까요?",
        "ja": "もう一度?", "es": "¿Otra vez?",
    },
    "ui.well_done": {
        "en": "Well done!", "ko": "잘했어요!",
        "ja": "よくできました!", "es": "¡Bien hecho!",
    },
    "ui.time": {"en": "Time", "ko": "시간", "ja": "タイム", "es": "Tiempo"},
    "ui.moves": {"en": "Moves", "ko": "이동", "ja": "手数", "es": "Movs"},
    "ui.wave": {"en": "Wave", "ko": "웨이브", "ja": "ウェーブ", "es": "Ola"},

    # Pong
    "game.pong.name": {
        "en": "Pong", "ko": "퐁", "ja": "ピン", "es": "Pong",
    },
    "game.pong.desc": {
        "en": "Classic paddle bounce vs the computer",
        "ko": "컴퓨터와 함께 즐기는 클래식 핑퐁",
        "ja": "コンピュータと遊ぶクラシック",
        "es": "Rebote clásico contra la computadora",
    },
    "pong.help": {
        "en": "Mouse: move paddle  ·  First to 5 wins  ·  ESC: menu",
        "ko": "마우스: 패들 이동  ·  먼저 5점 승리  ·  ESC: 메뉴",
        "ja": "マウス: パドル移動  ·  先に5点で勝ち  ·  ESC: メニュー",
        "es": "Ratón: mover paleta  ·  Primero a 5 gana  ·  ESC: menú",
    },
    "pong.you": {"en": "You", "ko": "나", "ja": "あなた", "es": "Tú"},
    "pong.cpu": {"en": "CPU", "ko": "컴퓨터", "ja": "コンピュータ", "es": "PC"},
    "pong.you_win": {
        "en": "You win!", "ko": "이겼어요!",
        "ja": "勝ち!", "es": "¡Ganaste!",
    },
    "pong.cpu_win": {
        "en": "Better luck next time", "ko": "다음에는 꼭!",
        "ja": "次は頑張ろう", "es": "Próxima vez",
    },

    # Memory cards
    "game.memory.name": {
        "en": "Memory Cards", "ko": "메모리 카드",
        "ja": "メモリーカード", "es": "Cartas de Memoria",
    },
    "game.memory.desc": {
        "en": "Flip cards to find matching pairs",
        "ko": "카드를 뒤집어 같은 그림 짝을 맞춰보세요",
        "ja": "カードをめくって同じ絵を見つけよう",
        "es": "Voltea cartas y encuentra parejas iguales",
    },
    "memory.help": {
        "en": "Click cards to flip  ·  R: new game  ·  ESC: menu",
        "ko": "카드 클릭해 뒤집기  ·  R: 새 게임  ·  ESC: 메뉴",
        "ja": "クリックでめくる  ·  R: 新しいゲーム  ·  ESC: メニュー",
        "es": "Clic para voltear  ·  R: nuevo juego  ·  ESC: menú",
    },
    "memory.cleared": {
        "en": "All matched!", "ko": "다 맞췄어요!",
        "ja": "全部そろえました!", "es": "¡Todas encontradas!",
    },

    # Minesweeper
    "game.minesweeper.name": {
        "en": "Minesweeper", "ko": "지뢰찾기",
        "ja": "マインスイーパ", "es": "Buscaminas",
    },
    "game.minesweeper.desc": {
        "en": "Reveal safe tiles, flag the mines",
        "ko": "안전한 칸을 열고 지뢰엔 깃발을 꽂으세요",
        "ja": "安全なマスを開き、地雷に旗を立てよう",
        "es": "Descubre casillas seguras y marca las minas",
    },
    "minesweeper.help": {
        "en": "Left: reveal  ·  Right: flag  ·  R: new game",
        "ko": "좌클릭: 열기  ·  우클릭: 깃발  ·  R: 새 게임",
        "ja": "左: 開く  ·  右: 旗  ·  R: 新しいゲーム",
        "es": "Izq: abrir  ·  Der: marcar  ·  R: nuevo juego",
    },
    "minesweeper.mines": {
        "en": "Mines", "ko": "지뢰", "ja": "地雷", "es": "Minas",
    },
    "minesweeper.cleared": {
        "en": "All clear!", "ko": "모두 안전!",
        "ja": "全部安全!", "es": "¡Todo despejado!",
    },

    # Flappy
    "game.flappy.name": {
        "en": "Flappy", "ko": "플래피",
        "ja": "フラッピー", "es": "Aleteo",
    },
    "game.flappy.desc": {
        "en": "Tap to flap. Slip through the gaps.",
        "ko": "탭해서 날갯짓. 틈 사이를 통과해보세요.",
        "ja": "タップで羽ばたき。すき間を抜けよう。",
        "es": "Toca para aletear. Pasa entre los huecos.",
    },
    "flappy.help": {
        "en": "Space / Click: flap  ·  ESC: menu",
        "ko": "스페이스 / 클릭: 날갯짓  ·  ESC: 메뉴",
        "ja": "スペース / クリック: 羽ばたき  ·  ESC: メニュー",
        "es": "Espacio / Clic: aletear  ·  ESC: menú",
    },
    "flappy.start": {
        "en": "Press Space or Click to start",
        "ko": "스페이스 또는 클릭으로 시작",
        "ja": "スペースまたはクリックで開始",
        "es": "Espacio o clic para empezar",
    },

    # Sokoban
    "game.sokoban.name": {
        "en": "Sokoban", "ko": "창고지기",
        "ja": "倉庫番", "es": "Sokoban",
    },
    "game.sokoban.desc": {
        "en": "Push boxes onto the target spots",
        "ko": "상자를 밀어 목표 지점에 놓아보세요",
        "ja": "箱を押して目印の上に置こう",
        "es": "Empuja las cajas hasta los objetivos",
    },
    "sokoban.help1": {
        "en": "Arrows / WASD: move  ·  R: restart level",
        "ko": "화살표 / WASD: 이동  ·  R: 다시",
        "ja": "矢印 / WASD: 移動  ·  R: やり直し",
        "es": "Flechas / WASD: mover  ·  R: reiniciar",
    },
    "sokoban.help2": {
        "en": "N: next  ·  P: previous  ·  ESC: menu",
        "ko": "N: 다음  ·  P: 이전  ·  ESC: 메뉴",
        "ja": "N: 次  ·  P: 前  ·  ESC: メニュー",
        "es": "N: siguiente  ·  P: anterior  ·  ESC: menú",
    },
    "sokoban.level": {"en": "Level", "ko": "단계", "ja": "ステージ", "es": "Nivel"},
    "sokoban.complete": {
        "en": "Level complete!  Press N for next.",
        "ko": "스테이지 완료! N으로 다음 단계.",
        "ja": "クリア!  N で次へ。",
        "es": "¡Nivel completado!  N para siguiente.",
    },
    "sokoban.all_done": {
        "en": "All levels done!  Wonderful!",
        "ko": "모든 단계 완료! 멋져요!",
        "ja": "全クリア!すごい!",
        "es": "¡Completaste todos!  ¡Estupendo!",
    },

    # Space Invaders
    "game.invaders.name": {
        "en": "Space Invaders", "ko": "스페이스 인베이더",
        "ja": "スペースインベーダー", "es": "Invasores",
    },
    "game.invaders.desc": {
        "en": "Shoot the descending fleet wave by wave",
        "ko": "내려오는 함대를 격추하며 웨이브를 진행하세요",
        "ja": "降りてくる艦隊をウェーブごとに撃ち落とそう",
        "es": "Derriba la flota oleada tras oleada",
    },
    "invaders.help": {
        "en": "←→ move  ·  Space: shoot  ·  ESC: menu",
        "ko": "←→ 이동  ·  스페이스: 발사  ·  ESC: 메뉴",
        "ja": "←→ 移動  ·  スペース: 発射  ·  ESC: メニュー",
        "es": "←→ mover  ·  Espacio: disparar  ·  ESC: menú",
    },

    # Doodle Jump
    "game.doodle.name": {
        "en": "Doodle Jump", "ko": "두들 점프",
        "ja": "ドゥードルジャンプ", "es": "Salto Garabato",
    },
    "game.doodle.desc": {
        "en": "Bounce upward platform by platform",
        "ko": "발판을 밟으며 위로 위로 올라가요",
        "ja": "足場を踏んで上へ上へ",
        "es": "Rebota plataforma a plataforma hacia arriba",
    },
    "doodle.help": {
        "en": "← → / A D: move  ·  ESC: menu",
        "ko": "← → / A D: 이동  ·  ESC: 메뉴",
        "ja": "← → / A D: 移動  ·  ESC: メニュー",
        "es": "← → / A D: mover  ·  ESC: menú",
    },
    "doodle.height": {
        "en": "Height", "ko": "높이", "ja": "高さ", "es": "Altura",
    },

    # Pacman-lite
    "game.pacman.name": {
        "en": "Pac Walk", "ko": "팩 워크",
        "ja": "パックウォーク", "es": "Paseo Pac",
    },
    "game.pacman.desc": {
        "en": "Collect all the dots while dodging the ghost",
        "ko": "유령을 피해 점을 모두 모아보세요",
        "ja": "おばけを避けてドットを全部集めよう",
        "es": "Recoge los puntos esquivando al fantasma",
    },
    "pacman.help": {
        "en": "Arrows / WASD: move  ·  ESC: menu",
        "ko": "화살표 / WASD: 이동  ·  ESC: 메뉴",
        "ja": "矢印 / WASD: 移動  ·  ESC: メニュー",
        "es": "Flechas / WASD: mover  ·  ESC: menú",
    },
    "pacman.dots": {
        "en": "Dots", "ko": "점", "ja": "ドット", "es": "Puntos",
    },
}


def t(key):
    entry = _strings.get(key)
    if not entry:
        return key
    return entry.get(_current) or entry.get("en") or key

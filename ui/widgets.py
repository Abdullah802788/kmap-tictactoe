"""
Custom widgets for the K-Map Tic-Tac-Toe application.

• GameCanvas       — The 3×3 game grid (Canvas-based, neon effects)
• GlowButton       — Themed button with hover glow
• ScorePanel        — Win / Draw / Loss counter
• MoveHistoryPanel  — Scrollable move log
"""

import tkinter as tk
import customtkinter as ctk

from ui.animations import (
    draw_neon_x, draw_neon_o,
    WinLineAnimation, ConfettiAnimation,
)
from core.utils import blend_color, play_sound


# ══════════════════════════════════════════════════════════
#  GAME CANVAS
# ══════════════════════════════════════════════════════════

class GameCanvas(ctk.CTkFrame):
    """Interactive 3×3 Tic-Tac-Toe board with neon glow effects."""

    CELL  = 150       # px per cell
    MARK  = 40        # half-size of drawn mark
    SIZE  = 450       # total canvas side (3 × CELL)

    def __init__(self, master, theme, on_cell_click=None, **kw):
        super().__init__(master, **kw)
        self.theme         = theme
        self.on_cell_click = on_cell_click
        self.board_state   = [None] * 9   # None / 'X' / 'O'
        self._hover        = -1
        self.enabled       = True
        self._win_anim: WinLineAnimation | None  = None
        self._confetti: ConfettiAnimation | None  = None

        self.canvas = tk.Canvas(
            self, width=self.SIZE, height=self.SIZE,
            highlightthickness=0, cursor='hand2',
        )
        self.canvas.pack(padx=10, pady=10)

        self.canvas.bind('<Motion>',   self._on_motion)
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<Leave>',    self._on_leave)

        self._draw_board()

    # ── geometry helpers ─────────────────────────────────

    def _cell_of(self, x, y) -> int:
        c, r = x // self.CELL, y // self.CELL
        return r * 3 + c if 0 <= r < 3 and 0 <= c < 3 else -1

    def _center_of(self, idx) -> tuple[int, int]:
        r, c = divmod(idx, 3)
        return c * self.CELL + self.CELL // 2, r * self.CELL + self.CELL // 2

    # ── full board redraw ────────────────────────────────

    def _draw_board(self):
        self.canvas.delete('bg', 'grid', 'mark')
        bg = self.theme.get('cell_bg')
        self.canvas.configure(bg=bg)

        # cell backgrounds
        for i in range(9):
            r, c = divmod(i, 3)
            x1 = c * self.CELL + 2
            y1 = r * self.CELL + 2
            x2 = x1 + self.CELL - 4
            y2 = y1 + self.CELL - 4
            fill = bg
            if i == self._hover and self.board_state[i] is None and self.enabled:
                fill = self.theme.get('cell_hover')
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=fill, outline='', tags='bg',
            )

        # grid lines with glow
        line_c = self.theme.get('grid_line')
        glow_c = self.theme.get('accent_purple')
        for k in (1, 2):
            pos = k * self.CELL
            glow = blend_color(glow_c, bg, 0.15)
            # vertical
            self.canvas.create_line(pos, 5, pos, self.SIZE - 5,
                                    fill=glow, width=6, tags='grid')
            self.canvas.create_line(pos, 5, pos, self.SIZE - 5,
                                    fill=line_c, width=2, tags='grid')
            # horizontal
            self.canvas.create_line(5, pos, self.SIZE - 5, pos,
                                    fill=glow, width=6, tags='grid')
            self.canvas.create_line(5, pos, self.SIZE - 5, pos,
                                    fill=line_c, width=2, tags='grid')

        # marks
        for i in range(9):
            cx, cy = self._center_of(i)
            if self.board_state[i] == 'X':
                draw_neon_x(self.canvas, cx, cy, self.MARK,
                            self.theme.get('x_color'), bg, tag='mark')
            elif self.board_state[i] == 'O':
                draw_neon_o(self.canvas, cx, cy, self.MARK,
                            self.theme.get('o_color'), bg, tag='mark')

    # ── events ───────────────────────────────────────────

    def _on_motion(self, e):
        cell = self._cell_of(e.x, e.y)
        if cell != self._hover:
            self._hover = cell
            self._draw_board()

    def _on_leave(self, _e):
        self._hover = -1
        self._draw_board()

    def _on_click(self, e):
        if not self.enabled:
            return
        cell = self._cell_of(e.x, e.y)
        if cell >= 0 and self.board_state[cell] is None:
            play_sound('click')
            if self.on_cell_click:
                self.on_cell_click(cell)

    # ── public API ───────────────────────────────────────

    def place_mark(self, cell: int, mark: str):
        self.board_state[cell] = mark
        play_sound('place')
        self._draw_board()

    def show_win_line(self, line, on_complete=None):
        if not line or len(line) != 3:
            return
        s = self._center_of(line[0])
        e = self._center_of(line[2])
        self._win_anim = WinLineAnimation(
            self.canvas, s, e,
            self.theme.get('win_glow'),
            self.theme.get('cell_bg'),
            on_complete=on_complete,
        )
        self._win_anim.start()

    def show_confetti(self):
        if self._confetti:
            self._confetti.stop()
        self._confetti = ConfettiAnimation(self.canvas, 55)
        self._confetti.start()

    def reset(self):
        if self._win_anim:
            self._win_anim.stop()
            self._win_anim = None
        if self._confetti:
            self._confetti.stop()
            self._confetti = None
        self.board_state = [None] * 9
        self._hover = -1
        self.enabled = True
        self._draw_board()

    def set_enabled(self, on: bool):
        self.enabled = on
        self.canvas.configure(cursor='hand2' if on else 'arrow')

    def refresh_theme(self):
        self._draw_board()


# ══════════════════════════════════════════════════════════
#  GLOW BUTTON
# ══════════════════════════════════════════════════════════

class GlowButton(ctk.CTkButton):
    """Themed button with primary / secondary styling."""

    def __init__(self, master, theme, text="", command=None,
                 primary=True, width=250, height=45, **kw):
        self.theme   = theme
        self.primary = primary
        bg    = theme.get('button_bg' if primary else 'button_secondary_bg')
        hover = theme.get('button_hover' if primary else 'button_secondary_hover')
        super().__init__(
            master, text=text, command=command,
            width=width, height=height, corner_radius=12,
            fg_color=bg, hover_color=hover,
            text_color=theme.get('button_text'),
            font=ctk.CTkFont(size=15, weight="bold"),
            **kw,
        )

    def refresh_theme(self):
        p = self.primary
        self.configure(
            fg_color=self.theme.get('button_bg' if p else 'button_secondary_bg'),
            hover_color=self.theme.get('button_hover' if p else 'button_secondary_hover'),
            text_color=self.theme.get('button_text'),
        )


# ══════════════════════════════════════════════════════════
#  SCORE PANEL
# ══════════════════════════════════════════════════════════

class ScorePanel(ctk.CTkFrame):
    """Compact score display."""

    def __init__(self, master, theme, **kw):
        super().__init__(master, **kw)
        self.theme = theme
        self.configure(fg_color=theme.get('panel'), corner_radius=12)

        self._title = ctk.CTkLabel(
            self, text="⚡ SCOREBOARD",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.get('accent_cyan'),
        )
        self._title.pack(pady=(10, 4))

        row = ctk.CTkFrame(self, fg_color='transparent')
        row.pack(pady=(0, 10), padx=12, fill='x')

        self._pl = ctk.CTkLabel(row, text="You: 0",
                                font=ctk.CTkFont(size=13),
                                text_color=theme.get('text_primary'))
        self._pl.pack(side='left', expand=True)

        self._dr = ctk.CTkLabel(row, text="Draw: 0",
                                font=ctk.CTkFont(size=13),
                                text_color=theme.get('text_secondary'))
        self._dr.pack(side='left', expand=True)

        self._ai = ctk.CTkLabel(row, text="AI: 0",
                                font=ctk.CTkFont(size=13),
                                text_color=theme.get('accent_pink'))
        self._ai.pack(side='left', expand=True)

    def update_score(self, player: int, ai: int, draws: int):
        self._pl.configure(text=f"You: {player}")
        self._ai.configure(text=f"AI: {ai}")
        self._dr.configure(text=f"Draw: {draws}")

    def refresh_theme(self):
        self.configure(fg_color=self.theme.get('panel'))
        self._title.configure(text_color=self.theme.get('accent_cyan'))
        self._pl.configure(text_color=self.theme.get('text_primary'))
        self._dr.configure(text_color=self.theme.get('text_secondary'))
        self._ai.configure(text_color=self.theme.get('accent_pink'))


# ══════════════════════════════════════════════════════════
#  MOVE HISTORY PANEL
# ══════════════════════════════════════════════════════════

class MoveHistoryPanel(ctk.CTkFrame):
    """Scrollable log of moves played."""

    def __init__(self, master, theme, **kw):
        super().__init__(master, **kw)
        self.theme = theme
        self.configure(fg_color=theme.get('panel'), corner_radius=12)

        self._title = ctk.CTkLabel(
            self, text="\U0001f4cb MOVE HISTORY",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.get('accent_cyan'),
        )
        self._title.pack(pady=(10, 4))

        self._text = ctk.CTkTextbox(
            self, width=220, height=200,
            font=ctk.CTkFont(size=12),
            fg_color=theme.get('bg_secondary'),
            text_color=theme.get('text_secondary'),
            corner_radius=8, state='disabled',
        )
        self._text.pack(padx=8, pady=(0, 8), fill='both', expand=True)

    def add_move(self, player: str, cell: int, strategy: str | None = None):
        r, c = divmod(cell, 3)
        arrow = '\u2192' if player == 'AI' else '\u2022'
        line = f" {arrow} {player}: ({r},{c})"
        if strategy:
            line += f"  [{strategy}]"
        line += "\n"
        self._text.configure(state='normal')
        self._text.insert('end', line)
        self._text.see('end')
        self._text.configure(state='disabled')

    def clear(self):
        self._text.configure(state='normal')
        self._text.delete('1.0', 'end')
        self._text.configure(state='disabled')

    def refresh_theme(self):
        self.configure(fg_color=self.theme.get('panel'))
        self._title.configure(text_color=self.theme.get('accent_cyan'))
        self._text.configure(
            fg_color=self.theme.get('bg_secondary'),
            text_color=self.theme.get('text_secondary'),
        )

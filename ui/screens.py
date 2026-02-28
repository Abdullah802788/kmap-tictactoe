"""
Screen definitions for the K-Map Tic-Tac-Toe application.

• StartScreen       — Main menu / landing page
• GameScreen        — Active gameplay
• HowItWorksScreen  — K-map / Boolean-logic explainer
"""

import customtkinter as ctk

from core.board import Board
from core.move_priority import MovePriority
from core.win_logic import check_winner, get_winning_line
from core.utils import play_sound
from ui.widgets import GameCanvas, GlowButton, ScorePanel, MoveHistoryPanel


# ══════════════════════════════════════════════════════════
#  START SCREEN
# ══════════════════════════════════════════════════════════

class StartScreen(ctk.CTkFrame):
    """Landing / main-menu screen."""

    def __init__(self, master, theme, callbacks, **kw):
        super().__init__(master, **kw)
        self.theme = theme
        self.cb    = callbacks
        self._btns: list[GlowButton] = []
        self.configure(fg_color=theme.get('bg'))
        self._build()

    def _build(self):
        # top spacer
        ctk.CTkLabel(self, text="", fg_color='transparent').pack(pady=30)

        # title
        self._title = ctk.CTkLabel(
            self, text="\u26a1  K-MAP TIC TAC TOE  \u26a1",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=self.theme.get('accent_cyan'),
        )
        self._title.pack(pady=(0, 5))

        # subtitle
        self._sub = ctk.CTkLabel(
            self, text="Digital Logic meets Game AI",
            font=ctk.CTkFont(size=18),
            text_color=self.theme.get('text_secondary'),
        )
        self._sub.pack(pady=(0, 8))

        # decorative line
        self._deco = ctk.CTkLabel(
            self,
            text="\u2501" * 22,
            font=ctk.CTkFont(size=14),
            text_color=self.theme.get('accent_purple'),
        )
        self._deco.pack(pady=(0, 30))

        # button column
        col = ctk.CTkFrame(self, fg_color='transparent')
        col.pack()

        def _btn(text, cmd, primary=True):
            b = GlowButton(col, self.theme, text=text,
                           command=cmd, primary=primary)
            b.pack(pady=6)
            self._btns.append(b)

        _btn("\u25b6  Play as X  (First)",  lambda: self.cb['play']('X'))
        _btn("\u25b6  Play as O  (Second)", lambda: self.cb['play']('O'))
        _btn("\U0001f4d6  How It Works",     self.cb['how_it_works'], False)
        _btn("\U0001f3a8  Toggle Theme",     self.cb['toggle_theme'], False)
        _btn("\u2716  Exit",                 self.cb['exit'],         False)

        # flex spacer
        ctk.CTkLabel(self, text="", fg_color='transparent').pack(expand=True)

        # footer
        self._foot = ctk.CTkLabel(
            self,
            text="A Digital Logic Design Demonstration  \u2022  "
                 "Boolean AI powered by K-Map simplification",
            font=ctk.CTkFont(size=11),
            text_color=self.theme.get('text_dim'),
        )
        self._foot.pack(pady=(0, 20))

    def refresh_theme(self):
        self.configure(fg_color=self.theme.get('bg'))
        self._title.configure(text_color=self.theme.get('accent_cyan'))
        self._sub.configure(text_color=self.theme.get('text_secondary'))
        self._deco.configure(text_color=self.theme.get('accent_purple'))
        self._foot.configure(text_color=self.theme.get('text_dim'))
        for b in self._btns:
            b.refresh_theme()


# ══════════════════════════════════════════════════════════
#  GAME SCREEN
# ══════════════════════════════════════════════════════════

class GameScreen(ctk.CTkFrame):
    """Active game-play screen."""

    def __init__(self, master, theme, callbacks, **kw):
        super().__init__(master, **kw)
        self.theme = theme
        self.cb    = callbacks

        # game state
        self.board        = Board()
        self.ai: MovePriority | None = None
        self.player_mark  = 'X'
        self.ai_mark      = 'O'
        self.current_turn  = 'X'
        self.game_over    = False
        self.thinking     = False

        # scores (persist across restarts within session)
        self._pw = 0    # player wins
        self._aw = 0    # AI wins
        self._dw = 0    # draws

        # pending after-IDs
        self._ai_after:       str | None = None
        self._think_after:    str | None = None

        self.configure(fg_color=theme.get('bg'))
        self._build()

    # ── UI construction ──────────────────────────────────

    def _build(self):
        # — top bar —
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=15, pady=(10, 5))

        self._btn_back = GlowButton(
            top, self.theme, text="\u2190 Menu",
            command=self._go_back,
            primary=False, width=100, height=35,
        )
        self._btn_back.pack(side='left')

        self._lbl_turn = ctk.CTkLabel(
            top, text="Your Turn",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.theme.get('accent_cyan'),
        )
        self._lbl_turn.pack(side='left', expand=True)

        self._lbl_match = ctk.CTkLabel(
            top, text="You (X) vs AI (O)",
            font=ctk.CTkFont(size=14),
            text_color=self.theme.get('text_secondary'),
        )
        self._lbl_match.pack(side='right', padx=10)

        # — main content —
        body = ctk.CTkFrame(self, fg_color='transparent')
        body.pack(expand=True, fill='both', padx=10, pady=5)

        # left panel: move history
        left = ctk.CTkFrame(body, fg_color='transparent', width=240)
        left.pack(side='left', fill='y', padx=(5, 5))
        left.pack_propagate(False)
        self._history = MoveHistoryPanel(left, self.theme)
        self._history.pack(fill='both', expand=True)

        # centre: board
        mid = ctk.CTkFrame(body, fg_color='transparent')
        mid.pack(side='left', expand=True)
        self._board_ui = GameCanvas(
            mid, self.theme,
            on_cell_click=self._on_click,
            fg_color='transparent',
        )
        self._board_ui.pack()

        self._lbl_status = ctk.CTkLabel(
            mid, text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme.get('accent_gold'),
        )
        self._lbl_status.pack(pady=(5, 0))

        self._lbl_reason = ctk.CTkLabel(
            mid, text="",
            font=ctk.CTkFont(size=12),
            text_color=self.theme.get('text_dim'),
        )
        self._lbl_reason.pack(pady=(2, 5))

        # right panel: score + AI info
        right = ctk.CTkFrame(body, fg_color='transparent', width=240)
        right.pack(side='left', fill='y', padx=(5, 5))
        right.pack_propagate(False)

        self._score = ScorePanel(right, self.theme)
        self._score.pack(fill='x', pady=(0, 10))

        self._info_frame = ctk.CTkFrame(
            right, fg_color=self.theme.get('panel'), corner_radius=12,
        )
        self._info_frame.pack(fill='both', expand=True)

        self._info_title = ctk.CTkLabel(
            self._info_frame, text="\U0001f9e0 AI ENGINE",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme.get('accent_cyan'),
        )
        self._info_title.pack(pady=(10, 4))

        self._info_body = ctk.CTkLabel(
            self._info_frame,
            text=(
                "K-Map Boolean Logic\n\n"
                "Priority Pipeline:\n"
                "1. Win\n2. Block\n3. Fork\n"
                "4. Block Fork\n5. Center\n"
                "6. Opp. Corner\n7. Corner\n8. Side"
            ),
            font=ctk.CTkFont(size=11),
            text_color=self.theme.get('text_secondary'),
            justify='left', wraplength=200,
        )
        self._info_body.pack(padx=10, pady=(0, 10))

        # — bottom bar —
        bot = ctk.CTkFrame(self, fg_color='transparent')
        bot.pack(fill='x', padx=15, pady=(5, 10))

        self._btn_restart = GlowButton(
            bot, self.theme, text="\U0001f504 New Round",
            command=self._restart, width=150, height=38,
        )
        self._btn_restart.pack(side='right', padx=5)

    # ── game lifecycle ───────────────────────────────────

    def start_game(self, player_mark: str):
        self._cancel_pending()
        self.player_mark = player_mark
        self.ai_mark     = 'O' if player_mark == 'X' else 'X'
        self.ai          = MovePriority(ai_mark=self.ai_mark)
        self.board.reset()
        self.current_turn = 'X'
        self.game_over   = False
        self.thinking    = False

        self._board_ui.reset()
        self._history.clear()
        self._lbl_status.configure(text="")
        self._lbl_reason.configure(text="")
        self._lbl_match.configure(
            text=f"You ({self.player_mark}) vs AI ({self.ai_mark})",
        )
        self._update_turn_label()
        self._score.update_score(self._pw, self._aw, self._dw)

        # AI first?
        if self.ai_mark == 'X':
            self._board_ui.set_enabled(False)
            self.thinking = True
            self._ai_after = self.after(500, self._do_ai_move)
            self._anim_thinking()

    def _restart(self):
        self.start_game(self.player_mark)

    def _go_back(self):
        self._cancel_pending()
        self.game_over = True
        self.cb['back_to_menu']()

    # ── pending callback management ──────────────────────

    def _cancel_pending(self):
        for attr in ('_ai_after', '_think_after'):
            aid = getattr(self, attr, None)
            if aid is not None:
                try:
                    self.after_cancel(aid)
                except Exception:
                    pass
                setattr(self, attr, None)
        self.thinking = False

    # ── turn display ─────────────────────────────────────

    def _update_turn_label(self):
        if self.game_over:
            return
        if self.current_turn == self.player_mark:
            self._lbl_turn.configure(
                text="\u26a1 Your Turn",
                text_color=self.theme.get('accent_cyan'),
            )
        else:
            self._lbl_turn.configure(
                text="\U0001f9e0 AI Thinking...",
                text_color=self.theme.get('accent_pink'),
            )

    def _anim_thinking(self, n=0):
        if not self.thinking:
            return
        dots = '.' * (n % 3 + 1)
        self._lbl_turn.configure(text=f"\U0001f9e0 AI Thinking{dots}")
        self._think_after = self.after(300, lambda: self._anim_thinking(n + 1))

    # ── player click ─────────────────────────────────────

    def _on_click(self, cell: int):
        if self.game_over or self.thinking:
            return
        if self.current_turn != self.player_mark:
            return
        if not self.board.is_empty(cell):
            return

        self.board.place(cell, self.player_mark)
        self._board_ui.place_mark(cell, self.player_mark)
        self._history.add_move("You", cell)

        if self._check_end():
            return

        self.current_turn = self.ai_mark
        self._update_turn_label()
        self._board_ui.set_enabled(False)
        self.thinking = True
        self._ai_after = self.after(450, self._do_ai_move)
        self._anim_thinking()

    # ── AI move ──────────────────────────────────────────

    def _do_ai_move(self):
        if self.game_over:
            return
        self.thinking = False

        move = self.ai.get_best_move(self.board)
        if move is None:
            return

        self.board.place(move, self.ai_mark)
        self._board_ui.place_mark(move, self.ai_mark)

        reason = self.ai.get_last_reasoning()
        self._history.add_move("AI", move, self.ai.last_priority)
        self._lbl_reason.configure(text=f"AI: {reason}")

        if self._check_end():
            return

        self.current_turn = self.player_mark
        self._update_turn_label()
        self._board_ui.set_enabled(True)

    # ── end-of-game check ────────────────────────────────

    def _check_end(self) -> bool:
        winner = check_winner(self.board)

        if winner:
            self.game_over = True
            self._board_ui.set_enabled(False)
            wl = get_winning_line(self.board)

            if winner == self.player_mark:
                self._pw += 1
                self._lbl_turn.configure(
                    text="\U0001f389 You Win!",
                    text_color=self.theme.get('accent_gold'),
                )
                self._lbl_status.configure(
                    text="Congratulations!",
                    text_color=self.theme.get('accent_gold'),
                )
                play_sound('win')
                self._board_ui.show_win_line(
                    wl, on_complete=self._board_ui.show_confetti,
                )
            else:
                self._aw += 1
                self._lbl_turn.configure(
                    text="\U0001f916 AI Wins!",
                    text_color=self.theme.get('accent_pink'),
                )
                self._lbl_status.configure(
                    text="The K-Map AI is unbeatable!",
                    text_color=self.theme.get('accent_pink'),
                )
                play_sound('lose')
                self._board_ui.show_win_line(wl)

            self._score.update_score(self._pw, self._aw, self._dw)
            return True

        if self.board.is_full():
            self.game_over = True
            self._board_ui.set_enabled(False)
            self._dw += 1
            self._lbl_turn.configure(
                text="\U0001f91d Draw!",
                text_color=self.theme.get('text_secondary'),
            )
            self._lbl_status.configure(
                text="It's a draw — well played!",
                text_color=self.theme.get('text_secondary'),
            )
            play_sound('draw')
            self._score.update_score(self._pw, self._aw, self._dw)
            return True

        return False

    # ── theme refresh ────────────────────────────────────

    def refresh_theme(self):
        self.configure(fg_color=self.theme.get('bg'))
        self._lbl_turn.configure(text_color=self.theme.get('accent_cyan'))
        self._lbl_match.configure(text_color=self.theme.get('text_secondary'))
        self._lbl_status.configure(text_color=self.theme.get('accent_gold'))
        self._lbl_reason.configure(text_color=self.theme.get('text_dim'))
        self._info_frame.configure(fg_color=self.theme.get('panel'))
        self._info_title.configure(text_color=self.theme.get('accent_cyan'))
        self._info_body.configure(text_color=self.theme.get('text_secondary'))
        self._board_ui.refresh_theme()
        self._score.refresh_theme()
        self._history.refresh_theme()
        self._btn_back.refresh_theme()
        self._btn_restart.refresh_theme()


# ══════════════════════════════════════════════════════════
#  HOW IT WORKS SCREEN
# ══════════════════════════════════════════════════════════

class HowItWorksScreen(ctk.CTkFrame):
    """Explainer screen covering K-maps, Boolean logic, and the AI."""

    _TEXT = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        HOW THE K-MAP AI WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔷  WHAT IS A KARNAUGH MAP?

A Karnaugh Map (K-Map) is a method used in
digital logic design to simplify Boolean
algebra expressions.

It converts truth tables into minimal
Sum-of-Products (SOP) or Product-of-Sums
(POS) expressions by visually grouping
adjacent 1s (or 0s) in a grid.

The result: optimally simplified Boolean
logic — directly implementable in hardware
(or software!).


🔷  BOOLEAN BOARD ENCODING

The Tic-Tac-Toe board uses 18 Boolean
variables:

  X0..X8  →  True if cell has X
  O0..O8  →  True if cell has O

Board layout:
  Cell 0 │ Cell 1 │ Cell 2
  ───────┼────────┼───────
  Cell 3 │ Cell 4 │ Cell 5
  ───────┼────────┼───────
  Cell 6 │ Cell 7 │ Cell 8


🔷  WIN DETECTION  (SOP Expression)

A player wins when three marks align.
In Sum-of-Products form:

  WIN_X = (X0·X1·X2) + (X3·X4·X5)
        + (X6·X7·X8) + (X0·X3·X6)
        + (X1·X4·X7) + (X2·X5·X8)
        + (X0·X4·X8) + (X2·X4·X6)

Each product term (AND) represents one
winning line.  The sum (OR) combines all
eight possibilities.

This IS a K-map–simplified SOP expression.


🔷  AI DECISION PIPELINE

The AI evaluates moves using 8 priority
modules, each implemented as Boolean SOP
expressions:

 1️⃣  WIN MODULE
    MOVE_WIN[i] = EMPTY[i] · Σ(AI[j]·AI[k])
    → complete a three-in-a-row

 2️⃣  BLOCK MODULE
    MOVE_BLOCK[i] = EMPTY[i] · Σ(OPP[j]·OPP[k])
    → prevent opponent's three-in-a-row

 3️⃣  FORK MODULE
    FORK[i] = EMPTY[i] · (THREATS[i] ≥ 2)
    → create two simultaneous winning threats

 4️⃣  BLOCK FORK MODULE
    Detects opponent fork cells and plays
    a forcing move to neutralise them.

 5️⃣  CENTER MODULE
    CENTER = ¬X4 · ¬O4
    → simplest possible SOP: one minterm

 6️⃣  OPPOSITE CORNER MODULE
    OPP_CORNER[0] = EMPTY[0] · OPP[8]
    OPP_CORNER[2] = EMPTY[2] · OPP[6]
    OPP_CORNER[6] = EMPTY[6] · OPP[2]
    OPP_CORNER[8] = EMPTY[8] · OPP[0]

 7️⃣  CORNER MODULE
    CORNER = EMPTY[0]+EMPTY[2]+EMPTY[6]+EMPTY[8]

 8️⃣  SIDE MODULE
    SIDE = EMPTY[1]+EMPTY[3]+EMPTY[5]+EMPTY[7]


🔷  WHY K-MAP / BOOLEAN LOGIC?

Traditional Tic-Tac-Toe AIs use game-tree
search (Minimax) and explore all possible
future states.

This AI instead uses pre-derived Boolean
expressions — the same kind of logic that
runs inside digital circuits.

Each decision is a direct evaluation of
AND / OR / NOT on the current board state:

  ✦  Deterministic (no randomness)
  ✦  O(1) decision time
  ✦  Perfect play (never loses)
  ✦  Hardware-implementable

This project demonstrates that K-map
simplification isn't just for circuit
design — it can power real game AI
through pure combinational logic!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def __init__(self, master, theme, callbacks, **kw):
        super().__init__(master, **kw)
        self.theme = theme
        self.cb    = callbacks
        self.configure(fg_color=theme.get('bg'))
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=15, pady=(10, 5))

        self._btn = GlowButton(
            top, self.theme, text="\u2190 Back",
            command=self.cb['back_to_menu'],
            primary=False, width=100, height=35,
        )
        self._btn.pack(side='left')

        self._title = ctk.CTkLabel(
            top, text="\U0001f4d6 How It Works",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.theme.get('accent_cyan'),
        )
        self._title.pack(side='left', expand=True)

        self._txt = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=self.theme.get('bg_secondary'),
            text_color=self.theme.get('text_primary'),
            corner_radius=12, wrap='word',
        )
        self._txt.pack(fill='both', expand=True, padx=20, pady=10)
        self._txt.insert('1.0', self._TEXT)
        self._txt.configure(state='disabled')

    def refresh_theme(self):
        self.configure(fg_color=self.theme.get('bg'))
        self._title.configure(text_color=self.theme.get('accent_cyan'))
        self._txt.configure(
            fg_color=self.theme.get('bg_secondary'),
            text_color=self.theme.get('text_primary'),
        )
        self._btn.refresh_theme()

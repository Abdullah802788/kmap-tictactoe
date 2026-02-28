"""
Main application controller for K-Map Tic-Tac-Toe.

Creates the window, manages screen transitions,
and wires up theme toggling.
"""

import customtkinter as ctk
from ui.themes import ThemeManager
from ui.screens import StartScreen, GameScreen, HowItWorksScreen
from core.utils import generate_sounds


class App:
    """Top-level application."""

    def __init__(self):
        # ── pre-flight ────────────────────────────────────
        generate_sounds()

        # ── theme ─────────────────────────────────────────
        self.theme = ThemeManager()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── window ────────────────────────────────────────
        self.root = ctk.CTk()
        self.root.title("K-Map Tic Tac Toe")
        self.root.geometry("980x720")
        self.root.minsize(820, 620)

        # Try to remove default icon gracefully
        try:
            self.root.iconbitmap(default='')
        except Exception:
            pass

        # ── theme listener ────────────────────────────────
        self.theme.add_listener(self._apply_theme)

        # ── screens ───────────────────────────────────────
        self._screens: dict[str, ctk.CTkFrame] = {}
        self._current: str | None = None
        self._create_screens()
        self._show('start')

    # ── screen creation ──────────────────────────────────

    def _create_screens(self):
        self._screens['start'] = StartScreen(
            self.root, self.theme, {
                'play':         self._play,
                'how_it_works': lambda: self._show('how'),
                'toggle_theme': self._toggle_theme,
                'exit':         self._exit,
            },
        )
        self._screens['game'] = GameScreen(
            self.root, self.theme, {
                'back_to_menu': lambda: self._show('start'),
            },
        )
        self._screens['how'] = HowItWorksScreen(
            self.root, self.theme, {
                'back_to_menu': lambda: self._show('start'),
            },
        )

    # ── navigation ───────────────────────────────────────

    def _show(self, name: str):
        if self._current:
            self._screens[self._current].pack_forget()
        self._screens[name].pack(fill='both', expand=True)
        self._current = name

    def _play(self, mark: str):
        self._show('game')
        self._screens['game'].start_game(mark)

    # ── theme ────────────────────────────────────────────

    def _toggle_theme(self):
        self.theme.toggle()

    def _apply_theme(self):
        ctk.set_appearance_mode("dark" if self.theme.is_dark() else "light")
        for scr in self._screens.values():
            scr.refresh_theme()

    # ── exit ─────────────────────────────────────────────

    def _exit(self):
        self.root.quit()

    # ── run ──────────────────────────────────────────────

    def run(self):
        self.root.mainloop()

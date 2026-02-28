"""
Theme definitions for the K-Map Tic-Tac-Toe application.

Two built-in palettes:
    • DARK  — Neon-on-black, cyberpunk / glassmorphism
    • LIGHT — Soft, pastel-accented, clean

Both use high-contrast accent colours for marks (X = cyan-ish,
O = pink-ish) to keep the board readable.
"""


DARK_THEME = {
    "name":                     "dark",

    # ── backgrounds ───────────────────────────────────────
    "bg":                       "#0D0D1A",
    "bg_secondary":             "#1A1A2E",
    "bg_tertiary":              "#16213E",
    "panel":                    "#1E1E3A",
    "panel_border":             "#2A2A5A",

    # ── accents ───────────────────────────────────────────
    "accent_cyan":              "#00F5FF",
    "accent_purple":            "#BF40BF",
    "accent_pink":              "#FF1493",
    "accent_gold":              "#FFD700",
    "accent_green":             "#00FF88",

    # ── text ──────────────────────────────────────────────
    "text_primary":             "#FFFFFF",
    "text_secondary":           "#A0A0C0",
    "text_dim":                 "#606080",

    # ── game board ────────────────────────────────────────
    "x_color":                  "#00F5FF",
    "o_color":                  "#FF1493",
    "grid_line":                "#2A2A5A",
    "cell_bg":                  "#12122A",
    "cell_hover":               "#1E1E40",
    "win_glow":                 "#FFD700",

    # ── buttons ───────────────────────────────────────────
    "button_bg":                "#BF40BF",
    "button_hover":             "#D050D0",
    "button_text":              "#FFFFFF",
    "button_secondary_bg":      "#2A2A5A",
    "button_secondary_hover":   "#3A3A6A",

    # ── misc ──────────────────────────────────────────────
    "scrollbar":                "#3A3A5A",
    "error":                    "#FF4444",
    "success":                  "#00FF88",
}


LIGHT_THEME = {
    "name":                     "light",

    "bg":                       "#F0F0F8",
    "bg_secondary":             "#FFFFFF",
    "bg_tertiary":              "#E8E8F4",
    "panel":                    "#FFFFFF",
    "panel_border":             "#D0D0E0",

    "accent_cyan":              "#0088CC",
    "accent_purple":            "#8B30CC",
    "accent_pink":              "#DD1177",
    "accent_gold":              "#CC9900",
    "accent_green":             "#00AA55",

    "text_primary":             "#1A1A2E",
    "text_secondary":           "#555577",
    "text_dim":                 "#888899",

    "x_color":                  "#0088CC",
    "o_color":                  "#DD1177",
    "grid_line":                "#C0C0D8",
    "cell_bg":                  "#F8F8FF",
    "cell_hover":               "#E0E0F8",
    "win_glow":                 "#CC9900",

    "button_bg":                "#8B30CC",
    "button_hover":             "#A040DD",
    "button_text":              "#FFFFFF",
    "button_secondary_bg":      "#D0D0E0",
    "button_secondary_hover":   "#C0C0D0",

    "scrollbar":                "#C0C0D0",
    "error":                    "#CC2222",
    "success":                  "#00AA55",
}


class ThemeManager:
    """Manages theme switching and provides colour look-ups."""

    def __init__(self):
        self.current_theme: dict = DARK_THEME
        self._listeners: list = []

    def get(self, key: str) -> str:
        """Look up a colour by key (returns #FFFFFF on miss)."""
        return self.current_theme.get(key, "#FFFFFF")

    def is_dark(self) -> bool:
        return self.current_theme["name"] == "dark"

    def toggle(self):
        """Switch between dark and light themes."""
        self.current_theme = LIGHT_THEME if self.is_dark() else DARK_THEME
        self._notify()

    def add_listener(self, callback):
        """Register a callable invoked on every theme change."""
        self._listeners.append(callback)

    def _notify(self):
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass

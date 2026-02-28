"""
Move-priority controller.

Orchestrates the K-Map AI decision pipeline and records
which Boolean module was activated for each move — useful
for the UI's AI-reasoning display.

Priority levels (derived from K-map analysis):
    1. Win            — Complete three-in-a-row
    2. Block          — Prevent opponent's three-in-a-row
    3. Fork           — Create simultaneous dual threat
    4. Block Fork     — Prevent opponent's dual threat
    5. Center         — Strategic center control
    6. Opp. Corner    — Counter opponent's corner
    7. Corner         — Positional corner advantage
    8. Side           — Remaining side cells
"""

from core.kmap_ai import KMapAI


class MovePriority:
    """
    Wrapper around KMapAI that tracks which priority module
    was used for each decision.
    """

    PRIORITY_NAMES = [
        "Win",
        "Block",
        "Fork",
        "Block Fork",
        "Center",
        "Opposite Corner",
        "Corner",
        "Side",
    ]

    def __init__(self, ai_mark: str = 'O'):
        self.ai = KMapAI(ai_mark)
        self.last_priority: str | None = None
        self.last_move: int | None = None

    # ── Ordered module list ───────────────────────────────

    def _modules(self):
        return [
            self.ai.win_module,
            self.ai.block_module,
            self.ai.fork_module,
            self.ai.block_fork_module,
            self.ai.center_module,
            self.ai.opposite_corner_module,
            self.ai.corner_module,
            self.ai.side_module,
        ]

    # ── Public API ────────────────────────────────────────

    def get_best_move(self, board) -> int | None:
        """
        Evaluate Boolean modules in priority order.
        Records the module name and chosen cell.
        """
        for idx, module in enumerate(self._modules()):
            move = module(board)
            if move is not None:
                self.last_priority = self.PRIORITY_NAMES[idx]
                self.last_move = move
                return move

        # Fallback
        empty = board.get_empty_cells()
        if empty:
            self.last_priority = "Fallback"
            self.last_move = empty[0]
            return empty[0]

        return None

    def get_last_reasoning(self) -> str:
        """Human-readable explanation of the last move."""
        if self.last_priority is not None and self.last_move is not None:
            row, col = divmod(self.last_move, 3)
            return f"{self.last_priority} → Cell ({row},{col})"
        return "No move made yet"

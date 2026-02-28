"""
Board representation using Boolean variables.

Each cell has two boolean variables:
    X[i] = True if cell i is occupied by X
    O[i] = True if cell i is occupied by O

A cell is empty when:  NOT X[i] AND NOT O[i]

Board indices:
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8

This encoding allows all game logic to be expressed as
Boolean SOP/POS expressions — directly derivable from
Karnaugh Map simplification.
"""


class Board:
    """Tic-Tac-Toe board with Boolean variable encoding."""

    def __init__(self):
        # Boolean arrays: X[i] is True iff cell i holds X
        self.X = [False] * 9
        self.O = [False] * 9

    def reset(self):
        """Clear the board — all variables go to False."""
        self.X = [False] * 9
        self.O = [False] * 9

    # ── Boolean cell queries ──────────────────────────────

    def is_empty(self, i: int) -> bool:
        """
        Boolean expression for empty cell:
            EMPTY[i] = NOT X[i]  AND  NOT O[i]
        """
        return (not self.X[i]) and (not self.O[i])

    def get_cell(self, i: int):
        """Return 'X', 'O', or None for cell i."""
        if self.X[i]:
            return 'X'
        if self.O[i]:
            return 'O'
        return None

    # ── Mutation ──────────────────────────────────────────

    def place(self, i: int, player: str) -> bool:
        """
        Place a mark.  player ∈ {'X', 'O'}.
        Returns True on success, False if cell is occupied.
        """
        if not self.is_empty(i):
            return False
        if player == 'X':
            self.X[i] = True
        else:
            self.O[i] = True
        return True

    # ── Board queries ─────────────────────────────────────

    def get_empty_cells(self):
        """Return list of indices where EMPTY[i] is True."""
        return [i for i in range(9) if self.is_empty(i)]

    def is_full(self) -> bool:
        """
        FULL = NOT EMPTY[0] AND NOT EMPTY[1] AND … AND NOT EMPTY[8]
        """
        return all(not self.is_empty(i) for i in range(9))

    def copy(self):
        """Return an independent copy of this board."""
        b = Board()
        b.X = self.X[:]
        b.O = self.O[:]
        return b

    # ── Display ───────────────────────────────────────────

    def __str__(self):
        symbols = []
        for i in range(9):
            if self.X[i]:
                symbols.append('X')
            elif self.O[i]:
                symbols.append('O')
            else:
                symbols.append('·')
        return (
            f" {symbols[0]} │ {symbols[1]} │ {symbols[2]}\n"
            f"───┼───┼───\n"
            f" {symbols[3]} │ {symbols[4]} │ {symbols[5]}\n"
            f"───┼───┼───\n"
            f" {symbols[6]} │ {symbols[7]} │ {symbols[8]}"
        )

    def __repr__(self):
        return f"Board(X={self.X}, O={self.O})"

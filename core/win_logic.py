"""
Win detection using Boolean logic — Sum-of-Products form.

Derived from Karnaugh Map analysis of the winning condition.

────────────────────────────────────────────────────────────
WINNING LINES  (8 product terms):
    Row 0:  (0, 1, 2)       Row 1:  (3, 4, 5)       Row 2:  (6, 7, 8)
    Col 0:  (0, 3, 6)       Col 1:  (1, 4, 7)       Col 2:  (2, 5, 8)
    Diag :  (0, 4, 8)       Anti :  (2, 4, 6)

For a player P the win condition in SOP form is:

    WIN_P = (P0·P1·P2) + (P3·P4·P5) + (P6·P7·P8)
          + (P0·P3·P6) + (P1·P4·P7) + (P2·P5·P8)
          + (P0·P4·P8) + (P2·P4·P6)

Each product term is a 3-variable AND.
The sum (OR) aggregates all eight lines.
This is a canonical SOP — the direct output of K-map
simplification applied to a 9-variable truth table of
winning states.
────────────────────────────────────────────────────────────
"""

# All winning lines as tuples of cell indices
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]

# Pre-computed mapping: cell → list of winning lines through that cell
# This lookup table accelerates the per-cell Boolean evaluation.
CELL_LINES: dict[int, list[tuple[int, int, int]]] = {i: [] for i in range(9)}
for _line in WIN_LINES:
    for _cell in _line:
        CELL_LINES[_cell].append(_line)


# ── SOP-based win checks ─────────────────────────────────

def check_win_x(board) -> tuple | None:
    """
    Boolean SOP evaluation for X winning:

        WIN_X =  (X0·X1·X2) + (X3·X4·X5) + (X6·X7·X8)
               + (X0·X3·X6) + (X1·X4·X7) + (X2·X5·X8)
               + (X0·X4·X8) + (X2·X4·X6)

    Returns the winning line tuple, or None.
    """
    X = board.X
    for a, b, c in WIN_LINES:
        # Product term:  Xa · Xb · Xc
        if X[a] and X[b] and X[c]:
            return (a, b, c)
    return None


def check_win_o(board) -> tuple | None:
    """
    Boolean SOP evaluation for O winning:

        WIN_O =  (O0·O1·O2) + (O3·O4·O5) + (O6·O7·O8)
               + (O0·O3·O6) + (O1·O4·O7) + (O2·O5·O8)
               + (O0·O4·O8) + (O2·O4·O6)

    Returns the winning line tuple, or None.
    """
    O = board.O
    for a, b, c in WIN_LINES:
        # Product term:  Oa · Ob · Oc
        if O[a] and O[b] and O[c]:
            return (a, b, c)
    return None


# ── Convenience helpers ───────────────────────────────────

def check_winner(board) -> str | None:
    """Return 'X', 'O', or None."""
    if check_win_x(board):
        return 'X'
    if check_win_o(board):
        return 'O'
    return None


def get_winning_line(board) -> tuple | None:
    """Return the winning line tuple, or None."""
    line = check_win_x(board)
    if line:
        return line
    return check_win_o(board)

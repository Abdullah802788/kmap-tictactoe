"""
K-Map–derived Boolean Logic AI for Tic-Tac-Toe.

Every decision module evaluates Boolean expressions in
Sum-of-Products (SOP) form — the canonical output of
Karnaugh Map simplification.

The AI uses a strict priority cascade of 8 Boolean modules.
Each module either returns a move index (0-8) or None,
deferring to the next lower-priority module.

═══════════════════════════════════════════════════════════
MODULE PRIORITY          SOP PATTERN
───────────────────────────────────────────────────────────
1. Win                   EMPTY[i] · Σ(AI[j]·AI[k])
2. Block                 EMPTY[i] · Σ(OPP[j]·OPP[k])
3. Fork (create)         EMPTY[i] · (THREATS[i] ≥ 2)
4. Fork (block)          Forcing / direct block logic
5. Center                ¬X[4] · ¬O[4]
6. Opposite corner       EMPTY[c] · OPP[opp(c)]
7. Any corner            EMPTY[0] + EMPTY[2] + …
8. Any side              EMPTY[1] + EMPTY[3] + …
═══════════════════════════════════════════════════════════
"""

from core.win_logic import WIN_LINES, CELL_LINES


class KMapAI:
    """
    Perfect Tic-Tac-Toe player powered by K-map Boolean logic.

    The AI evaluates pure combinational logic on the board's
    Boolean state variables — no game-tree search, no minimax,
    no randomness.
    """

    def __init__(self, ai_mark: str = 'O'):
        self.ai_mark = ai_mark
        self.human_mark = 'X' if ai_mark == 'O' else 'O'

    # ── helper accessors ──────────────────────────────────

    def _ai_cells(self, board) -> list[bool]:
        return board.X if self.ai_mark == 'X' else board.O

    def _human_cells(self, board) -> list[bool]:
        return board.X if self.human_mark == 'X' else board.O

    # ══════════════════════════════════════════════════════
    #  MODULE 1 — WIN
    # ══════════════════════════════════════════════════════
    def win_module(self, board) -> int | None:
        """
        K-Map SOP — winning move for the AI at cell i:

            MOVE_WIN[i]  =  EMPTY[i]  ·  Σ  ( AI[j] · AI[k] )
                                         (i,j,k) ∈ lines(i)

        Example, fully expanded for cell 0:

            MOVE_WIN[0] = (¬X0·¬O0) · ( (AI1·AI2)
                                       + (AI3·AI6)
                                       + (AI4·AI8) )

        Each inner product is a minterm; the OR is the sum —
        a textbook SOP produced by K-map grouping.
        """
        ai = self._ai_cells(board)
        for i in range(9):
            if not board.is_empty(i):
                continue
            # OR of product terms (one per line through i)
            for line in CELL_LINES[i]:
                j, k = [c for c in line if c != i]
                if ai[j] and ai[k]:          # product term: AI[j] · AI[k]
                    return i
        return None

    # ══════════════════════════════════════════════════════
    #  MODULE 2 — BLOCK
    # ══════════════════════════════════════════════════════
    def block_module(self, board) -> int | None:
        """
        K-Map SOP — block opponent's winning move at cell i:

            MOVE_BLOCK[i]  =  EMPTY[i]  ·  Σ  ( OPP[j] · OPP[k] )
                                             (i,j,k) ∈ lines(i)

        Structurally identical to the Win module but over
        the opponent's Boolean variables.
        """
        opp = self._human_cells(board)
        for i in range(9):
            if not board.is_empty(i):
                continue
            for line in CELL_LINES[i]:
                j, k = [c for c in line if c != i]
                if opp[j] and opp[k]:        # product term: OPP[j] · OPP[k]
                    return i
        return None

    # ── threat counter (shared by fork modules) ───────────

    def _count_threats_at(self, board, cell: int, mark: list[bool]) -> int:
        """
        Count prospective winning threats created by placing
        *mark* at *cell*.

        For each line (cell, j, k) the Boolean threat term is:

            THREAT_LINE = (MARK[j] · EMPTY[k]) + (EMPTY[j] · MARK[k])

        i.e. one ally and one empty in the line — after placing
        at *cell* this becomes a two-in-a-row with one open end.

        Total threats = Σ THREAT_LINE  over all lines through cell.
        A fork exists when this sum ≥ 2.
        """
        threats = 0
        for line in CELL_LINES[cell]:
            j, k = [c for c in line if c != cell]
            # SOP: (MARK[j]·EMPTY[k]) + (MARK[k]·EMPTY[j])
            if mark[j] and board.is_empty(k):
                threats += 1
            elif mark[k] and board.is_empty(j):
                threats += 1
        return threats

    # ══════════════════════════════════════════════════════
    #  MODULE 3 — FORK (create)
    # ══════════════════════════════════════════════════════
    def fork_module(self, board) -> int | None:
        """
        K-Map SOP for fork creation:

            FORK[i] = EMPTY[i]  ·  ( THREATS_AI[i] ≥ 2 )

        The threshold (≥ 2) over a sum of Boolean product terms
        is equivalent to selecting cells whose K-map–simplified
        expression evaluates to 1 on at least two independent
        threat minterms.
        """
        ai = self._ai_cells(board)
        best_cell = None
        best_threats = 1          # need ≥ 2 for a fork

        for i in range(9):
            if not board.is_empty(i):
                continue
            t = self._count_threats_at(board, i, ai)
            if t > best_threats:
                best_threats = t
                best_cell = i

        return best_cell

    # ══════════════════════════════════════════════════════
    #  MODULE 4 — FORK BLOCK
    # ══════════════════════════════════════════════════════
    def block_fork_module(self, board) -> int | None:
        """
        K-Map SOP for blocking opponent forks:

        Step 1 — identify all opponent fork cells:

            OPP_FORK[i] = EMPTY[i] · (THREATS_OPP[i] ≥ 2)

        Step 2 — resolve:
            • Single fork  → block directly.
            • Multiple forks → play a forcing move (create a
              two-in-a-row) whose forced block cell is NOT
              itself a fork cell.  This collapses the opponent
              into a defensive path that avoids the fork.
        """
        opp = self._human_cells(board)
        ai = self._ai_cells(board)

        # ── Step 1: enumerate opponent fork cells ──
        fork_cells = []
        for i in range(9):
            if not board.is_empty(i):
                continue
            if self._count_threats_at(board, i, opp) >= 2:
                fork_cells.append(i)

        if not fork_cells:
            return None

        # Single fork — block directly
        if len(fork_cells) == 1:
            return fork_cells[0]

        # ── Step 2: find a forcing move ──
        # A forcing move is a cell where placing the AI mark
        # creates a two-in-a-row, and the cell the opponent
        # must block is NOT one of their fork cells.
        fork_set = set(fork_cells)
        for i in range(9):
            if not board.is_empty(i):
                continue
            for line in CELL_LINES[i]:
                j, k = [c for c in line if c != i]
                # Does placing at i create a threat?
                if ai[j] and board.is_empty(k):
                    # Opponent would need to block at k
                    if k not in fork_set:
                        return i
                elif ai[k] and board.is_empty(j):
                    if j not in fork_set:
                        return i

        # Fallback: block a fork cell directly
        return fork_cells[0]

    # ══════════════════════════════════════════════════════
    #  MODULE 5 — CENTER
    # ══════════════════════════════════════════════════════
    def center_module(self, board) -> int | None:
        """
        Simplest K-Map SOP — single product term:

            CENTER = ¬X[4] · ¬O[4]       (i.e. EMPTY[4])
        """
        if board.is_empty(4):
            return 4
        return None

    # ══════════════════════════════════════════════════════
    #  MODULE 6 — OPPOSITE CORNER
    # ══════════════════════════════════════════════════════
    def opposite_corner_module(self, board) -> int | None:
        """
        K-Map SOP with four product terms:

            OPP_CORNER = (EMPTY[0] · OPP[8])
                       + (EMPTY[2] · OPP[6])
                       + (EMPTY[6] · OPP[2])
                       + (EMPTY[8] · OPP[0])

        Each term is a 2-literal minterm — minimal SOP that
        a K-map would produce for this 4-cell sub-problem.
        """
        opp = self._human_cells(board)
        pairs = [(0, 8), (2, 6), (6, 2), (8, 0)]
        for corner, opposite in pairs:
            # Product term: EMPTY[corner] · OPP[opposite]
            if board.is_empty(corner) and opp[opposite]:
                return corner
        return None

    # ══════════════════════════════════════════════════════
    #  MODULE 7 — ANY CORNER
    # ══════════════════════════════════════════════════════
    def corner_module(self, board) -> int | None:
        """
        K-Map SOP — pure sum of single-literal terms:

            CORNER = EMPTY[0] + EMPTY[2] + EMPTY[6] + EMPTY[8]
        """
        for c in (0, 2, 6, 8):
            if board.is_empty(c):
                return c
        return None

    # ══════════════════════════════════════════════════════
    #  MODULE 8 — ANY SIDE
    # ══════════════════════════════════════════════════════
    def side_module(self, board) -> int | None:
        """
        K-Map SOP — pure sum of single-literal terms:

            SIDE = EMPTY[1] + EMPTY[3] + EMPTY[5] + EMPTY[7]
        """
        for s in (1, 3, 5, 7):
            if board.is_empty(s):
                return s
        return None

    # ══════════════════════════════════════════════════════
    #  MAIN DECISION PIPELINE
    # ══════════════════════════════════════════════════════
    def get_move(self, board) -> int | None:
        """
        Evaluate all Boolean modules in strict priority order.
        Returns the optimal cell index (0-8), or None if the
        board is full.
        """
        for module in (
            self.win_module,
            self.block_module,
            self.fork_module,
            self.block_fork_module,
            self.center_module,
            self.opposite_corner_module,
            self.corner_module,
            self.side_module,
        ):
            move = module(board)
            if move is not None:
                return move

        # Absolute fallback (should never trigger in a valid game)
        empty = board.get_empty_cells()
        return empty[0] if empty else None

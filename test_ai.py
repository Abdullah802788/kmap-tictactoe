#!/usr/bin/env python3
"""
AI Validation Script
~~~~~~~~~~~~~~~~~~~~

Simulates 1000 games (500 as X, 500 as O) of the K-Map AI
against a uniformly-random opponent and verifies:

    • AI never loses.
    • Win + Draw counts are printed.

Usage:
    python test_ai.py
"""

import sys
import os
import random

# Ensure project root is importable
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from core.board import Board
from core.move_priority import MovePriority
from core.win_logic import check_winner


def simulate(ai_mark: str) -> str:
    """
    Play one game: AI (ai_mark) vs random.
    Returns 'ai_win', 'draw', or 'ai_loss'.
    """
    board = Board()
    ai = MovePriority(ai_mark=ai_mark)
    opp_mark = 'O' if ai_mark == 'X' else 'X'
    turn = 'X'                       # X always first

    while not board.is_full():
        if turn == ai_mark:
            move = ai.get_best_move(board)
        else:
            move = random.choice(board.get_empty_cells())

        board.place(move, turn)

        w = check_winner(board)
        if w:
            return 'ai_win' if w == ai_mark else 'ai_loss'

        turn = 'O' if turn == 'X' else 'X'

    return 'draw'


def main():
    N = 1000
    print()
    print("  " + "\u2550" * 48)
    print("   K-MAP AI VALIDATION TEST")
    print(f"   Simulating {N} games vs Random Player")
    print("  " + "\u2550" * 48)
    print()

    random.seed(42)

    wins = draws = losses = 0

    for i in range(N):
        mark = 'X' if i % 2 == 0 else 'O'
        result = simulate(mark)
        if result == 'ai_win':
            wins += 1
        elif result == 'draw':
            draws += 1
        else:
            losses += 1
            print(f"  \u26a0  LOSS in game {i+1} (AI as {mark})")

        if (i + 1) % 200 == 0:
            print(f"  ... {i+1}/{N} games")

    print()
    print("  " + "\u2500" * 48)
    print("   RESULTS")
    print("  " + "\u2500" * 48)
    print(f"   AI Wins :  {wins:>5}   ({wins / N * 100:.1f}%)")
    print(f"   Draws   :  {draws:>5}   ({draws / N * 100:.1f}%)")
    print(f"   Losses  :  {losses:>5}   ({losses / N * 100:.1f}%)")
    print("  " + "\u2500" * 48)

    if losses == 0:
        print("\n   \u2705  PASS — AI never lost!  K-Map logic is perfect.\n")
    else:
        print(f"\n   \u274c  FAIL — AI lost {losses} game(s).  Logic needs fixing!\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

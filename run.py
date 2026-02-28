#!/usr/bin/env python3
"""
K-Map Tic Tac Toe — Launcher
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run this file to start the application:

    python run.py

It will:
  1.  Verify Python version (3.8+)
  2.  Auto-install missing dependencies
  3.  Launch the game
"""

import sys
import subprocess
import os


def check_python():
    v = sys.version_info
    if v < (3, 8):
        print(f"  ERROR  Python 3.8+ required (you have {v.major}.{v.minor}.{v.micro})")
        sys.exit(1)
    print(f"  \u2713 Python {v.major}.{v.minor}.{v.micro}")


def install_deps():
    needed = []
    try:
        import customtkinter        # noqa: F401
    except ImportError:
        needed.append('customtkinter')

    if needed:
        print(f"  Installing: {', '.join(needed)} ...")
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install'] + needed + ['-q'],
        )
        print("  \u2713 Dependencies installed")
    else:
        print("  \u2713 All dependencies satisfied")


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print()
    print("  \u2550" * 44)
    print("   K-MAP TIC TAC TOE  \u2014  Starting ...")
    print("  \u2550" * 44)
    print()

    check_python()
    install_deps()

    # Ensure project root is on sys.path
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    print("  \u2713 Launching application ...\n")

    from ui.app import App
    App().run()


if __name__ == '__main__':
    main()

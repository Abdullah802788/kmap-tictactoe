"""
Animation utilities for the K-Map Tic-Tac-Toe application.

• ConfettiAnimation  — coloured particles falling on a Canvas
• PulseAnimation     — pulsing colour cycle on canvas items
• WinLineAnimation   — animated line drawn across winning cells
• draw_neon_x / draw_neon_o  — mark-drawing with glow layers
"""

import random
import math
from core.utils import blend_color


# ══════════════════════════════════════════════════════════
#  CONFETTI
# ══════════════════════════════════════════════════════════

class ConfettiAnimation:
    """Shower of coloured particles on a tkinter Canvas."""

    PALETTE = [
        '#FF1493', '#00F5FF', '#FFD700', '#FF4500',
        '#00FF88', '#FF69B4', '#BF40BF', '#00BFFF',
        '#7B68EE', '#FFA500',
    ]

    def __init__(self, canvas, num_particles: int = 60):
        self.canvas = canvas
        self.num_particles = num_particles
        self.particles: list[dict] = []
        self.running = False
        self._after_id = None

    def start(self):
        self.stop()
        self.running = True

        w = max(self.canvas.winfo_width(), 500)
        h = max(self.canvas.winfo_height(), 600)

        for _ in range(self.num_particles):
            x = random.randint(0, w)
            y = random.randint(-h, -10)
            size = random.randint(4, 10)
            color = random.choice(self.PALETTE)
            dx = random.uniform(-1.5, 1.5)
            dy = random.uniform(2.0, 5.0)

            rid = self.canvas.create_rectangle(
                x, y, x + size, y + int(size * 0.6),
                fill=color, outline='', tags='confetti',
            )
            self.particles.append(dict(
                id=rid, x=x, y=y, dx=dx, dy=dy, size=size,
            ))

        self._tick()

    def _tick(self):
        if not self.running:
            return
        w = max(self.canvas.winfo_width(), 500)
        h = max(self.canvas.winfo_height(), 600)

        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['dy'] += 0.04          # gravity

            if p['y'] > h + 20:
                p['y'] = random.randint(-60, -10)
                p['x'] = random.randint(0, w)
                p['dy'] = random.uniform(2.0, 5.0)

            s = p['size']
            self.canvas.coords(
                p['id'], p['x'], p['y'],
                p['x'] + s, p['y'] + int(s * 0.6),
            )

        self._after_id = self.canvas.after(30, self._tick)

    def stop(self):
        self.running = False
        if self._after_id:
            try:
                self.canvas.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self.canvas.delete('confetti')
        self.particles.clear()


# ══════════════════════════════════════════════════════════
#  PULSE  (colour oscillation)
# ══════════════════════════════════════════════════════════

class PulseAnimation:
    """Pulses a canvas item's fill between two colours."""

    def __init__(self, canvas, items, color1: str, color2: str,
                 speed: int = 50, steps: int = 20):
        self.canvas = canvas
        self.items = items if isinstance(items, list) else [items]
        self.color1 = color1
        self.color2 = color2
        self.speed = speed
        self.steps = steps
        self.step = 0
        self.direction = 1
        self.running = False
        self._after_id = None

    def start(self):
        self.running = True
        self._tick()

    def _tick(self):
        if not self.running:
            return
        alpha = self.step / self.steps
        color = blend_color(self.color1, self.color2, alpha)
        for item in self.items:
            try:
                self.canvas.itemconfig(item, fill=color)
            except Exception:
                pass
        self.step += self.direction
        if self.step >= self.steps:
            self.direction = -1
        elif self.step <= 0:
            self.direction = 1
        self._after_id = self.canvas.after(self.speed, self._tick)

    def stop(self):
        self.running = False
        if self._after_id:
            try:
                self.canvas.after_cancel(self._after_id)
            except Exception:
                pass


# ══════════════════════════════════════════════════════════
#  WIN-LINE ANIMATION
# ══════════════════════════════════════════════════════════

class WinLineAnimation:
    """Animated glowing line drawn between two points."""

    def __init__(self, canvas, start, end, color: str,
                 bg_color: str, on_complete=None):
        self.canvas = canvas
        self.sx, self.sy = start
        self.ex, self.ey = end
        self.color = color
        self.bg_color = bg_color
        self.on_complete = on_complete
        self.progress = 0.0
        self.items: list = []
        self.running = False
        self._after_id = None

    def start(self):
        self.running = True
        self.progress = 0.0
        self._tick()

    def _tick(self):
        if not self.running:
            return

        self.progress = min(1.0, self.progress + 0.06)

        # clear previous frame
        for item in self.items:
            try:
                self.canvas.delete(item)
            except Exception:
                pass
        self.items.clear()

        cx = self.sx + (self.ex - self.sx) * self.progress
        cy = self.sy + (self.ey - self.sy) * self.progress

        # glow layers (outer → inner)
        for i in range(5, 0, -1):
            alpha = 0.15 * (6 - i) / 5
            glow = blend_color(self.color, self.bg_color, alpha)
            self.items.append(self.canvas.create_line(
                self.sx, self.sy, cx, cy,
                fill=glow, width=4 + i * 6, capstyle='round',
                tags='winline',
            ))

        # core line
        self.items.append(self.canvas.create_line(
            self.sx, self.sy, cx, cy,
            fill=self.color, width=4, capstyle='round',
            tags='winline',
        ))

        if self.progress < 1.0:
            self._after_id = self.canvas.after(18, self._tick)
        elif self.on_complete:
            self.on_complete()

    def stop(self):
        self.running = False
        if self._after_id:
            try:
                self.canvas.after_cancel(self._after_id)
            except Exception:
                pass
        for item in self.items:
            try:
                self.canvas.delete(item)
            except Exception:
                pass
        self.canvas.delete('winline')
        self.items.clear()


# ══════════════════════════════════════════════════════════
#  NEON MARK DRAWING
# ══════════════════════════════════════════════════════════

def draw_neon_x(canvas, cx, cy, size, color, bg_color, tag='mark'):
    """Draw an X with multi-layer glow."""
    h = size
    c1 = (cx - h, cy - h, cx + h, cy + h)
    c2 = (cx + h, cy - h, cx - h, cy + h)
    items = []
    for i in range(4, 0, -1):
        alpha = 0.12 * (5 - i) / 4
        glow = blend_color(color, bg_color, alpha)
        w = 3 + i * 4
        items.append(canvas.create_line(*c1, fill=glow, width=w,
                                        capstyle='round', tags=tag))
        items.append(canvas.create_line(*c2, fill=glow, width=w,
                                        capstyle='round', tags=tag))
    items.append(canvas.create_line(*c1, fill=color, width=3,
                                    capstyle='round', tags=tag))
    items.append(canvas.create_line(*c2, fill=color, width=3,
                                    capstyle='round', tags=tag))
    return items


def draw_neon_o(canvas, cx, cy, size, color, bg_color, tag='mark'):
    """Draw an O with multi-layer glow."""
    h = size
    items = []
    for i in range(4, 0, -1):
        alpha = 0.12 * (5 - i) / 4
        glow = blend_color(color, bg_color, alpha)
        w = 3 + i * 4
        items.append(canvas.create_oval(
            cx - h, cy - h, cx + h, cy + h,
            outline=glow, width=w, tags=tag,
        ))
    items.append(canvas.create_oval(
        cx - h, cy - h, cx + h, cy + h,
        outline=color, width=3, tags=tag,
    ))
    return items

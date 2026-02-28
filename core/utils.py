"""
Utility functions for the K-Map Tic-Tac-Toe application.

• Sound generation (pure-Python WAV synthesis)
• Cross-platform sound playback
• Color blending helpers
• Path helpers
"""

import os
import sys
import math
import struct
import wave

# ── Sound playback backend ────────────────────────────────
# Uses built-in winsound on Windows; silent fallback elsewhere.

_SOUND_AVAILABLE = False
try:
    if sys.platform == 'win32':
        import winsound as _winsound
        _SOUND_AVAILABLE = True
except ImportError:
    pass

_sound_enabled = True          # global mute toggle


def set_sound_enabled(enabled: bool):
    global _sound_enabled
    _sound_enabled = enabled


def is_sound_enabled() -> bool:
    return _sound_enabled


# ── Path helpers ──────────────────────────────────────────

def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_assets_dir() -> str:
    return os.path.join(get_project_root(), 'assets')


def get_sounds_dir() -> str:
    return os.path.join(get_assets_dir(), 'sounds')


def ensure_dirs():
    """Create asset directories if they don't exist."""
    for sub in ('sounds', 'fonts', 'icons', 'images'):
        os.makedirs(os.path.join(get_assets_dir(), sub), exist_ok=True)


# ── WAV synthesis ─────────────────────────────────────────

def _write_wav(path: str, samples: list[int], sample_rate: int = 44100):
    """Write 16-bit mono WAV from a list of int16 samples."""
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for s in samples:
            wf.writeframes(struct.pack('<h', max(-32767, min(32767, s))))


def _synth_tone(freq_fn, duration: float, volume: float = 0.4,
                sample_rate: int = 44100) -> list[int]:
    """
    Synthesise a tone.
    freq_fn: either a fixed float or callable(t, duration) → float
    """
    n = int(sample_rate * duration)
    fade = max(1, int(sample_rate * min(0.015, duration * 0.1)))
    samples = []
    for i in range(n):
        t = i / sample_rate
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n - fade:
            env = (n - i) / fade
        f = freq_fn(t, duration) if callable(freq_fn) else freq_fn
        val = volume * env * math.sin(2 * math.pi * f * t)
        samples.append(int(val * 32767))
    return samples


def _synth_chord(freqs: list[float], duration: float,
                 volume: float = 0.35, sample_rate: int = 44100) -> list[int]:
    """Synthesise a chord (sum of sine waves)."""
    n = int(sample_rate * duration)
    fade = max(1, int(sample_rate * min(0.015, duration * 0.1)))
    nf = len(freqs)
    samples = []
    for i in range(n):
        t = i / sample_rate
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n - fade:
            env = (n - i) / fade
        val = sum(math.sin(2 * math.pi * f * t) for f in freqs) / nf
        samples.append(int(volume * env * val * 32767))
    return samples


def generate_sounds():
    """Generate all game sound-effect WAV files (idempotent)."""
    ensure_dirs()
    d = get_sounds_dir()

    # Click — short bright blip
    p = os.path.join(d, 'click.wav')
    if not os.path.exists(p):
        _write_wav(p, _synth_chord([800, 1200], 0.055, 0.3))

    # Place mark — subtle tap
    p = os.path.join(d, 'place.wav')
    if not os.path.exists(p):
        _write_wav(p, _synth_chord([600, 900], 0.04, 0.25))

    # Win — ascending sweep
    p = os.path.join(d, 'win.wav')
    if not os.path.exists(p):
        _write_wav(p, _synth_tone(lambda t, d: 400 + 600 * (t / d), 0.5, 0.35))

    # Lose — descending sweep
    p = os.path.join(d, 'lose.wav')
    if not os.path.exists(p):
        _write_wav(p, _synth_tone(lambda t, d: 600 - 300 * (t / d), 0.5, 0.35))

    # Draw — flat neutral tone
    p = os.path.join(d, 'draw.wav')
    if not os.path.exists(p):
        _write_wav(p, _synth_chord([300, 350], 0.4, 0.25))


# ── Playback ──────────────────────────────────────────────

def play_sound(name: str):
    """Play a sound by short name (e.g. 'click', 'win')."""
    if not _SOUND_AVAILABLE or not _sound_enabled:
        return
    try:
        path = os.path.join(get_sounds_dir(), f'{name}.wav')
        if os.path.exists(path):
            _winsound.PlaySound(
                path,
                _winsound.SND_FILENAME | _winsound.SND_ASYNC | _winsound.SND_NODEFAULT,
            )
    except Exception:
        pass


# ── Color helpers ─────────────────────────────────────────

def blend_color(c1: str, c2: str, alpha: float) -> str:
    """
    Linearly blend two hex colours.
    alpha = 1.0  → pure c1
    alpha = 0.0  → pure c2
    """
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 * alpha + r2 * (1 - alpha))
    g = int(g1 * alpha + g2 * (1 - alpha))
    b = int(b1 * alpha + b2 * (1 - alpha))
    return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"

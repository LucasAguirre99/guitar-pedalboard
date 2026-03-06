#!/usr/bin/env python3
"""
Guitar Pedalboard - Simulador de pedales de guitarra en tiempo real
Conecta tu guitarra via interfaz de audio USB y procesa el sonido en tiempo real.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import uuid
import math
import numpy as np
from typing import Dict, List, Optional, Any

# ─── Verificar dependencias ───────────────────────────────────────────────────
try:
    from pedalboard import (
        Pedalboard, Chorus, Reverb, Distortion, Compressor, Gain,
        Delay, Phaser, NoiseGate, PitchShift,
        HighpassFilter, LowpassFilter,
    )
    import sounddevice as sd
    DEPS_OK = True
    MISSING_MSG = ""
except ImportError as e:
    DEPS_OK = False
    MISSING_MSG = str(e)

# ─── Definicion de pedales disponibles ───────────────────────────────────────
#  "params" define cada control: su nombre en el plugin, label, rango y default.
PEDALS: Dict[str, Any] = {
    "Volumen": {
        "factory": lambda p: Gain(gain_db=p["gain_db"]),
        "color": "#1565C0",
        "params": {
            "gain_db": {"label": "Ganancia", "min": -20.0, "max": 20.0, "default": 0.0, "unit": " dB"},
        },
    },
    "Distorsion": {
        "factory": lambda p: Distortion(drive_db=p["drive_db"]),
        "color": "#B71C1C",
        "params": {
            "drive_db": {"label": "Drive", "min": 0.0, "max": 60.0, "default": 25.0, "unit": " dB"},
        },
    },
    "Overdrive": {
        "factory": lambda p: Distortion(drive_db=p["drive_db"]),
        "color": "#E65100",
        "params": {
            "drive_db": {"label": "Drive", "min": 0.0, "max": 25.0, "default": 8.0, "unit": " dB"},
        },
    },
    "Reverb": {
        "factory": lambda p: Reverb(
            room_size=p["room_size"],
            damping=p["damping"],
            wet_level=p["wet_level"],
            dry_level=p["dry_level"],
        ),
        "color": "#4A148C",
        "params": {
            "room_size":  {"label": "Tamano sala", "min": 0.0, "max": 1.0, "default": 0.5,  "unit": ""},
            "damping":    {"label": "Amortiguacion", "min": 0.0, "max": 1.0, "default": 0.5,  "unit": ""},
            "wet_level":  {"label": "Efecto",   "min": 0.0, "max": 1.0, "default": 0.33, "unit": ""},
            "dry_level":  {"label": "Seco",     "min": 0.0, "max": 1.0, "default": 0.4,  "unit": ""},
        },
    },
    "Delay": {
        "factory": lambda p: Delay(
            delay_seconds=p["delay_seconds"],
            feedback=p["feedback"],
            mix=p["mix"],
        ),
        "color": "#37474F",
        "params": {
            "delay_seconds": {"label": "Tiempo",      "min": 0.05, "max": 1.0,  "default": 0.3,  "unit": " s"},
            "feedback":      {"label": "Retroalim.",  "min": 0.0,  "max": 0.95, "default": 0.3,  "unit": ""},
            "mix":           {"label": "Mezcla",      "min": 0.0,  "max": 1.0,  "default": 0.5,  "unit": ""},
        },
    },
    "Chorus": {
        "factory": lambda p: Chorus(
            rate_hz=p["rate_hz"],
            depth=p["depth"],
            mix=p["mix"],
        ),
        "color": "#006064",
        "params": {
            "rate_hz": {"label": "Velocidad",    "min": 0.1, "max": 10.0, "default": 1.0,  "unit": " Hz"},
            "depth":   {"label": "Profundidad",  "min": 0.0, "max": 1.0,  "default": 0.25, "unit": ""},
            "mix":     {"label": "Mezcla",       "min": 0.0, "max": 1.0,  "default": 0.5,  "unit": ""},
        },
    },
    "Phaser": {
        "factory": lambda p: Phaser(
            rate_hz=p["rate_hz"],
            depth=p["depth"],
            mix=p["mix"],
        ),
        "color": "#1B5E20",
        "params": {
            "rate_hz": {"label": "Velocidad",   "min": 0.1, "max": 10.0, "default": 1.0, "unit": " Hz"},
            "depth":   {"label": "Profundidad", "min": 0.0, "max": 1.0,  "default": 0.5, "unit": ""},
            "mix":     {"label": "Mezcla",      "min": 0.0, "max": 1.0,  "default": 0.5, "unit": ""},
        },
    },
    "Compresor": {
        "factory": lambda p: Compressor(
            threshold_db=p["threshold_db"],
            ratio=p["ratio"],
            attack_ms=p["attack_ms"],
            release_ms=p["release_ms"],
        ),
        "color": "#4E342E",
        "params": {
            "threshold_db": {"label": "Umbral",   "min": -60.0, "max": 0.0,    "default": -10.0, "unit": " dB"},
            "ratio":        {"label": "Ratio",    "min": 1.0,   "max": 20.0,   "default": 4.0,   "unit": ":1"},
            "attack_ms":    {"label": "Ataque",   "min": 1.0,   "max": 200.0,  "default": 10.0,  "unit": " ms"},
            "release_ms":   {"label": "Release",  "min": 10.0,  "max": 1000.0, "default": 100.0, "unit": " ms"},
        },
    },
    "Puerta de Ruido": {
        "factory": lambda p: NoiseGate(
            threshold_db=p["threshold_db"],
            ratio=p["ratio"],
            attack_ms=p["attack_ms"],
            release_ms=p["release_ms"],
        ),
        "color": "#263238",
        "params": {
            "threshold_db": {"label": "Umbral",  "min": -100.0, "max": 0.0,    "default": -50.0, "unit": " dB"},
            "ratio":        {"label": "Ratio",   "min": 1.0,    "max": 100.0,  "default": 10.0,  "unit": ":1"},
            "attack_ms":    {"label": "Ataque",  "min": 1.0,    "max": 100.0,  "default": 5.0,   "unit": " ms"},
            "release_ms":   {"label": "Release", "min": 10.0,   "max": 1000.0, "default": 100.0, "unit": " ms"},
        },
    },
    "Filtro Agudos": {
        "factory": lambda p: HighpassFilter(cutoff_frequency_hz=p["cutoff_frequency_hz"]),
        "color": "#BF360C",
        "params": {
            "cutoff_frequency_hz": {"label": "Frecuencia", "min": 20.0, "max": 8000.0, "default": 200.0, "unit": " Hz"},
        },
    },
    "Filtro Graves": {
        "factory": lambda p: LowpassFilter(cutoff_frequency_hz=p["cutoff_frequency_hz"]),
        "color": "#004D40",
        "params": {
            "cutoff_frequency_hz": {"label": "Frecuencia", "min": 200.0, "max": 20000.0, "default": 5000.0, "unit": " Hz"},
        },
    },
    "Pitch Shift": {
        "factory": lambda p: PitchShift(semitones=p["semitones"]),
        "color": "#880E4F",
        "params": {
            "semitones": {"label": "Semitonos", "min": -12.0, "max": 12.0, "default": 0.0, "unit": " st"},
        },
    },
}


# ─── Pedal activo en la cadena ────────────────────────────────────────────────

class ActivePedal:
    """Una instancia de pedal dentro de la cadena de efectos."""

    def __init__(self, pedal_type: str):
        self.id = str(uuid.uuid4())
        self.pedal_type = pedal_type
        self.enabled = True
        defn = PEDALS[pedal_type]
        self.params: Dict[str, float] = {
            k: v["default"] for k, v in defn["params"].items()
        }
        self._plugin = defn["factory"](self.params)

    @property
    def color(self) -> str:
        return PEDALS[self.pedal_type]["color"]

    def set_param(self, key: str, value: float):
        self.params[key] = value
        # Actualizar propiedad en el plugin directamente (sin recrearlo)
        # Esto preserva el estado interno del efecto (p.ej. cola del reverb)
        try:
            setattr(self._plugin, key, value)
        except AttributeError:
            # Si no tiene esa propiedad directa, recrear el plugin
            self._plugin = PEDALS[self.pedal_type]["factory"](self.params)

    def get_plugin(self):
        return self._plugin

    def reset_params(self):
        defn = PEDALS[self.pedal_type]
        for k, v in defn["params"].items():
            self.params[k] = v["default"]
        self._plugin = defn["factory"](self.params)


# ─── Afinador — deteccion de pitch ───────────────────────────────────────────

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_TUNER_BUF_SIZE = 8192   # ~186 ms a 44100 Hz — suficiente para detectar E2 (82 Hz)
_TUNER_MIN_FREQ = 60.0   # Hz  (por debajo del Mi grave con afinacion baja)
_TUNER_MAX_FREQ = 1400.0 # Hz  (cubrir hasta el Mi agudo en el traste 24)


def _detect_pitch(audio: np.ndarray, sample_rate: int):
    """
    Deteccion de pitch por autocorrelacion via FFT.
    Devuelve (freq_hz, nota, octava, cents) o None si la senal es muy debil.
    """
    audio = audio - audio.mean()
    if np.sqrt(np.mean(audio ** 2)) < 0.008:
        return None

    n = len(audio)
    # Autocorrelacion rapida via FFT
    fft = np.fft.rfft(audio, n=2 * n)
    acf = np.fft.irfft(fft * np.conj(fft))[:n]
    if acf[0] == 0:
        return None
    acf /= acf[0]

    min_lag = max(1, int(sample_rate / _TUNER_MAX_FREQ))
    max_lag = min(n - 1, int(sample_rate / _TUNER_MIN_FREQ))
    if min_lag >= max_lag:
        return None

    search = acf[min_lag:max_lag]
    peak_rel = int(np.argmax(search))
    lag = peak_rel + min_lag

    if acf[lag] < 0.35:   # correlacion insuficiente = nota no confiable
        return None

    # Interpolacion parabolica para precision sub-muestra
    if 0 < peak_rel < len(search) - 1:
        y1, y2, y3 = search[peak_rel - 1], search[peak_rel], search[peak_rel + 1]
        denom = 2 * y2 - y1 - y3
        if denom != 0:
            lag = lag + (y3 - y1) / (2 * denom)

    freq = sample_rate / lag
    semitones = 12 * np.log2(freq / 440.0)
    nearest = round(semitones)
    cents = (semitones - nearest) * 100
    midi = int(nearest) + 69
    note = NOTE_NAMES[midi % 12]
    octave = midi // 12 - 1
    return freq, note, octave, float(cents)


# ─── Motor de audio ───────────────────────────────────────────────────────────

class AudioEngine:
    """
    Loop de audio en tiempo real usando sounddevice + pedalboard.
    sounddevice usa el PortAudio del sistema (mas estable en Linux con ALSA/PulseAudio).
    El procesamiento de efectos lo hace pedalboard buffer a buffer.
    """

    def __init__(self):
        self._stream: Optional[sd.Stream] = None
        self._pedalboard = Pedalboard([])
        self._lock = threading.Lock()
        self._ready_event = threading.Event()
        self.running = False
        self.error: Optional[str] = None
        self._sample_rate = 44100
        # Afinador
        self._tuner_buf = np.zeros(_TUNER_BUF_SIZE, dtype="float32")
        self._tuner_pos = 0
        self._tuner_result = None   # (freq, nota, octava, cents) o None
        self._tuner_lock = threading.Lock()

    def get_tuner(self):
        with self._tuner_lock:
            return self._tuner_result

    @staticmethod
    def input_devices() -> List[str]:
        devices = sd.query_devices()
        return [d["name"] for d in devices if d["max_input_channels"] > 0]

    @staticmethod
    def output_devices() -> List[str]:
        devices = sd.query_devices()
        return [d["name"] for d in devices if d["max_output_channels"] > 0]

    def _callback(self, indata: np.ndarray, outdata: np.ndarray,
                  frames: int, time_info, status):
        """Callback de sounddevice: procesa cada buffer en tiempo real."""
        with self._lock:
            pb = self._pedalboard
        # indata: (frames, 2) float32 — mezclar a mono y procesar
        mono = indata.mean(axis=1, keepdims=True).T  # (1, frames)

        # Alimentar buffer del afinador con audio crudo (antes de efectos)
        raw = mono[0]
        n = len(raw)
        space = _TUNER_BUF_SIZE - self._tuner_pos
        if n >= space:
            self._tuner_buf[self._tuner_pos:] = raw[:space]
            result = _detect_pitch(self._tuner_buf.copy(), self._sample_rate)
            with self._tuner_lock:
                self._tuner_result = result
            self._tuner_pos = 0
        else:
            self._tuner_buf[self._tuner_pos:self._tuner_pos + n] = raw
            self._tuner_pos += n

        processed = pb(mono, self._sample_rate, reset=False)
        if processed.shape[0] == 1:
            processed = np.repeat(processed, 2, axis=0)
        outdata[:] = processed.T[:frames]

    def start(self, input_name: str, output_name: str,
              sample_rate: int = 48000, buffer_size: int = 256):
        self.stop()
        self.error = None
        self._sample_rate = sample_rate
        try:
            devices = sd.query_devices()
            in_idx = next(
                (i for i, d in enumerate(devices)
                 if d["name"] == input_name and d["max_input_channels"] > 0),
                None,
            )
            out_idx = next(
                (i for i, d in enumerate(devices)
                 if d["name"] == output_name and d["max_output_channels"] > 0),
                None,
            )
            if in_idx is None:
                raise RuntimeError(f"Dispositivo de entrada no encontrado: {input_name}")
            if out_idx is None:
                raise RuntimeError(f"Dispositivo de salida no encontrado: {output_name}")

            self._stream = sd.Stream(
                device=(in_idx, out_idx),
                samplerate=sample_rate,
                blocksize=buffer_size,
                dtype="float32",
                channels=2,  # estereo en ambos lados (requerido por hw: ALSA)
                callback=self._callback,
                latency="low",
            )
            self._stream.start()
            self.running = True
        except Exception as exc:
            self.error = str(exc)
            self.running = False
            raise

    def stop(self):
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        self.running = False

    def update_chain(self, chain: List["ActivePedal"]):
        """Actualiza la cadena de efectos activa (thread-safe)."""
        plugins = [p.get_plugin() for p in chain if p.enabled]
        with self._lock:
            self._pedalboard = Pedalboard(plugins)


# ─── Estilos visuales de pedales (inspirados en modelos famosos) ─────────────

PEDAL_STYLES: Dict[str, Any] = {
    "Volumen":         {"brand": "BOSS",   "model": "FV-500H",   "body": "#b8b8b8", "accent": "#808080", "knob_color": "#222222", "knobs": ["VOL"]},
    "Distorsion":      {"brand": "BOSS",   "model": "DS-1",      "body": "#e8921a", "accent": "#c07010", "knob_color": "#1a1a1a", "knobs": ["LVL", "TONE", "DIST"]},
    "Overdrive":       {"brand": "IBANEZ", "model": "TS9",       "body": "#2e7d32", "accent": "#1b5e20", "knob_color": "#1a1a1a", "knobs": ["DRIVE", "TONE", "LVL"]},
    "Reverb":          {"brand": "BOSS",   "model": "RV-6",      "body": "#0277bd", "accent": "#01579b", "knob_color": "#1a1a1a", "knobs": ["LVL", "TIME", "TONE"]},
    "Delay":           {"brand": "BOSS",   "model": "DD-3",      "body": "#f9a825", "accent": "#e65100", "knob_color": "#1a1a1a", "knobs": ["LVL", "F.B.", "TIME"]},
    "Chorus":          {"brand": "BOSS",   "model": "CE-5",      "body": "#1565c0", "accent": "#0d47a1", "knob_color": "#dddddd", "knobs": ["LVL", "RATE", "DEPTH"]},
    "Phaser":          {"brand": "MXR",    "model": "Phase 90",  "body": "#e65100", "accent": "#bf360c", "knob_color": "#111111", "knobs": ["SPEED"]},
    "Compresor":       {"brand": "MXR",    "model": "Dyna Comp", "body": "#c62828", "accent": "#8e0000", "knob_color": "#111111", "knobs": ["OUTPUT", "SENS"]},
    "Puerta de Ruido": {"brand": "BOSS",   "model": "NS-2",      "body": "#1a237e", "accent": "#0d1466", "knob_color": "#cccccc", "knobs": ["THRES.", "DECAY"]},
    "Filtro Agudos":   {"brand": "EHX",    "model": "Knockout",  "body": "#880e4f", "accent": "#560027", "knob_color": "#111111", "knobs": ["FREQ"]},
    "Filtro Graves":   {"brand": "EHX",    "model": "Bass Boost","body": "#1b5e20", "accent": "#003300", "knob_color": "#111111", "knobs": ["FREQ"]},
    "Pitch Shift":     {"brand": "BOSS",   "model": "PS-6",      "body": "#6a1b9a", "accent": "#4a0072", "knob_color": "#111111", "knobs": ["PITCH", "MODE"]},
}


def _lighten(hex_color: str, amount: int = 40) -> str:
    h = hex_color.lstrip("#")
    return "#{:02x}{:02x}{:02x}".format(
        min(255, int(h[0:2], 16) + amount),
        min(255, int(h[2:4], 16) + amount),
        min(255, int(h[4:6], 16) + amount),
    )


def _darken(hex_color: str, amount: int = 40) -> str:
    h = hex_color.lstrip("#")
    return "#{:02x}{:02x}{:02x}".format(
        max(0, int(h[0:2], 16) - amount),
        max(0, int(h[2:4], 16) - amount),
        max(0, int(h[4:6], 16) - amount),
    )


# ─── Presets ──────────────────────────────────────────────────────────────────
# Cada preset es una lista de dicts con "type" y "params".
# Los valores de params deben coincidir exactamente con las keys del PEDALS registry.

PRESETS: Dict[str, List[Dict]] = {
    "Marty Friedman - Lead": [
        {   # Gate apretado para silenciar ruido entre frases
            "type": "Puerta de Ruido",
            "params": {"threshold_db": -52.0, "ratio": 15.0, "attack_ms": 4.0, "release_ms": 180.0},
        },
        {   # Distorsion alta y apretada, estilo Marshall JCM800 con gain alto
            "type": "Distorsion",
            "params": {"drive_db": 50.0},
        },
        {   # Cortar el barro del bajo — su tono es brillante y articulado
            "type": "Filtro Agudos",
            "params": {"cutoff_frequency_hz": 110.0},
        },
        {   # Reverb minimo, solo para dar "sala" sin ensuciar
            "type": "Reverb",
            "params": {"room_size": 0.2, "damping": 0.75, "wet_level": 0.12, "dry_level": 0.88},
        },
    ],
    "Sonido Limpio": [
        {
            "type": "Compresor",
            "params": {"threshold_db": -18.0, "ratio": 3.0, "attack_ms": 15.0, "release_ms": 120.0},
        },
        {
            "type": "Chorus",
            "params": {"rate_hz": 0.8, "depth": 0.15, "mix": 0.3},
        },
        {
            "type": "Reverb",
            "params": {"room_size": 0.4, "damping": 0.5, "wet_level": 0.25, "dry_level": 0.75},
        },
    ],
    "Blues Clasico": [
        {
            "type": "Compresor",
            "params": {"threshold_db": -14.0, "ratio": 4.0, "attack_ms": 8.0, "release_ms": 150.0},
        },
        {
            "type": "Overdrive",
            "params": {"drive_db": 12.0},
        },
        {
            "type": "Reverb",
            "params": {"room_size": 0.5, "damping": 0.4, "wet_level": 0.3, "dry_level": 0.7},
        },
    ],
    "Doom / Stoner": [
        {
            "type": "Puerta de Ruido",
            "params": {"threshold_db": -45.0, "ratio": 8.0, "attack_ms": 10.0, "release_ms": 300.0},
        },
        {
            "type": "Distorsion",
            "params": {"drive_db": 58.0},
        },
        {   # Filtro grave para el tono oscuro y pesado
            "type": "Filtro Graves",
            "params": {"cutoff_frequency_hz": 3500.0},
        },
        {
            "type": "Reverb",
            "params": {"room_size": 0.8, "damping": 0.3, "wet_level": 0.4, "dry_level": 0.6},
        },
    ],
    "Surf Rock": [
        {
            "type": "Chorus",
            "params": {"rate_hz": 2.0, "depth": 0.35, "mix": 0.5},
        },
        {
            "type": "Reverb",
            "params": {"room_size": 0.75, "damping": 0.2, "wet_level": 0.55, "dry_level": 0.45},
        },
        {
            "type": "Delay",
            "params": {"delay_seconds": 0.18, "feedback": 0.25, "mix": 0.3},
        },
    ],
    "Shred / Metal Moderno": [
        {
            "type": "Puerta de Ruido",
            "params": {"threshold_db": -50.0, "ratio": 20.0, "attack_ms": 3.0, "release_ms": 120.0},
        },
        {
            "type": "Compresor",
            "params": {"threshold_db": -20.0, "ratio": 6.0, "attack_ms": 5.0, "release_ms": 80.0},
        },
        {
            "type": "Distorsion",
            "params": {"drive_db": 55.0},
        },
        {
            "type": "Filtro Agudos",
            "params": {"cutoff_frequency_hz": 90.0},
        },
        {
            "type": "Delay",
            "params": {"delay_seconds": 0.35, "feedback": 0.2, "mix": 0.2},
        },
    ],
}


# ─── Interfaz grafica ─────────────────────────────────────────────────────────

BG         = "#1a1a2e"
BG_DARK    = "#12122a"
BG_PANEL   = "#0d1b2a"
FG         = "#e0e0e0"
FG_DIM     = "#888888"
ACCENT     = "#00b4d8"
FONT       = ("Helvetica", 10)
FONT_BOLD  = ("Helvetica", 10, "bold")
FONT_SMALL = ("Helvetica", 8)
FONT_TITLE = ("Helvetica", 13, "bold")


class GuitarPedalboardApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Guitar Pedalboard")
        self.configure(bg=BG)
        self.minsize(960, 580)
        self.resizable(True, True)

        self.engine = AudioEngine()
        self.chain: List[ActivePedal] = []
        self.selected: Optional[ActivePedal] = None

        self._style_ttk()
        self._build_ui()

        if DEPS_OK:
            self._refresh_devices()
        else:
            self._show_missing_deps()

        self._rebuild_chain_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Estilo ────────────────────────────────────────────────────────────────

    def _style_ttk(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=BG_DARK, background=BG_DARK,
                        foreground=FG, selectbackground=BG_DARK, selectforeground=FG)
        style.configure("Horizontal.TScrollbar", background=BG_DARK,
                        troughcolor=BG, arrowcolor=FG_DIM)
        style.configure("TScale", background=BG_PANEL, troughcolor="#2a2a4a",
                        sliderlength=16)

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Barra superior
        self._build_topbar()

        # Contenedor principal con tres columnas
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True)

        self._build_left_panel(main)
        self._build_chain_panel(main)
        self._build_editor_panel(main)

    def _build_topbar(self):
        bar = tk.Frame(self, bg=BG_DARK, pady=8, padx=14)
        bar.pack(fill="x")

        tk.Label(bar, text="Guitar Pedalboard", bg=BG_DARK, fg=ACCENT,
                 font=FONT_TITLE).pack(side="left", padx=(0, 20))

        # Entrada
        tk.Label(bar, text="Entrada:", bg=BG_DARK, fg=FG_DIM, font=FONT).pack(side="left")
        self.input_var = tk.StringVar()
        self.input_combo = ttk.Combobox(bar, textvariable=self.input_var,
                                        width=26, state="readonly")
        self.input_combo.pack(side="left", padx=(4, 14))

        # Salida
        tk.Label(bar, text="Salida:", bg=BG_DARK, fg=FG_DIM, font=FONT).pack(side="left")
        self.output_var = tk.StringVar()
        self.output_combo = ttk.Combobox(bar, textvariable=self.output_var,
                                         width=26, state="readonly")
        self.output_combo.pack(side="left", padx=(4, 14))

        # Sample rate
        tk.Label(bar, text="Hz:", bg=BG_DARK, fg=FG_DIM, font=FONT).pack(side="left")
        self.samplerate_var = tk.StringVar(value="44100")
        ttk.Combobox(bar, textvariable=self.samplerate_var, width=7, state="readonly",
                     values=["44100", "48000", "96000"]).pack(side="left", padx=(4, 10))

        # Buffer
        tk.Label(bar, text="Buffer:", bg=BG_DARK, fg=FG_DIM, font=FONT).pack(side="left")
        self.buffer_var = tk.StringVar(value="256")
        ttk.Combobox(bar, textvariable=self.buffer_var, width=6, state="readonly",
                     values=["64", "128", "256", "512", "1024"]).pack(side="left", padx=(4, 14))

        # Boton iniciar/detener
        self.start_btn = tk.Button(bar, text="  Iniciar  ", bg="#2e7d32", fg="white",
                                   font=FONT_BOLD, relief="flat", padx=10, pady=2,
                                   activebackground="#1b5e20", activeforeground="white",
                                   cursor="hand2", command=self._toggle_audio)
        self.start_btn.pack(side="left", padx=6)

        # Estado
        self.status_lbl = tk.Label(bar, text="Detenido", bg=BG_DARK, fg=FG_DIM, font=FONT)
        self.status_lbl.pack(side="left", padx=8)

        # Refrescar
        tk.Button(bar, text="Refrescar", bg=BG_PANEL, fg=FG_DIM, font=FONT_SMALL,
                  relief="flat", padx=6, cursor="hand2",
                  command=self._refresh_devices).pack(side="right")

    def _build_left_panel(self, parent):
        panel = tk.Frame(parent, bg=BG_PANEL, width=175)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        tk.Label(panel, text="PEDALES DISPONIBLES", bg=BG_PANEL, fg=FG_DIM,
                 font=("Helvetica", 8, "bold")).pack(pady=(12, 6))

        sep = tk.Frame(panel, bg="#2a2a4a", height=1)
        sep.pack(fill="x", padx=10, pady=(0, 8))

        for name in sorted(PEDALS.keys()):
            color = PEDALS[name]["color"]
            btn = tk.Button(
                panel, text=name, bg=color, fg="white",
                font=FONT_SMALL, relief="flat", pady=6, anchor="w", padx=10,
                cursor="hand2", activebackground=color, activeforeground="white",
                command=lambda n=name: self._add_pedal(n),
            )
            btn.pack(fill="x", padx=8, pady=2)

        # ── Seccion de presets ─────────────────────────────
        tk.Frame(panel, bg="#2a2a4a", height=1).pack(fill="x", padx=10, pady=(12, 8))
        tk.Label(panel, text="PRESETS", bg=BG_PANEL, fg=FG_DIM,
                 font=("Helvetica", 8, "bold")).pack()

        self.preset_var = tk.StringVar()
        preset_combo = ttk.Combobox(panel, textvariable=self.preset_var,
                                    values=list(PRESETS.keys()),
                                    state="readonly", width=20)
        preset_combo.pack(padx=8, pady=(6, 4), fill="x")
        preset_combo.current(0)

        tk.Button(panel, text="Cargar preset", bg=ACCENT, fg="#000000",
                  font=FONT_SMALL, relief="flat", pady=5, cursor="hand2",
                  activebackground=_lighten(ACCENT, 30),
                  command=self._load_preset).pack(fill="x", padx=8, pady=(0, 8))

    def _load_preset(self):
        name = self.preset_var.get()
        if name not in PRESETS:
            return
        # Reemplazar la cadena actual con los pedales del preset
        self.chain.clear()
        self.selected = None
        for step in PRESETS[name]:
            pedal = ActivePedal(step["type"])
            for key, val in step["params"].items():
                pedal.set_param(key, val)
            self.chain.append(pedal)
        self._rebuild_chain_ui()
        self._show_editor_placeholder()
        self._push_chain()

    def _build_chain_panel(self, parent):
        self.chain_outer = tk.Frame(parent, bg=BG)
        self.chain_outer.pack(side="left", fill="both", expand=True)

        tk.Label(self.chain_outer,
                 text="CADENA DE EFECTOS   |   Clic = editar     ON/OFF = activar     < > = mover     X = eliminar",
                 bg=BG, fg=FG_DIM, font=("Helvetica", 8)).pack(pady=(8, 2))

        # Canvas scrollable horizontal para la cadena
        self.chain_canvas = tk.Canvas(self.chain_outer, bg=BG,
                                      highlightthickness=0, height=220)
        self.chain_canvas.pack(fill="x", padx=10, pady=4)

        hbar = ttk.Scrollbar(self.chain_outer, orient="horizontal",
                              command=self.chain_canvas.xview)
        hbar.pack(fill="x", padx=10)
        self.chain_canvas.configure(xscrollcommand=hbar.set)

        self.chain_inner = tk.Frame(self.chain_canvas, bg=BG)
        self._chain_window = self.chain_canvas.create_window(
            (0, 0), window=self.chain_inner, anchor="nw"
        )
        self.chain_inner.bind("<Configure>", self._on_chain_resize)

        # Label de cadena vacia
        self.empty_lbl = tk.Label(
            self.chain_outer,
            text="Agrega pedales desde el panel izquierdo\npara construir tu cadena de efectos",
            bg=BG, fg="#333355", font=("Helvetica", 12),
        )
        self.empty_lbl.pack(expand=True, pady=30)

        # Indicador de senial
        sig = tk.Frame(self.chain_outer, bg=BG)
        sig.pack(fill="x", padx=14, pady=(4, 0))
        tk.Label(sig, text="GUITARRA -->", bg=BG, fg="#445566", font=FONT_SMALL).pack(side="left")
        tk.Label(sig, text="--> AURICULARES / SALIDA", bg=BG, fg="#445566",
                 font=FONT_SMALL).pack(side="right")

    def _build_editor_panel(self, parent):
        self.editor_frame = tk.Frame(parent, bg=BG_PANEL, width=235)
        self.editor_frame.pack(side="right", fill="y")
        self.editor_frame.pack_propagate(False)

        tk.Label(self.editor_frame, text="EDITOR DE PARAMETROS", bg=BG_PANEL,
                 fg=FG_DIM, font=("Helvetica", 8, "bold")).pack(pady=(12, 6))
        tk.Frame(self.editor_frame, bg="#2a2a4a", height=1).pack(fill="x", padx=10, pady=(0, 8))

        self.editor_scroll_frame = tk.Frame(self.editor_frame, bg=BG_PANEL)
        self.editor_scroll_frame.pack(fill="both", expand=True, padx=12)

        self._show_editor_placeholder()
        self._build_tuner_panel()

    # ── Helpers de layout ─────────────────────────────────────────────────────

    def _on_chain_resize(self, _event=None):
        self.chain_canvas.configure(scrollregion=self.chain_canvas.bbox("all"))

    def _show_editor_placeholder(self):
        for w in self.editor_scroll_frame.winfo_children():
            w.destroy()
        tk.Label(
            self.editor_scroll_frame,
            text="Selecciona un pedal\npara editar sus parametros",
            bg=BG_PANEL, fg="#444466", font=("Helvetica", 10), justify="center",
        ).pack(expand=True, pady=40)

    # ── Dispositivos ──────────────────────────────────────────────────────────

    def _refresh_devices(self):
        if not DEPS_OK:
            return
        try:
            ins = AudioEngine.input_devices()
            outs = AudioEngine.output_devices()
            self.input_combo["values"] = ins
            self.output_combo["values"] = outs
            if ins:
                # pulse captura desde la fuente default de PulseAudio (interfaz HUGEL)
                preferred_in = next(
                    (i for i, name in enumerate(ins) if name == "pulse"),
                    next((i for i, name in enumerate(ins) if name == "default"), 0),
                )
                self.input_combo.current(preferred_in)
            if outs:
                # pulse envia a la salida default de PulseAudio (donde suena YouTube)
                preferred_out = next(
                    (i for i, name in enumerate(outs) if name == "pulse"),
                    next((i for i, name in enumerate(outs) if name == "default"), 0),
                )
                self.output_combo.current(preferred_out)
        except Exception as exc:
            messagebox.showerror("Error de audio", str(exc))

    # ── Audio ─────────────────────────────────────────────────────────────────

    def _toggle_audio(self):
        if self.engine.running:
            self.engine.stop()
            self.start_btn.config(text="  Iniciar  ", bg="#2e7d32", activebackground="#1b5e20")
            self.status_lbl.config(text="Detenido", fg=FG_DIM)
        else:
            try:
                self.engine.start(
                    input_name=self.input_var.get(),
                    output_name=self.output_var.get(),
                    sample_rate=int(self.samplerate_var.get()),
                    buffer_size=int(self.buffer_var.get()),
                )
                self.engine.update_chain(self.chain)
                self.start_btn.config(text="  Detener  ", bg="#c62828", activebackground="#b71c1c")
                self.status_lbl.config(text="En vivo", fg="#66ff66")
            except Exception as exc:
                messagebox.showerror("Error al iniciar audio", str(exc))

    def _push_chain(self):
        """Envia la cadena actualizada al motor de audio."""
        if self.engine.running:
            try:
                self.engine.update_chain(self.chain)
            except Exception as exc:
                print(f"Error actualizando cadena: {exc}")

    # ── Gestion de pedales ────────────────────────────────────────────────────

    def _add_pedal(self, pedal_type: str):
        pedal = ActivePedal(pedal_type)
        self.chain.append(pedal)
        self._select_pedal(pedal)  # ya llama _rebuild_chain_ui internamente
        self._push_chain()

    def _remove_pedal(self, pedal: ActivePedal):
        if pedal in self.chain:
            self.chain.remove(pedal)
        if self.selected is pedal:
            self.selected = None
            self._show_editor_placeholder()
        self._rebuild_chain_ui()
        self._push_chain()

    def _move_pedal(self, pedal: ActivePedal, direction: int):
        idx = self.chain.index(pedal)
        new_idx = idx + direction
        if 0 <= new_idx < len(self.chain):
            self.chain[idx], self.chain[new_idx] = self.chain[new_idx], self.chain[idx]
            self._rebuild_chain_ui()
            self._push_chain()

    def _toggle_pedal(self, pedal: ActivePedal):
        pedal.enabled = not pedal.enabled
        self._rebuild_chain_ui()
        self._push_chain()

    def _select_pedal(self, pedal: ActivePedal):
        self.selected = pedal
        self._rebuild_chain_ui()
        self._build_editor(pedal)

    # ── Cadena UI ─────────────────────────────────────────────────────────────

    def _rebuild_chain_ui(self):
        for w in self.chain_inner.winfo_children():
            w.destroy()

        if not self.chain:
            self.empty_lbl.pack(expand=True, pady=30)
            self.chain_canvas.configure(height=10)
            return

        self.empty_lbl.pack_forget()
        self.chain_canvas.configure(height=255)

        for i, pedal in enumerate(self.chain):
            if i > 0:
                tk.Label(self.chain_inner, text="->", bg=BG, fg="#334455",
                         font=("Helvetica", 18)).pack(side="left", padx=2)
            self._draw_pedal_canvas(self.chain_inner, pedal, i)

        self.chain_canvas.update_idletasks()
        self._on_chain_resize()

    def _draw_pedal_canvas(self, parent: tk.Widget, pedal: ActivePedal, idx: int):
        style   = PEDAL_STYLES[pedal.pedal_type]
        enabled = pedal.enabled
        selected = (pedal is self.selected)

        W, H = 122, 205   # dimensiones del canvas

        body   = style["body"]   if enabled else "#3a3a4a"
        accent = style["accent"] if enabled else "#2a2a3a"
        light  = _lighten(body, 55) if enabled else "#4a4a5a"
        shadow = _darken(body, 45)
        kfill  = style["knob_color"] if enabled else "#333344"
        txt    = "#f0f0f0" if enabled else "#666677"

        border_color = "#ffffff" if selected else "#1a1a2e"
        outer = tk.Frame(parent, bg=border_color, padx=2, pady=2)
        outer.pack(side="left", padx=3, pady=8)

        cv = tk.Canvas(outer, width=W, height=H, bg="#111111",
                       highlightthickness=0, cursor="hand2")
        cv.pack()

        # ── Cuerpo metalico ─────────────────────────────────
        cv.create_rectangle(6, 6, W - 4, H - 38, fill="#0a0a0a", outline="")  # sombra
        cv.create_rectangle(4, 4, W - 6, H - 40, fill=body, outline=shadow, width=1)
        cv.create_line(4,    4, W - 6,    4, fill=light, width=2)   # borde superior
        cv.create_line(4,    4,    4, H - 40, fill=light, width=2)  # borde izquierdo
        cv.create_line(4, H-40, W - 6, H - 40, fill=shadow, width=1)
        cv.create_line(W-6,  4, W - 6, H - 40, fill=shadow, width=1)

        # ── Marca (brand) ────────────────────────────────────
        cv.create_text(W // 2, 14, text=style["brand"], fill=txt,
                       font=("Helvetica", 7, "bold"))

        # ── LED ──────────────────────────────────────────────
        led_fill = "#00ff55" if enabled else "#111111"
        led_out  = "#005500" if enabled else "#222222"
        cv.create_oval(W-18, 8, W-9, 17, fill=led_fill, outline=led_out)

        # ── Linea separadora superior ────────────────────────
        cv.create_line(8, 23, W - 8, 23, fill=accent, width=1)

        # ── Perillas (knobs) ─────────────────────────────────
        knobs = style["knobs"]
        n_knobs = len(knobs)
        knob_y = 68
        KR = 13
        if n_knobs == 1:
            xs = [W // 2]
        elif n_knobs == 2:
            xs = [W // 3, 2 * W // 3]
        else:
            xs = [W // 4, W // 2, 3 * W // 4]

        for xi, lbl in zip(xs, knobs[:3]):
            cv.create_oval(xi-KR+1, knob_y-KR+1, xi+KR+1, knob_y+KR+1,
                           fill="#060606", outline="")
            cv.create_oval(xi-KR, knob_y-KR, xi+KR, knob_y+KR,
                           fill=kfill, outline=_darken(kfill, 25))
            # Indicador (linea apuntando a la 1 en punto)
            ang = -math.pi / 4
            ix = xi + (KR - 4) * math.sin(ang)
            iy = knob_y - (KR - 4) * math.cos(ang)
            cv.create_line(xi, knob_y, int(ix), int(iy),
                           fill="#cccccc" if enabled else "#444455",
                           width=2, capstyle="round")
            # Reflejo pequeño
            cv.create_oval(xi-KR+3, knob_y-KR+3, xi-KR+8, knob_y-KR+8,
                           fill=_lighten(kfill, 50) if enabled else "#2a2a3a",
                           outline="")
            cv.create_text(xi, knob_y + KR + 8, text=lbl,
                           fill=txt, font=("Helvetica", 6))

        # ── Nombre del modelo ────────────────────────────────
        cv.create_text(W // 2, 112, text=style["model"], fill=txt,
                       font=("Helvetica", 10, "bold"))

        # ── Tipo de efecto ───────────────────────────────────
        cv.create_text(W // 2, 126, text=pedal.pedal_type.upper(),
                       fill=_lighten(accent, 60) if enabled else "#444455",
                       font=("Helvetica", 6), width=W - 10)

        # ── Separador y zona del footswitch ──────────────────
        cv.create_line(8, H-72, W-8, H-72, fill=accent, width=1)
        cv.create_rectangle(4, H-70, W-6, H-40, fill=_darken(body, 30), outline=shadow)

        scx, scy, SR = W // 2, H - 55, 14
        cv.create_oval(scx-SR-1, scy-SR-1, scx+SR+1, scy+SR+1,
                       fill="#060606", outline="")
        cv.create_oval(scx-SR, scy-SR, scx+SR, scy+SR,
                       fill="#1c1c1c", outline="#333333")
        cv.create_oval(scx-SR+3, scy-SR+3, scx+SR-3, scy+SR-3,
                       fill="#252525", outline="")

        # ── Goma inferior ────────────────────────────────────
        cv.create_rectangle(4, H-40, W-6, H-4, fill="#090909", outline="#111111")

        # Clic en el canvas para seleccionar
        cv.bind("<Button-1>", lambda _, p=pedal: self._select_pedal(p))

        # ── Botones de control debajo del canvas ─────────────
        btn_row = tk.Frame(outer, bg="#1a1a2e")
        btn_row.pack(fill="x")

        onoff_bg = "#1b5e20" if enabled else "#7f0000"
        tk.Button(btn_row, text="ON" if enabled else "OFF",
                  bg=onoff_bg, fg="white", font=("Helvetica", 7, "bold"),
                  relief="flat", padx=4, cursor="hand2",
                  command=lambda p=pedal: self._toggle_pedal(p)
                  ).pack(side="left", fill="x", expand=True)

        if idx > 0:
            tk.Button(btn_row, text="<", bg="#222233", fg="#aaa",
                      relief="flat", padx=3, cursor="hand2",
                      command=lambda p=pedal: self._move_pedal(p, -1)
                      ).pack(side="left")
        if idx < len(self.chain) - 1:
            tk.Button(btn_row, text=">", bg="#222233", fg="#aaa",
                      relief="flat", padx=3, cursor="hand2",
                      command=lambda p=pedal: self._move_pedal(p, 1)
                      ).pack(side="left")

        tk.Button(btn_row, text="X", bg="#7a1a1a", fg="white",
                  relief="flat", padx=4, cursor="hand2",
                  command=lambda p=pedal: self._remove_pedal(p)
                  ).pack(side="right")

    # ── Editor de parametros ──────────────────────────────────────────────────

    def _build_editor(self, pedal: ActivePedal):
        for w in self.editor_scroll_frame.winfo_children():
            w.destroy()

        color = pedal.color
        defn = PEDALS[pedal.pedal_type]

        # Titulo
        tk.Label(self.editor_scroll_frame, text=pedal.pedal_type,
                 bg=BG_PANEL, fg=color, font=("Helvetica", 12, "bold")).pack(pady=(0, 10))

        # Un slider por parametro
        for key, meta in defn["params"].items():
            # Seccion del parametro
            sect = tk.Frame(self.editor_scroll_frame, bg=BG_PANEL)
            sect.pack(fill="x", pady=5)

            # Label + valor actual
            header = tk.Frame(sect, bg=BG_PANEL)
            header.pack(fill="x")

            tk.Label(header, text=meta["label"], bg=BG_PANEL, fg=FG,
                     font=FONT, anchor="w").pack(side="left")

            var = tk.DoubleVar(value=pedal.params[key])
            val_lbl = tk.Label(header,
                                text=f"{pedal.params[key]:.2f}{meta['unit']}",
                                bg=BG_PANEL, fg=color, font=FONT_SMALL, width=10, anchor="e")
            val_lbl.pack(side="right")

            # Slider
            def _make_cb(k=key, v=var, lbl=val_lbl, u=meta["unit"], p=pedal):
                def _cb(value):
                    val = float(value)
                    p.set_param(k, val)
                    lbl.config(text=f"{val:.2f}{u}")
                    self._push_chain()
                return _cb

            slider = ttk.Scale(sect, from_=meta["min"], to=meta["max"],
                               variable=var, orient="horizontal",
                               command=_make_cb())
            slider.pack(fill="x", pady=(2, 0))

        # Separador
        tk.Frame(self.editor_scroll_frame, bg="#2a2a4a", height=1).pack(
            fill="x", pady=12)

        # Boton restablecer
        def _reset():
            pedal.reset_params()
            self._build_editor(pedal)
            self._rebuild_chain_ui()
            self._push_chain()

        tk.Button(self.editor_scroll_frame, text="Restablecer valores",
                  bg="#222233", fg=FG_DIM, font=FONT, relief="flat", pady=6,
                  cursor="hand2", command=_reset).pack(fill="x")

    # ── Mensaje de dependencias faltantes ─────────────────────────────────────

    def _show_missing_deps(self):
        msg = (
            "Faltan dependencias.\n\n"
            "Ejecuta en la terminal:\n\n"
            "  pip install pedalboard\n\n"
            f"Detalle: {MISSING_MSG}"
        )
        for w in self.chain_outer.winfo_children():
            w.destroy()
        tk.Label(self.chain_outer, text=msg, bg=BG, fg="#ff6666",
                 font=("Helvetica", 11), justify="left").pack(expand=True)

    # ── Afinador UI ───────────────────────────────────────────────────────────

    def _build_tuner_panel(self):
        tk.Frame(self.editor_frame, bg="#2a2a4a", height=1).pack(fill="x", padx=10, pady=(8, 0))

        tuner = tk.Frame(self.editor_frame, bg=BG_PANEL)
        tuner.pack(fill="x", padx=10, pady=(6, 10))

        tk.Label(tuner, text="AFINADOR", bg=BG_PANEL, fg=FG_DIM,
                 font=("Helvetica", 8, "bold")).pack()

        # Nota grande
        self._tuner_note_lbl = tk.Label(
            tuner, text="--", bg=BG_PANEL, fg="#444466",
            font=("Helvetica", 36, "bold"),
        )
        self._tuner_note_lbl.pack()

        # Frecuencia
        self._tuner_freq_lbl = tk.Label(
            tuner, text="--- Hz", bg=BG_PANEL, fg=FG_DIM, font=FONT_SMALL,
        )
        self._tuner_freq_lbl.pack()

        # Barra de cents
        self._tuner_canvas = tk.Canvas(
            tuner, bg="#111122", height=28, highlightthickness=1,
            highlightbackground="#2a2a4a",
        )
        self._tuner_canvas.pack(fill="x", pady=(6, 2))
        self._tuner_canvas.bind("<Configure>", lambda e: self._draw_tuner_bar(None))

        # Etiquetas de referencia
        ref = tk.Frame(tuner, bg=BG_PANEL)
        ref.pack(fill="x")
        tk.Label(ref, text="-50", bg=BG_PANEL, fg="#444", font=("Helvetica", 7)).pack(side="left")
        tk.Label(ref, text="EN TONO", bg=BG_PANEL, fg="#444", font=("Helvetica", 7)).pack(side="left", expand=True)
        tk.Label(ref, text="+50", bg=BG_PANEL, fg="#444", font=("Helvetica", 7)).pack(side="right")

        # Arrancar el polling
        self.after(120, self._update_tuner)

    def _draw_tuner_bar(self, cents: Optional[float]):
        c = self._tuner_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 4:
            return

        # Zonas de color de fondo
        mid = w // 2
        zone_w_green  = int(w * 10 / 100)
        zone_w_yellow = int(w * 25 / 100)

        c.create_rectangle(0,        0, w,                       h, fill="#3a1111", outline="")
        c.create_rectangle(mid - zone_w_yellow, 0, mid + zone_w_yellow, h, fill="#3a3a11", outline="")
        c.create_rectangle(mid - zone_w_green,  0, mid + zone_w_green,  h, fill="#113a11", outline="")

        # Linea central
        c.create_line(mid, 0, mid, h, fill="#335533", width=1)

        if cents is not None:
            # Aguja: cents va de -50 a +50, mapeado a 0..w
            clamped = max(-50.0, min(50.0, cents))
            x = int((clamped + 50) / 100 * w)

            if abs(cents) <= 10:
                color = "#00ff66"
            elif abs(cents) <= 25:
                color = "#ffdd00"
            else:
                color = "#ff4444"

            c.create_rectangle(x - 3, 2, x + 3, h - 2, fill=color, outline="")

    def _update_tuner(self):
        """Polling cada 120 ms para actualizar el panel del afinador."""
        result = self.engine.get_tuner() if self.engine.running else None

        if result is None:
            self._tuner_note_lbl.config(text="--", fg="#444466")
            self._tuner_freq_lbl.config(text="--- Hz")
            self._draw_tuner_bar(None)
        else:
            freq, note, octave, cents = result
            if abs(cents) <= 10:
                color = "#00ff66"
            elif abs(cents) <= 25:
                color = "#ffdd00"
            else:
                color = "#ff4444"
            self._tuner_note_lbl.config(text=f"{note}{octave}", fg=color)
            self._tuner_freq_lbl.config(text=f"{freq:.1f} Hz")
            self._draw_tuner_bar(cents)

        self.after(120, self._update_tuner)

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        self.engine.stop()
        self.destroy()


# ─── Entrada ──────────────────────────────────────────────────────────────────

def main():
    app = GuitarPedalboardApp()
    app.mainloop()


if __name__ == "__main__":
    main()

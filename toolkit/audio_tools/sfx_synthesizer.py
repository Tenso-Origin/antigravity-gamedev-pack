"""
Sintetizador Procedural de Efeitos Sonoros Retro (SFX Synthesizer)
Gera arquivos de áudio .wav (PCM 16-bit) procedurais sem dependências externas.
Ideal para prototipagem rápida e produção de efeitos sonoros clássicos (8-bit / 16-bit).
"""

import math
import random
import struct
import wave
import os
from typing import Dict, Any, List, Optional

SAMPLE_RATE = 44100

def _clamp(val: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
    return max(min_val, min(max_val, val))

class SFXGenerator:
    @staticmethod
    def generate_sfx(params: Dict[str, Any], output_path: str) -> str:
        """
        Gera uma amostra de áudio procedural com base nos parâmetros ADSR e forma de onda.
        """
        wave_type = params.get("wave_type", "square")
        duration = float(params.get("duration", 0.3))
        freq_start = float(params.get("freq_start", 440.0))
        freq_end = float(params.get("freq_end", 220.0))
        attack = float(params.get("attack", 0.01))
        decay = float(params.get("decay", 0.1))
        sustain_level = float(params.get("sustain_level", 0.5))
        release = float(params.get("release", 0.15))
        volume = float(params.get("volume", 0.7))
        vibrato_speed = float(params.get("vibrato_speed", 0.0))
        vibrato_depth = float(params.get("vibrato_depth", 0.0))
        arp_speed = float(params.get("arp_speed", 0.0))
        arp_semitone = float(params.get("arp_semitone", 0.0))
        bitcrush = int(params.get("bitcrush", 0))  # 0 = desligado, 8 = 8-bit, 4 = 4-bit

        num_samples = int(duration * SAMPLE_RATE)
        samples: List[float] = []

        total_envelope_time = attack + decay + release
        if total_envelope_time > duration:
            scale = duration / total_envelope_time
            attack *= scale
            decay *= scale
            release *= scale
        sustain_time = max(0.0, duration - (attack + decay + release))

        phase = 0.0
        lowpass_last = 0.0

        for i in range(num_samples):
            t = i / SAMPLE_RATE

            # Envelope de amplitude ADSR
            if t < attack:
                env = (t / attack) if attack > 0 else 1.0
            elif t < attack + decay:
                dt = t - attack
                env = 1.0 - (1.0 - sustain_level) * (dt / decay) if decay > 0 else sustain_level
            elif t < attack + decay + sustain_time:
                env = sustain_level
            else:
                rt = t - (attack + decay + sustain_time)
                env = sustain_level * (1.0 - (rt / release)) if release > 0 else 0.0
            env = max(0.0, env)

            # Modulação de Frequência (Slide / Sweep)
            progress = t / duration if duration > 0 else 1.0
            current_freq = freq_start + (freq_end - freq_start) * progress

            # Arpeggio (salto de semitons)
            if arp_speed > 0 and t >= arp_speed:
                multiplier = 2.0 ** (arp_semitone / 12.0)
                current_freq *= multiplier

            # Vibrato (LFO de modulação de pitch)
            if vibrato_speed > 0 and vibrato_depth > 0:
                current_freq += math.sin(2.0 * math.pi * vibrato_speed * t) * vibrato_depth

            current_freq = max(20.0, min(SAMPLE_RATE / 2.0 - 100.0, current_freq))

            # Atualização da fase
            phase += current_freq / SAMPLE_RATE
            if phase >= 1.0:
                phase -= math.floor(phase)

            # Síntese da forma de onda
            if wave_type == "sine":
                val = math.sin(2.0 * math.pi * phase)
            elif wave_type == "square":
                val = 1.0 if phase < 0.5 else -1.0
            elif wave_type == "triangle":
                val = 4.0 * abs(phase - 0.5) - 1.0
            elif wave_type == "sawtooth":
                val = 2.0 * phase - 1.0
            elif wave_type == "noise":
                raw_noise = random.uniform(-1.0, 1.0)
                # Filtro passa-baixa simples para ruídos mais suaves
                val = lowpass_last + 0.3 * (raw_noise - lowpass_last)
                lowpass_last = val
            else:
                val = math.sin(2.0 * math.pi * phase)

            # Aplicação de bitcrush se requisitado
            if bitcrush > 0:
                steps = 2 ** bitcrush
                val = round(val * steps) / steps

            sample = val * env * volume
            samples.append(_clamp(sample))

        # Gravação em formato WAV (PCM 16-bit mono)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(1)        # Mono
            wav_file.setsampwidth(2)       # 16 bits = 2 bytes
            wav_file.setframerate(SAMPLE_RATE)
            
            raw_data = bytearray()
            for s in samples:
                int_val = int(s * 32767.0)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))
            
            wav_file.writeframes(raw_data)

        return os.path.abspath(output_path)

    @classmethod
    def preset(cls, preset_name: str, output_path: str, **kwargs) -> str:
        """
        Gera efeitos sonoros procedurais baseados em presets clássicos de videogames.
        """
        presets = {
            "jump": {
                "wave_type": "square",
                "duration": 0.16,
                "freq_start": 160.0,
                "freq_end": 520.0,
                "attack": 0.005,
                "decay": 0.05,
                "sustain_level": 0.4,
                "release": 0.1,
                "volume": 0.65,
                "bitcrush": 8
            },
            "laser": {
                "wave_type": "sawtooth",
                "duration": 0.15,
                "freq_start": 980.0,
                "freq_end": 90.0,
                "attack": 0.002,
                "decay": 0.06,
                "sustain_level": 0.2,
                "release": 0.08,
                "volume": 0.7
            },
            "explosion": {
                "wave_type": "noise",
                "duration": 0.45,
                "freq_start": 200.0,
                "freq_end": 30.0,
                "attack": 0.01,
                "decay": 0.18,
                "sustain_level": 0.35,
                "release": 0.25,
                "volume": 0.8
            },
            "hit": {
                "wave_type": "triangle",
                "duration": 0.12,
                "freq_start": 320.0,
                "freq_end": 60.0,
                "attack": 0.005,
                "decay": 0.04,
                "sustain_level": 0.15,
                "release": 0.07,
                "volume": 0.75,
                "bitcrush": 6
            },
            "coin": {
                "wave_type": "sine",
                "duration": 0.32,
                "freq_start": 987.77,  # Nota B5
                "freq_end": 1318.51,   # Nota E6
                "attack": 0.005,
                "decay": 0.08,
                "sustain_level": 0.6,
                "release": 0.2,
                "arp_speed": 0.07,
                "arp_semitone": 5.0,
                "volume": 0.65
            },
            "powerup": {
                "wave_type": "triangle",
                "duration": 0.42,
                "freq_start": 261.63,  # C4
                "freq_end": 783.99,    # G5
                "attack": 0.01,
                "decay": 0.1,
                "sustain_level": 0.7,
                "release": 0.15,
                "vibrato_speed": 12.0,
                "vibrato_depth": 25.0,
                "volume": 0.65
            },
            "slash": {
                "wave_type": "noise",
                "duration": 0.14,
                "freq_start": 600.0,
                "freq_end": 120.0,
                "attack": 0.005,
                "decay": 0.04,
                "sustain_level": 0.3,
                "release": 0.09,
                "volume": 0.7
            },
            "step": {
                "wave_type": "noise",
                "duration": 0.07,
                "freq_start": 180.0,
                "freq_end": 60.0,
                "attack": 0.003,
                "decay": 0.03,
                "sustain_level": 0.2,
                "release": 0.03,
                "volume": 0.5
            }
        }

        if preset_name not in presets:
            raise ValueError(f"Preset '{preset_name}' desconhecido. Disponíveis: {list(presets.keys())}")

        cfg = dict(presets[preset_name])
        cfg.update(kwargs)
        return cls.generate_sfx(cfg, output_path)

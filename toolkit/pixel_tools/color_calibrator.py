"""
Módulo para extração, auditoria e harmonização de perfis de cores e saturação (HSV).
Garante consistência cromática estrita entre frames de animação.
"""

from typing import Dict, List, Tuple
from PIL import Image
import colorsys
import numpy as np


def extract_palette_profile(image: Image.Image, alpha_threshold: int = 50) -> Dict[str, float]:
    """
    Extrai as métricas de saturação e brilho médias no espaço HSV de uma imagem.
    """
    im_rgba = image.convert("RGBA")
    w, h = im_rgba.size
    pixels = [im_rgba.getpixel((x, y)) for y in range(h) for x in range(w) if im_rgba.getpixel((x, y))[3] > alpha_threshold]
    
    if not pixels:
        return {"avg_sat": 0.0, "avg_val": 0.0, "sample_count": 0}

    hsvs = [colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0) for r, g, b, a in pixels]
    sats = [s for h, s, v in hsvs]
    vals = [v for h, s, v in hsvs]

    return {
        "avg_saturation": round(float(np.mean(sats)), 3),
        "avg_brightness": round(float(np.mean(vals)), 3),
        "saturation_p80": round(float(np.percentile(sats, 80)), 3),
        "brightness_p80": round(float(np.percentile(vals, 80)), 3),
        "sample_count": len(pixels)
    }


def harmonize_colors(
    image: Image.Image,
    target_sat_scale: float = 1.0,
    target_val_scale: float = 1.0,
    hue_filter_range: Tuple[float, float] = (0.0, 1.0)
) -> Image.Image:
    """
    Ajusta a saturação e o brilho dos pixels dentro de uma faixa de matiz (Hue).
    Útil para calibrar cores específicas (ex: verdes de roupas, dourado de cabelos ou metais).
    """
    im_rgba = image.convert("RGBA")
    w, h = im_rgba.size
    out = im_rgba.copy()

    h_min, h_max = hue_filter_range

    for y in range(h):
        for x in range(w):
            r, g, b, a = im_rgba.getpixel((x, y))
            if a < 30:
                continue
            h_val, s_val, v_val = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

            if h_min <= h_val <= h_max:
                s_new = min(1.0, max(0.0, s_val * target_sat_scale))
                v_new = min(1.0, max(0.0, v_val * target_val_scale))
                r_n, g_n, b_n = colorsys.hsv_to_rgb(h_val, s_new, v_new)
                out.putpixel((x, y), (int(round(r_n * 255)), int(round(g_n * 255)), int(round(b_n * 255)), a))

    return out

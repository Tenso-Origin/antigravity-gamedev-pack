"""
Módulo para extração, centralização e geração de Atlas de Itens / HUD para Godot.
Substitui e expande a função `forge_item_kit` do PixelForge MCP.
"""

import os
import json
import math
from typing import List, Tuple, Dict, Optional
from PIL import Image
import numpy as np
from .sprite_splitter import detect_sprite_islands


def process_item_kit(
    input_path: str,
    output_dir: str,
    target_size: int = 16,
    prefix: str = "item",
    remove_black_bg: bool = True,
    black_threshold: int = 25
) -> List[str]:
    """
    Fatia um conjunto de itens e padroniza cada ícone centralizado em células quadradas
    de tamanho fixo (ex: 16x16, 24x24 ou 32x32), ideal para inventários e HUD do Godot.
    """
    os.makedirs(output_dir, exist_ok=True)
    im = Image.open(input_path).convert("RGBA")
    w, h = im.size

    if remove_black_bg:
        transparent = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for y in range(h):
            for x in range(w):
                r, g, b, a = im.getpixel((x, y))
                if r <= black_threshold and g <= black_threshold and b <= black_threshold:
                    continue
                transparent.putpixel((x, y), (r, g, b, a))
        im = transparent

    boxes = detect_sprite_islands(im, min_pixels=15)
    saved_items = []

    for idx, box in enumerate(boxes):
        item_crop = im.crop(box)
        # Se for maior que o target, escala preservando proporção
        max_dim = max(item_crop.width, item_crop.height)
        if max_dim > target_size:
            scale = target_size / float(max_dim)
            new_w = max(1, int(round(item_crop.width * scale)))
            new_h = max(1, int(round(item_crop.height * scale)))
            item_crop = item_crop.resize((new_w, new_h), Image.Resampling.NEAREST)

        # Centralizar na célula quadrada
        cell = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
        pos_x = (target_size - item_crop.width) // 2
        pos_y = (target_size - item_crop.height) // 2
        cell.paste(item_crop, (pos_x, pos_y), item_crop)

        out_path = os.path.join(output_dir, f"{prefix}_{idx:02d}.png")
        cell.save(out_path)
        saved_items.append(out_path)

    return saved_items


def pack_item_atlas(
    item_paths: List[str],
    output_atlas_path: str,
    item_size: int = 16,
    columns: Optional[int] = None
) -> Dict[str, any]:
    """
    Empacota múltiplos itens individuais em uma folha única de AtlasTexture compatível com Godot,
    gerando um manifesto JSON com os retângulos de região (region rect) de cada item.
    """
    if not item_paths:
        return {}

    n = len(item_paths)
    if not columns:
        columns = max(1, math.ceil(math.sqrt(n)))
    rows = math.ceil(n / float(columns))

    atlas_w = columns * item_size
    atlas_h = rows * item_size
    atlas = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))

    manifest = {"item_size": item_size, "atlas_size": [atlas_w, atlas_h], "items": {}}

    for idx, path in enumerate(item_paths):
        c = idx % columns
        r = idx // columns
        pos_x = c * item_size
        pos_y = r * item_size

        item = Image.open(path).convert("RGBA")
        if item.size != (item_size, item_size):
            item = item.resize((item_size, item_size), Image.Resampling.NEAREST)

        atlas.paste(item, (pos_x, pos_y), item)
        item_name = os.path.splitext(os.path.basename(path))[0]
        manifest["items"][item_name] = {
            "x": pos_x,
            "y": pos_y,
            "width": item_size,
            "height": item_size
        }

    os.makedirs(os.path.dirname(os.path.abspath(output_atlas_path)), exist_ok=True)
    atlas.save(output_atlas_path)

    json_path = os.path.splitext(output_atlas_path)[0] + ".json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "atlas_path": output_atlas_path,
        "json_path": json_path,
        "total_items": n
    }

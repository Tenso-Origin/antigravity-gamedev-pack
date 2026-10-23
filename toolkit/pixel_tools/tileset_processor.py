"""
Módulo para fatiamento, verificação de repetição contínua e montagem de Tilesets para Godot.
Substitui e expande a função `forge_tileset` do PixelForge MCP.
"""

import os
from typing import List, Tuple, Dict
from PIL import Image
import numpy as np


def slice_grid(
    input_path: str,
    output_dir: str,
    tile_size: Tuple[int, int] = (16, 16),
    prefix: str = "tile",
    skip_empty: bool = True
) -> List[str]:
    """
    Fatia uma imagem em uma grade regular de tiles (ex: 16x16 ou 32x32).
    """
    os.makedirs(output_dir, exist_ok=True)
    im = Image.open(input_path).convert("RGBA")
    w, h = im.size
    tw, th = tile_size

    cols = w // tw
    rows = h // th

    saved_tiles = []
    for r in range(rows):
        for c in range(cols):
            x = c * tw
            y = r * th
            tile = im.crop((x, y, x + tw, y + th))

            # Verificar se o tile é vazio (transparente ou preto puro)
            if skip_empty:
                bbox = tile.getbbox()
                if not bbox:
                    continue
                # Se for completamente preto sem alfa
                arr = np.array(tile)
                if np.all(arr[:, :, :3] < 10) and np.all(arr[:, :, 3] > 200):
                    continue

            filename = f"{prefix}_r{r:02d}_c{c:02d}.png"
            tile_path = os.path.join(output_dir, filename)
            tile.save(tile_path)
            saved_tiles.append(tile_path)

    return saved_tiles


def verify_seamless_tile(image: Image.Image) -> Dict[str, float]:
    """
    Verifica a continuidade das bordas de um tile para repetição contínua (seamless).
    Retorna a diferença média de cor (RGB) nas bordas horizontal e vertical.
    Scores próximos de 0 indicam repetição perfeita sem costuras.
    """
    arr = np.array(image.convert("RGB")).astype(float)
    h, w, _ = arr.shape

    # Borda esquerda vs borda direita
    left_edge = arr[:, 0, :]
    right_edge = arr[:, -1, :]
    horiz_diff = float(np.mean(np.abs(left_edge - right_edge)))

    # Borda superior vs borda inferior
    top_edge = arr[0, :, :]
    bottom_edge = arr[-1, :, :]
    vert_diff = float(np.mean(np.abs(top_edge - bottom_edge)))

    return {
        "horizontal_seam_error": round(horiz_diff, 2),
        "vertical_seam_error": round(vert_diff, 2),
        "is_horizontal_seamless": horiz_diff < 15.0,
        "is_vertical_seamless": vert_diff < 15.0,
    }


def process_tileset(
    input_path: str,
    output_path: str,
    tile_size: Tuple[int, int] = (16, 16),
    margin: int = 0,
    spacing: int = 0
) -> str:
    """
    Padroniza e organiza uma imagem de tileset em uma grade limpa com espaçamento opcional
    para evitar sangramento de textura (texture bleeding) em engines 2D como Godot.
    """
    im = Image.open(input_path).convert("RGBA")
    w, h = im.size
    tw, th = tile_size

    cols = w // tw
    rows = h // th

    new_w = margin * 2 + cols * tw + (cols - 1) * spacing
    new_h = margin * 2 + rows * th + (rows - 1) * spacing
    out = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))

    for r in range(rows):
        for c in range(cols):
            x = c * tw
            y = r * th
            tile = im.crop((x, y, x + tw, y + th))

            dest_x = margin + c * (tw + spacing)
            dest_y = margin + r * (th + spacing)
            out.paste(tile, (dest_x, dest_y), tile)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    out.save(output_path)
    return output_path

"""
Módulo para detecção, fatiamento e alinhamento automático de spritesheets.
Substitui e supera a função `process_sprite(split: true)` do PixelForge MCP.
"""

import os
from typing import List, Tuple, Optional
from PIL import Image
import numpy as np


def detect_sprite_islands(
    image: Image.Image,
    alpha_threshold: int = 25,
    min_pixels: int = 30
) -> List[Tuple[int, int, int, int]]:
    """
    Detecta ilhas de pixels conexas (bounding boxes de cada sprite) em uma imagem transparente.
    Retorna lista de tuplas (x_min, y_min, x_max, y_max) ordenadas da esquerda para a direita,
    agrupadas por linhas horizontais.
    """
    im_rgba = image.convert("RGBA")
    w, h = im_rgba.size
    alpha = np.array(im_rgba)[:, :, 3] > alpha_threshold

    visited = np.zeros((h, w), dtype=bool)
    boxes = []

    for y in range(h):
        for x in range(w):
            if alpha[y, x] and not visited[y, x]:
                # BFS para encontrar a ilha completa
                queue = [(y, x)]
                visited[y, x] = True
                min_x, max_x = x, x
                min_y, max_y = y, y
                pixel_count = 0

                while queue:
                    cy, cx = queue.pop()
                    pixel_count += 1
                    min_x = min(min_x, cx)
                    max_x = max(max_x, cx)
                    min_y = min(min_y, cy)
                    max_y = max(max_y, cy)

                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and alpha[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            queue.append((ny, nx))

                if pixel_count >= min_pixels:
                    boxes.append((min_x, min_y, max_x + 1, max_y + 1))

    # Ordenação espacial inteligente: ordenar por linhas (Y com tolerância) e depois por X
    if not boxes:
        return []

    # Altura média estimada para agrupar em linhas
    avg_h = max(1, sum(b[3] - b[1] for b in boxes) // len(boxes))
    row_tolerance = avg_h // 2

    def sort_key(b):
        row_bucket = b[1] // row_tolerance
        return (row_bucket, b[0])

    boxes.sort(key=sort_key)
    return boxes


def split_spritesheet(
    input_path: str,
    output_dir: str,
    prefix: str = "frame",
    remove_black_bg: bool = True,
    black_threshold: int = 25,
    canvas_size: Optional[Tuple[int, int]] = None,
    ground_y: Optional[int] = None,
    target_height: Optional[int] = None,
    padding: int = 0
) -> List[str]:
    """
    Fatia um spritesheet em arquivos individuais de frames PNG.
    
    Args:
        input_path: Caminho da imagem de entrada.
        output_dir: Diretório onde salvar os frames.
        prefix: Prefixo do nome dos arquivos gerados (ex: 'attack_normal').
        remove_black_bg: Remove automaticamente fundo preto/escuro.
        black_threshold: Limiar RGB para remoção de preto.
        canvas_size: Tamanho do canvas final (ex: (110, 96)). Se None, salva recortado (trimmed).
        ground_y: Linha Y do solo para cravar a base dos pés.
        target_height: Altura fixa exata em pixels (H_orig) usando Nearest Neighbor.
        padding: Padding em pixels ao redor do sprite recortado.
        
    Returns:
        Lista com os caminhos dos arquivos gerados.
    """
    os.makedirs(output_dir, exist_ok=True)
    im = Image.open(input_path).convert("RGBA")
    w, h = im.size

    # Remover fundo preto se solicitado
    if remove_black_bg:
        transparent = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for y in range(h):
            for x in range(w):
                r, g, b, a = im.getpixel((x, y))
                if r <= black_threshold and g <= black_threshold and b <= black_threshold:
                    continue
                transparent.putpixel((x, y), (r, g, b, a))
        im = transparent

    boxes = detect_sprite_islands(im)
    if not boxes:
        # Se for imagem única sem ilhas separadas, usa o bbox geral
        bbox = im.getbbox()
        if bbox:
            boxes = [bbox]

    saved_files = []
    for idx, box in enumerate(boxes):
        sprite = im.crop(box)

        # Redimensionamento para target_height se especificado
        if target_height and sprite.height > 0:
            scale = target_height / float(sprite.height)
            target_w = max(1, int(round(sprite.width * scale)))
            sprite = sprite.resize((target_w, target_height), Image.Resampling.NEAREST)

        # Montagem no canvas padrão ou corte direto
        if canvas_size:
            cw, ch = canvas_size
            frame_canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            if ground_y is not None:
                pos_y = ground_y - sprite.height
            else:
                pos_y = (ch - sprite.height) // 2
            pos_x = (cw - sprite.width) // 2
            frame_canvas.paste(sprite, (pos_x, pos_y), sprite)
            out_img = frame_canvas
        else:
            if padding > 0:
                padded = Image.new("RGBA", (sprite.width + padding * 2, sprite.height + padding * 2), (0, 0, 0, 0))
                padded.paste(sprite, (padding, padding), sprite)
                out_img = padded
            else:
                out_img = sprite

        out_path = os.path.join(output_dir, f"{prefix}_{idx}.png")
        out_img.save(out_path)
        saved_files.append(out_path)

    return saved_files

"""
Módulo para processamento de cenários em camadas de Parallax e loop horizontal contínuo.
Substitui e expande a função `forge_background` do PixelForge MCP.
"""

import os
import json
from typing import List, Tuple, Dict, Optional
from PIL import Image
import numpy as np


def make_seamless_horizontal(image: Image.Image, blend_width: int = 16) -> Image.Image:
    """
    Suaviza e mescla as bordas laterais esquerda e direita de uma imagem de fundo
    para garantir repetição horizontal contínua e infinita (seamless horizontal scrolling).
    """
    im_rgba = image.convert("RGBA")
    w, h = im_rgba.size
    arr = np.array(im_rgba).astype(float)

    blend_w = min(blend_width, w // 4)
    out_arr = arr.copy()

    # Interpolação linear entre a borda esquerda e a borda direita
    for x in range(blend_w):
        factor = x / float(blend_w)
        # Mistura o início (esquerda) com o final (direita)
        blended = (1.0 - factor) * arr[:, -(blend_w - x), :] + factor * arr[:, x, :]
        out_arr[:, x, :] = blended
        out_arr[:, -(blend_w - x), :] = blended

    return Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8))


def process_parallax_layers(
    layers: List[str],
    output_dir: str,
    target_height: int = 180,
    seamless_wrap: bool = True,
    blend_width: int = 16
) -> Dict[str, any]:
    """
    Processa múltiplas camadas de parallax, redimensiona proporcionalmente mantendo
    pixel art nítido, aplica loop contínuo nas bordas e gera metadados para Godot.
    
    Args:
        layers: Lista de caminhos para as imagens de cada camada (ordenadas da mais distante para a mais próxima).
        output_dir: Diretório de destino.
        target_height: Altura alvo de renderização nativa (ex: 180 px para jogos em 320x180).
        seamless_wrap: Aplica mesclagem de bordas para repetição infinita.
        blend_width: Largura em pixels da transição de bordas.
        
    Returns:
        Dicionário com a configuração pronta para o Godot (motion_scale, mirroring, etc.).
    """
    os.makedirs(output_dir, exist_ok=True)
    layer_info = []

    # Escalares de movimento sugeridos da camada mais distante para a mais próxima
    default_speeds = [0.1, 0.25, 0.5, 0.75, 1.0]

    for i, layer_path in enumerate(layers):
        im = Image.open(layer_path).convert("RGBA")
        
        # Redimensionar altura mantendo aspect ratio com amostragem limpa
        scale = target_height / float(im.height)
        new_w = int(round(im.width * scale))
        resized = im.resize((new_w, target_height), Image.Resampling.NEAREST)

        # Aplicar repetição horizontal se solicitado
        if seamless_wrap:
            processed = make_seamless_horizontal(resized, blend_width=blend_width)
        else:
            processed = resized

        filename = f"parallax_layer_{i}.png"
        out_file = os.path.join(output_dir, filename)
        processed.save(out_file)

        speed = default_speeds[min(i, len(default_speeds) - 1)]
        layer_info.append({
            "index": i,
            "filename": filename,
            "width": processed.width,
            "height": processed.height,
            "motion_scale": {"x": speed, "y": 1.0},
            "motion_mirroring": {"x": processed.width, "y": 0}
        })

    config_path = os.path.join(output_dir, "parallax_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(layer_info, f, indent=2)

    return {
        "output_dir": output_dir,
        "layers": layer_info,
        "config_file": config_path
    }

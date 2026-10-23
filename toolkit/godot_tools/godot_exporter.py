"""
Godot 4 Resource Exporter (godot_exporter.py)
Gera arquivos nativos de recursos do Godot 4 (.tres) diretamente a partir de sequências de sprites e assets.
Suporta:
- SpriteFrames (.tres) para AnimatedSprite2D com múltiplas animações, FPS e controle de loop.
"""

import os
import re
import random
import string
from typing import List, Dict, Any, Optional

def _generate_godot_uid() -> str:
    """Gera um UID compatível com o formato interno do Godot 4."""
    chars = string.ascii_lowercase + string.digits
    token = "".join(random.choice(chars) for _ in range(12))
    return f"uid://{token}"

class GodotExporter:
    @staticmethod
    def create_sprite_frames(
        animations_data: List[Dict[str, Any]],
        output_tres_path: str,
        project_root: Optional[str] = None
    ) -> str:
        """
        Compila sequências de imagens em um recurso Godot 4 SpriteFrames (.tres).
        
        animations_data: lista de dicionários no formato:
        [
            {
                "name": "attack_normal_w",
                "speed": 10.0,
                "loop": False,
                "frames": ["sprites/hero_w/attack_normal_0.png", ...]
            }
        ]
        """
        if project_root is None:
            # Assume o diretório atual como raiz do projeto Godot (onde fica o project.godot)
            project_root = os.getcwd()

        all_frames_paths: List[str] = []
        for anim in animations_data:
            for f_path in anim.get("frames", []):
                norm_p = os.path.normpath(f_path)
                if norm_p not in all_frames_paths:
                    all_frames_paths.append(norm_p)

        # Mapeamento de ext_resource id e res:// path
        ext_resources: List[Dict[str, str]] = []
        path_to_res_id: Dict[str, str] = {}

        for idx, abs_or_rel_path in enumerate(all_frames_paths, start=1):
            abs_p = os.path.abspath(abs_or_rel_path)
            # Converter para res:// relativo à raiz do projeto
            rel_to_proj = os.path.relpath(abs_p, project_root).replace("\\", "/")
            res_path = f"res://{rel_to_proj}"
            res_id = f"{idx}_{''.join(random.choices(string.ascii_lowercase, k=5))}"
            uid = _generate_godot_uid()

            ext_resources.append({
                "id": res_id,
                "path": res_path,
                "uid": uid
            })
            path_to_res_id[os.path.normpath(abs_or_rel_path)] = res_id

        # Total load steps = total ext resources + 1 (o próprio recurso)
        load_steps = len(ext_resources) + 1
        main_uid = _generate_godot_uid()

        lines = [
            f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3 uid="{main_uid}"]',
            ""
        ]

        # Ext resources
        for ext in ext_resources:
            lines.append(f'[ext_resource type="Texture2D" uid="{ext["uid"]}" path="{ext["path"]}" id="{ext["id"]}"]')

        lines.append("")
        lines.append("[resource]")
        lines.append("animations = [{")

        # Serialização das animações
        anim_blocks = []
        for anim in animations_data:
            anim_name = anim.get("name", "default")
            speed = float(anim.get("speed", 10.0))
            loop = bool(anim.get("loop", True))
            frames = anim.get("frames", [])

            frame_entries = []
            for f in frames:
                r_id = path_to_res_id.get(os.path.normpath(f))
                if r_id:
                    frame_entries.append(
                        '{\n"duration": 1.0,\n"texture": ExtResource("' + r_id + '")\n}'
                    )

            anim_str = (
                f'"frames": [\n' + ",\n".join(frame_entries) + "\n],\n"
                f'"loop": {"true" if loop else "false"},\n'
                f'"name": &"{anim_name}",\n'
                f'"speed": {speed}'
            )
            anim_blocks.append("{\n" + anim_str + "\n}")

        lines.append(",\n".join(anim_blocks))
        lines.append("}]")

        tres_content = "\n".join(lines) + "\n"

        os.makedirs(os.path.dirname(os.path.abspath(output_tres_path)), exist_ok=True)
        with open(output_tres_path, "w", encoding="utf-8") as f:
            f.write(tres_content)

        return os.path.abspath(output_tres_path)

    @classmethod
    def scan_and_export_spriteframes(
        cls,
        sprite_dir: str,
        output_tres_path: str,
        anim_name: Optional[str] = None,
        speed: float = 10.0,
        loop: bool = True,
        filter_pattern: Optional[str] = None,
        project_root: Optional[str] = None
    ) -> str:
        """
        Escaneia um diretório por arquivos de imagem ordenados numericamente e gera o SpriteFrames .tres.
        filter_pattern: regex opcional para filtrar nomes de arquivo (ex: r"^attack_normal_\\d+\\.png$").
        """
        valid_exts = {".png", ".webp"}
        files = [
            f for f in os.listdir(sprite_dir)
            if os.path.splitext(f)[1].lower() in valid_exts and not f.endswith(".import")
        ]

        if filter_pattern:
            reg = re.compile(filter_pattern)
            files = [f for f in files if reg.search(f)]

        # Ordenação natural por números no nome do arquivo (ex: 0, 1, 2, 10)
        def natural_sort_key(s: str):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]

        files.sort(key=natural_sort_key)
        full_paths = [os.path.join(sprite_dir, f) for f in files]

        if not anim_name:
            anim_name = os.path.basename(os.path.normpath(sprite_dir))

        anim_data = [{
            "name": anim_name,
            "speed": speed,
            "loop": loop,
            "frames": full_paths
        }]

        return cls.create_sprite_frames(anim_data, output_tres_path, project_root)

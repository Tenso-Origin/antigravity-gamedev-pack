"""
PixelToolkit - CLI unificada de ferramentas de Pixel Art para Godot.
Executa operações de fatiamento de spritesheets, geração de tilesets, parallax, kits de itens e calibração de cor.
"""

import sys
import argparse
from PIL import Image
from pixel_tools import (
    split_spritesheet,
    slice_grid,
    verify_seamless_tile,
    process_tileset,
    process_parallax_layers,
    process_item_kit,
    pack_item_atlas,
    extract_palette_profile
)
from audio_tools import SFXGenerator
from godot_tools import GodotExporter


def main():
    parser = argparse.ArgumentParser(description="PixelToolkit - Suíte de Engenharia de Pixel Art para Godot")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # 1. Subcomando: split
    p_split = subparsers.add_parser("split", help="Fatia spritesheet em frames individuais alinhados")
    p_split.add_argument("input", help="Caminho da imagem do spritesheet")
    p_split.add_argument("output", help="Diretório de saída para os frames")
    p_split.add_argument("--prefix", default="frame", help="Prefixo dos arquivos (default: frame)")
    p_split.add_argument("--target-height", type=int, default=None, help="Altura biométrica exata em pixels (H_orig)")
    p_split.add_argument("--canvas", type=int, nargs=2, default=None, help="Tamanho do canvas final (ex: 110 96)")
    p_split.add_argument("--ground", type=int, default=None, help="Linha Y do solo para cravar os pés (ex: 96)")
    p_split.add_argument("--keep-bg", action="store_true", help="Não remove fundo preto")

    # 2. Subcomando: tileset
    p_tile = subparsers.add_parser("tileset", help="Fatia ou padroniza folhas de tilesets")
    p_tile.add_argument("input", help="Caminho da imagem do tileset")
    p_tile.add_argument("output", help="Diretório de saída dos tiles ou caminho do atlas")
    p_tile.add_argument("--size", type=int, default=16, help="Tamanho do tile em pixels (default: 16)")
    p_tile.add_argument("--verify", action="store_true", help="Verifica continuidade das costuras (seamless)")

    # 3. Subcomando: parallax
    p_para = subparsers.add_parser("parallax", help="Processa camadas de fundo de parallax com loop infinito")
    p_para.add_argument("layers", nargs="+", help="Caminhos das imagens das camadas (do fundo para a frente)")
    p_para.add_argument("--out", required=True, help="Diretório de destino")
    p_para.add_argument("--height", type=int, default=180, help="Altura alvo do parallax (default: 180)")

    # 4. Subcomando: items
    p_item = subparsers.add_parser("items", help="Fatia kit de itens/ícones e empacota em AtlasTexture")
    p_item.add_argument("input", help="Caminho da imagem com múltiplos itens")
    p_item.add_argument("output", help="Diretório para os ícones individuais")
    p_item.add_argument("--size", type=int, default=16, help="Tamanho quadrado do ícone (default: 16)")
    p_item.add_argument("--atlas", default=None, help="Caminho opcional para gerar a imagem combinada do Atlas")

    # 5. Subcomando: audit
    p_audit = subparsers.add_parser("audit", help="Audita métricas de saturação e brilho de sprites")
    p_audit.add_argument("sprites", nargs="+", help="Caminhos dos sprites a auditar")

    # 6. Subcomando: sfx
    p_sfx = subparsers.add_parser("sfx", help="Gera efeitos sonoros procedurais retro (.wav)")
    p_sfx.add_argument("preset", choices=["jump", "laser", "explosion", "hit", "coin", "powerup", "slash", "step"], help="Preset do efeito sonoro")
    p_sfx.add_argument("output", help="Caminho do arquivo .wav de saída")
    p_sfx.add_argument("--volume", type=float, default=None, help="Volume relativo (0.0 a 1.0)")
    p_sfx.add_argument("--duration", type=float, default=None, help="Duração customizada em segundos")

    # 7. Subcomando: godot
    p_godot = subparsers.add_parser("godot", help="Compila sequências de sprites em recursos nativos Godot 4 (.tres)")
    p_godot.add_argument("input_dir", help="Diretório contendo os frames da animação")
    p_godot.add_argument("output_tres", help="Caminho do arquivo .tres de saída")
    p_godot.add_argument("--name", default=None, help="Nome da animação (default: nome da pasta)")
    p_godot.add_argument("--fps", type=float, default=10.0, help="Frames por segundo (default: 10.0)")
    p_godot.add_argument("--loop", action="store_true", help="Ativa loop na animação (default: desligado)")
    p_godot.add_argument("--filter", default=None, help="Regex para filtrar arquivos de frame (ex: '^attack_normal_\\d+\\.png$')")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "split":
        canvas = tuple(args.canvas) if args.canvas else None
        files = split_spritesheet(
            input_path=args.input,
            output_dir=args.output,
            prefix=args.prefix,
            remove_black_bg=not args.keep_bg,
            canvas_size=canvas,
            ground_y=args.ground,
            target_height=args.target_height
        )
        print(f"Sucesso! {len(files)} frames gerados em '{args.output}'.")

    elif args.command == "tileset":
        if args.verify:
            im = Image.open(args.input)
            report = verify_seamless_tile(im)
            print("Relatório de Continuidade (Seamless):", report)
        else:
            files = slice_grid(args.input, args.output, tile_size=(args.size, args.size))
            print(f"Sucesso! {len(files)} tiles fatiados em '{args.output}'.")

    elif args.command == "parallax":
        res = process_parallax_layers(args.layers, args.out, target_height=args.height)
        print(f"Sucesso! Camadas de Parallax processadas em '{args.out}'. Manifesto: {res['config_file']}")

    elif args.command == "items":
        files = process_item_kit(args.input, args.output, target_size=args.size)
        print(f"Sucesso! {len(files)} itens individuais gerados em '{args.output}'.")
        if args.atlas:
            atlas_res = pack_item_atlas(files, args.atlas, item_size=args.size)
            print(f"Atlas gerado em: {atlas_res['atlas_path']} com manifesto JSON: {atlas_res['json_path']}")

    elif args.command == "audit":
        print(f"{'Sprite':<40} | {'Saturação':<10} | {'Brilho':<10}")
        print("-" * 65)
        for p in args.sprites:
            im = Image.open(p)
            prof = extract_palette_profile(im)
            print(f"{p:<40} | {prof['avg_saturation']*100:6.1f}%   | {prof['avg_brightness']*100:6.1f}%")

    elif args.command == "sfx":
        overrides = {}
        if args.volume is not None:
            overrides["volume"] = args.volume
        if args.duration is not None:
            overrides["duration"] = args.duration
        out = SFXGenerator.preset(args.preset, args.output, **overrides)
        print(f"Sucesso! Efeito sonoro procedural '{args.preset}' gerado em: {out}")

    elif args.command == "godot":
        out = GodotExporter.scan_and_export_spriteframes(
            sprite_dir=args.input_dir,
            output_tres_path=args.output_tres,
            anim_name=args.name,
            speed=args.fps,
            loop=args.loop,
            filter_pattern=args.filter
        )
        print(f"Sucesso! Recurso SpriteFrames do Godot 4 gerado em: {out}")


if __name__ == "__main__":
    main()

---
trigger: always_on
description: Regra global mandatoria para criacao de modelos 3D, CAD e conversao de imagens para 3D via MCP blender-3d-cad.
---

# DIRETRIZ GLOBAL DE MODELAGEM 3D E MCP CAD (BLENDER 4.5)

Sempre que o usuario, em qualquer projeto, workspace ou sessao, solicitar:
1. Modelagem de objetos 3D, pecas mecanicas, gabinetes, suportes ou solidos parametricos;
2. Transcricao ou conversao de imagens, fotografias ou blueprints 2D para modelos 3D;
3. Geracao de malhas tridimensionais fechadas (manifold/watertight) para inspecao tecnica ou impressao 3D;

O agente DEVE OBRIGATORIAMENTE acionar as ferramentas do servidor MCP `blender-3d-cad` registrado globalmente, em vez de improvisar scripts locais ou aproximados.

## REGRAS OBRIGATORIAS DE EXECUCAO:

1. **Principio "Shape-First" (Geometria Pura sem Cores Prematuras):**
   - Todo modelo 3D em fase de concepcao deve ser gerado estritamente em material Clay Tecnico Neutro (cinza fosco/acetinado PBR: RGB ~0.76, Roughness ~0.38, Metallic ~0.08).
   - O agente e o MCP NUNCA devem aplicar esquemas de cores, pinturas ou texturas antes da aprovacao morfologica.
   - O foco absoluto e captar formas, silhuetas, proporcoes, curvaturas, quinas e profundidades reais.
   - Somente apos o usuario aprovar explicitamente a geometria, o agente devera perguntar se ha cores ou texturas desejadas.

2. **Padrao Universal de Coordenadas CAD (Z-Up Rigoroso):**
   - **Eixo X (Vermelho):** Comprimento longitudinal (Frente <-> Traseira).
   - **Eixo Y (Verde):** Largura transversal (Esquerda <-> Direita).
   - **Eixo Z (Azul):** Altura vertical (Chao <-> Topo/Teto). O eixo Z aponta sempre para CIMA.

3. **Ferramenta Padrao de Transcricao de Imagens:**
   - Utilizar prioritariamente `transcrever_imagem_3d_adaptativo(caminho_imagem, modo='auto', comprimento_alvo_mm=...)`.
   - O orquestrador decide automaticamente entre TripoSR (GPU com VRAM >= 6GB) e Depth-Anything-V2 (CPU / GPUs leves).

4. **Visualizacao Técnica em Tempo Real:**
   - O Viewport Three.js opera desacoplado em http://127.0.0.1:8088 com Live-Reload automatico via SSE.

---
trigger: always_on
description: Modelo padrão de solicitação e pipeline para rotação de personagens em 180º horizontal com assimetria física 3D real.
---

# DIRETRIZ DE ROTAÇÃO 180º HORIZONTAL DE PERSONAGENS (3D TURNAROUND)

Sempre que for solicitado girar, rotacionar ou criar sprites complementares de um personagem em **180º na horizontal** (olhando para o lado oposto, ex: da direita para a esquerda):

## 1. Princípio Fundamental de Assimetria 3D Real
**NUNCA utilize um simples espelhamento 2D (`flip_h`)**, pois o espelhamento 2D inverte erroneamente os itens de mão (troca a espada para a mão esquerda e o escudo para a mão direita).

A rotação 180º horizontal deve simular uma **câmera girando em torno de um modelo 3D verdadeiro**:
- **Mão Dominante (ex: Espada na mão direita)**: Permanece na mão direita física. Ao olhar para a esquerda, o braço direito fica **ao fundo (afastado da câmera / lado oposto do torso)**.
- **Mão Secundária (ex: Escudo na mão esquerda)**: Permanece na mão esquerda física. Ao olhar para a esquerda, o braço esquerdo fica **em primeiro plano (mais próximo da câmera / frente do corpo)**.
- **Acessórios (ex: Chapéu / Capuz / Capa)**: A ponta e caimento apontam para trás do personagem (em direção oposta à face).
- **Oclusão Física de Profundidade (Depth Occlusion)**: Membros, empunhaduras ou partes de armas localizadas no plano de fundo (lado oposto da câmera) devem ser natural e realisticamente encobertas pela cabeça, gorro, ombros ou torso quando a perspectiva tridimensional ditar. **NUNCA contorcer a anatomia ou rotacionar braços/ombros para tentar forçar a visibilidade total de uma arma ou membro que deveria estar parcialmente ocluído**.
- **Detecção e Mapeamento Cinemático de Juntas (Skeletal Bones & Pose Estimation)**:
  - Antes de qualquer rotação, o agente **DEVE mapear e decompor a pose esquelética do sprite original** em suas juntas articulares (*bones*):
    1. **Coluna e Tronco (*Spine/Core*)**: Identificar a curvatura da coluna (ex: curvada para a frente em compressão de golpe, ereta ou inclinada) e a inclinação do abdômen/quadril.
    2. **Membros Dominantes (*Dominant Arm: Shoulder -> Elbow -> Wrist*)**: Identificar os ângulos individuais de cada junta (ex: braço descendo a ~45º em relação ao solo no final de um arco de corte descendente, enquanto o punho mantém a lâmina horizontal).
    3. **Membros Secundários (*Offhand: Shoulder -> Elbow*)**: Identificar a posição do braço secundário (ex: cotovelo recolhido para trás do torso abrindo a guarda).
    4. **Membros Inferiores (*Pelvis -> Knees -> Feet*)**: Distribuição de peso, largura da base e flexão dos joelhos.
    5. **Vetor e Dinâmica do Golpe**: Distinguir rigorosamente a cinemática da ação (ex: término de corte descendente em arco com o corpo todo *overhead slash* vs estocada frontal reta *thrust*).
  - **Proibição de Espelhamento Falso**: O turnaround 180º deve aplicar essas mesmas rotações articulares no modelo visto pelo lado oposto. **A espada JAMAIS deve passar para o braço em primeiro plano (braço esquerdo) para simular um falso espelho 2D**.
- **Extração e Preservação da Paleta de Cores (Agnóstica de Personagem)**:
  - O agente **DEVE inspecionar e registrar programaticamente a paleta de cores, saturação média, contraste e brilho do sprite original** antes de gerar novos frames.
  - O turnaround gerado deve herdar e manter rigorosamente os mesmos valores tonais, níveis de saturação e contraste do original, proibindo variações lavadas, escuras ou dessaturadas.

---

## 2. Template Padrão de Prompt Generativo (Turnaround 180° Universal)

```
Using the attached image as a strict visual reference for the character design, colors, and pixel density, generate the exact same character performing {ACTION_AND_SKELETAL_POSE_DESCRIPTION}, rotated 180 degrees horizontally, viewing them from the opposite side (facing {FACING_DIRECTION}). Maintain the exact skeletal joint angles and spine curvature of the reference: {SPINE_AND_LIMB_KINEMATICS}. Ensure their asymmetric details (dominant hand weapon remains in its physical hand on the far/background side; offhand shield/item remains in its physical hand on the near/foreground side) are physically accurate to a real 3D turnaround without 2D flipping. Respect natural 3D depth occlusion: if weapons, limbs, or equipment pass behind the head, shoulders, or body, let them be naturally and partially occluded instead of unnaturally twisting the character's pose to force full visibility. Maintain the exact retro pixel art style, adhering strictly to the identical color palette, contrast, and rich saturation of the reference without color shifts or washouts, with a clean pixel grid and solid black background for clean extraction.
```

---

## 3. Pipeline Universal de Processamento e Alinhamento no Canvas

1. **Mapeamento Cinemático dos Bones e Pose Original**:
   - Analisar o esqueleto articular original: curvatura da espinha/costas, compressão do abdômen, ângulo do braço no ombro e cotovelo, orientação do punho e postura das pernas.
2. **Inspeção e Extração da Paleta Original**:
   - Analisar o sprite original e registrar suas métricas colorimétricas de referência (amostras de cores dominantes, saturação HSV média e brilho) para conferência e harmonização posterior.
3. **Medição Biométrica Original**:
   - Obter a altura exata da bounding box do frame original correspondente ($H_{orig} = bbox_{orig}[3] - bbox_{orig}[1]$).
4. **Geração**: Executar `generate_image` com a referência do frame e o template acima detalhando a cinemática das juntas.
5. **Isolamento de Alfa**: Remover o fundo preto puro.
6. **Calibração Rígida de Altura com o Original**:
   - O sprite recortado do turnaround **DEVE ser escalado para ter EXATAMENTE a mesma altura $H_{orig}$**, garantindo consistência biométrica absoluta e zero flutuação de escala durante os ciclos de animação.
7. **PixelForge MCP / Downscale**: Processar com amostragem limpa e nítida de pixel art sem blur bilinear.
8. **Validação Anatômica e de Cores**:
   - Verificar se a espada não foi colocada no braço dianteiro e se a curvatura da coluna e o ângulo do braço correspondem fielmente à pose mapeada no Passo 1.
   - Comparar as métricas HSV do novo frame com a paleta registrada no Passo 2.
9. **Alinhamento no Canvas**: Posicionar o sprite no canvas padrão do jogo alinhando a base dos pés rigorosamente com a linha de solo do sprite original ($Y = Y_{solo}$ e $Y_{topo} = Y_{solo} - H_{orig}$).
10. **Destino**: Salvar na pasta de sprites invertidos sem alterar os scripts do jogo ativo até aprovação final.



# 🎮 Antigravity GameDev Ecosystem Pack

Pacote unificado de portabilidade de ambiente, regras de IA, competências e ferramentas para desenvolvimento de jogos no **Antigravity IDE**.

Este pacote permite replicar **com 1 único comando** em qualquer outro computador (Windows) a exata mesma configuração mental, ferramentas e comportamento de inteligência artificial da sua máquina principal.

---

## 📦 1. O Que Está Incluído no Pacote

### 🧠 A. Regras Globais de Comportamento da IA (`rules/`)
- **`turnaround_180_prompt_template.md`**: Diretriz técnica e matemática para giro horizontal de 180° com assimetria 3D real (preserva mão dominante da arma no plano de fundo, oclusão física de profundidade, decomposição cinemática de juntas/ossos e preservação da paleta de cores original HSV sem espelhamento 2D falso).
- **`agent_orchestration.md`**: Protocolo de roteamento e triagem de tarefas (Gemini Pro como arquiteto/lógica, Claude como programador sênior de UI/gameplay, e geradores visuais para assets).
- **`mcp_3d_modeling.md`**: Diretriz global para CAD 3D paramétrico no Blender 4.5, sistema universal Z-Up e materiais Clay Técnico Neutro PBR.
- **`architecture_check.md`**: Validação de integridade e padrões de projeto.

### 🛠️ B. Suíte Completa de Ferramentas de GameDev (`toolkit/`)
Totalmente nativa, sem dependência de APIs externas de terceiros:
1. **`pixel_tools/`**:
   - `sprite_splitter.py`: Extração alfa, corte de caixas e alinhamento biométrico ($H_{orig}$ e solo $Y=96$).
   - `tileset_processor.py`: Fatiamento em grade, teste de repetição contínua (*seamless wrap score*) e margens anti-bleeding.
   - `parallax_processor.py`: Blending alfa nas extremidades horizontais para looping infinito e manifesto para o Godot.
   - `item_kit_processor.py`: Detecção de ícones, centralização em células quadradas e geração de Atlas combinada com JSON.
   - `color_calibrator.py`: Leitura e equalização de perfis colorimétricos (matiz, saturação e brilho).
2. **`audio_tools/`**:
   - `sfx_synthesizer.py`: Sintetizador procedural de efeitos sonoros retro (onda senoidal, quadrada, triangular, dente-de-serra e ruído) com envelopes ADSR, sweeps de frequência e bitcrush. Presets: `jump`, `laser`, `explosion`, `hit`, `coin`, `powerup`, `slash`, `step`.
3. **`godot_tools/`**:
   - `godot_exporter.py`: Compilador nativo de sequências de sprites em recursos `.tres` do Godot 4 (`SpriteFrames`) com IDs, UIDs e controle de loop/FPS.

### 🔌 C. Configuração dos Servidores MCP (`mcp_config.template.json`)
- Integração pré-configurada para `blender-3d-cad`, `unreal-mcp`, `ferramentas-dev-lyra`, `pixelforge` e `game-asset-generator`.

---

## 🚀 2. Como Instalar em Outra Máquina

### Passo 1: Copiar a pasta
Copie a pasta `antigravity-gamedev-pack` para a nova máquina (via pendrive, rede local ou compactado em `.zip`).

### Passo 2: Executar o Instalador Automático
Abra o **PowerShell** na pasta do pacote e execute:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

O instalador irá:
1. Identificar o seu usuário atual e criar as pastas de configuração do Antigravity (`~/.gemini/config/`).
2. Instalar as regras em `~/.gemini/config/rules/`.
3. Instalar as skills em `~/.gemini/config/skills/`.
4. Copiar o toolkit para `~/.gemini/config/toolkit/`.
5. Mesclar o `mcp_config.json` adaptando os caminhos para o usuário atual da máquina.
6. Instalar as dependências do Python (`Pillow`, `numpy`).

---

## 💻 3. Como Usar o Toolkit na Nova Máquina

O toolkit pode ser invocado via linha de comando ou diretamente pelos agentes do Antigravity:

```bash
# Ver todos os comandos disponíveis:
python ~/.gemini/config/toolkit/gamedev_toolkit.py --help

# 1. Fatiar e calibrar altura de spritesheet:
python ~/.gemini/config/toolkit/gamedev_toolkit.py split spritesheet.png output_dir/ --target-height 49 --ground 96

# 2. Gerar efeito sonoro de pulo (jump) ou moeda (coin):
python ~/.gemini/config/toolkit/gamedev_toolkit.py sfx jump audio/pulo.wav
python ~/.gemini/config/toolkit/gamedev_toolkit.py sfx coin audio/moeda.wav

# 3. Compilar pasta de sprites em SpriteFrames do Godot 4:
python ~/.gemini/config/toolkit/gamedev_toolkit.py godot sprites/hero_w/ hero_w.tres --name "attack_normal_w" --fps 10.0

# 4. Fatiar tileset em blocos 16x16:
python ~/.gemini/config/toolkit/gamedev_toolkit.py tileset tileset.png tiles/ --size 16

# 5. Processar camadas de Parallax para loop infinito:
python ~/.gemini/config/toolkit/gamedev_toolkit.py parallax bg_ceu.png bg_montanhas.png bg_chao.png --out parallax/
```

---

## 🔒 4. Garantia de Consistência
Qualquer agente Antigravity executado nesta nova máquina lerá automaticamente as mesmas regras de orquestração e templates de prompt, garantindo que o fluxo de turnaround 180°, proporções biométricas de pixel art e padrões de código sejam mantidos rigorosamente idênticos.

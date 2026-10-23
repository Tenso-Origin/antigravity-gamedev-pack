# ==============================================================================
# Antigravity GameDev Ecosystem - Script de Instalação e Portabilidade
# Configura o mesmo ambiente de desenvolvimento e regras de IA em qualquer máquina.
# ==============================================================================

param(
    [switch]$SkipVenv = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "   INSTALADOR DO ECOSSISTEMA ANTIGRAVITY GAMEDEV (PORTÁTIL)      " -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$UserDir = $env:USERPROFILE
$GeminiConfigDir = Join-Path $UserDir ".gemini\config"
$TargetRulesDir = Join-Path $GeminiConfigDir "rules"
$TargetSkillsDir = Join-Path $GeminiConfigDir "skills"
$TargetToolkitDir = Join-Path $GeminiConfigDir "toolkit"
$TargetMcpConfigFile = Join-Path $GeminiConfigDir "mcp_config.json"

Write-Host "[1/5] Verificando estrutura de diretórios do Antigravity..." -ForegroundColor White
$Directories = @($GeminiConfigDir, $TargetRulesDir, $TargetSkillsDir, $TargetToolkitDir)
foreach ($Dir in $Directories) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Force -Path $Dir | Out-Null
        Write-Host "      + Criado: $Dir" -ForegroundColor Gray
    }
}
Write-Host "      [OK] Pastas base configuradas." -ForegroundColor Green

Write-Host "`n[2/5] Sincronizando Regras Globais de IA (Rules)..." -ForegroundColor White
$SourceRules = Join-Path $CurrentDir "rules"
if (Test-Path $SourceRules) {
    Copy-Item -Path "$SourceRules\*" -Destination $TargetRulesDir -Recurse -Force
    $CopiedRules = (Get-ChildItem $TargetRulesDir).Count
    Write-Host "      [OK] $CopiedRules diretrizes e regras instaladas em $TargetRulesDir" -ForegroundColor Green
} else {
    Write-Host "      [AVISO] Pasta 'rules' não encontrada no pacote." -ForegroundColor Yellow
}

Write-Host "`n[3/5] Sincronizando Competências e Customizações (Skills)..." -ForegroundColor White
$SourceSkills = Join-Path $CurrentDir "skills"
if (Test-Path $SourceSkills) {
    Copy-Item -Path "$SourceSkills\*" -Destination $TargetSkillsDir -Recurse -Force
    $CopiedSkills = (Get-ChildItem $TargetSkillsDir).Count
    Write-Host "      [OK] $CopiedSkills skills sincronizadas em $TargetSkillsDir" -ForegroundColor Green
} else {
    Write-Host "      [AVISO] Pasta 'skills' não encontrada no pacote." -ForegroundColor Yellow
}

Write-Host "`n[4/5] Instalando Suíte de Engenharia de Jogos (Toolkit)..." -ForegroundColor White
$SourceToolkit = Join-Path $CurrentDir "toolkit"
if (Test-Path $SourceToolkit) {
    Copy-Item -Path "$SourceToolkit\*" -Destination $TargetToolkitDir -Recurse -Force
    Write-Host "      [OK] Módulos de Pixel Art, Áudio e Godot instalados em $TargetToolkitDir" -ForegroundColor Green
} else {
    Write-Host "      [AVISO] Pasta 'toolkit' não encontrada no pacote." -ForegroundColor Yellow
}

Write-Host "`n[5/5] Configurando Servidores MCP e Dependências Python..." -ForegroundColor White
$NormalizedUserDir = $UserDir.Replace("\", "/")
$McpTemplateFile = Join-Path $CurrentDir "mcp_config.template.json"

if (Test-Path $McpTemplateFile) {
    $TemplateContent = Get-Content -Raw -Path $McpTemplateFile -Encoding UTF8
    $ProcessedContent = $TemplateContent.Replace("{{USERPROFILE}}", $NormalizedUserDir)

    if (Test-Path $TargetMcpConfigFile) {
        try {
            $ExistingJson = Get-Content -Raw -Path $TargetMcpConfigFile -Encoding UTF8 | ConvertFrom-Json
            $NewJson = $ProcessedContent | ConvertFrom-Json

            if (-not $ExistingJson.mcpServers) {
                $ExistingJson | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue (New-Object PSObject)
            }

            foreach ($prop in $NewJson.mcpServers.PSObject.Properties) {
                if (-not $ExistingJson.mcpServers.PSObject.Properties[$prop.Name]) {
                    $ExistingJson.mcpServers | Add-Member -NotePropertyName $prop.Name -NotePropertyValue $prop.Value
                    Write-Host "      + Servidor MCP adicionado: $($prop.Name)" -ForegroundColor Gray
                }
            }

            $ExistingJson | ConvertTo-Json -Depth 10 | Set-Content -Path $TargetMcpConfigFile -Encoding UTF8
            Write-Host "      [OK] mcp_config.json mesclado com sucesso." -ForegroundColor Green
        } catch {
            Write-Host "      [AVISO] Erro ao mesclar JSON existente. Preservando backup e gravando novo." -ForegroundColor Yellow
            Copy-Item -Path $TargetMcpConfigFile -Destination "$TargetMcpConfigFile.bak" -Force
            Set-Content -Path $TargetMcpConfigFile -Value $ProcessedContent -Encoding UTF8
        }
    } else {
        Set-Content -Path $TargetMcpConfigFile -Value $ProcessedContent -Encoding UTF8
        Write-Host "      [OK] mcp_config.json criado com sucesso." -ForegroundColor Green
    }
}

# Configuração opcional do Venv para dependências de imagem (Pillow/Numpy)
if (-not $SkipVenv) {
    $ReqFile = Join-Path $CurrentDir "requirements.txt"
    $PythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
    if ($PythonCmd) {
        Write-Host "`nInstalando bibliotecas do toolkit (Pillow / NumPy)..." -ForegroundColor White
        try {
            & python -m pip install -r $ReqFile --quiet
            Write-Host "      [OK] Dependências do Python instaladas com sucesso." -ForegroundColor Green
        } catch {
            Write-Host "      [AVISO] Não foi possível rodar o pip automaticamente. Execute manualmente: pip install -r requirements.txt" -ForegroundColor Yellow
        }
    } else {
        Write-Host "      [INFO] Python não encontrado no PATH global. Instale o Python para usar o CLI do toolkit." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "   INSTALAÇÃO CONCLUÍDA COM SUCESSO!                             " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "O seu Antigravity IDE nesta máquina agora possui exatamente as" -ForegroundColor White
Write-Host "mesmas regras, diretrizes de rotação 3D, agentes e toolkit que" -ForegroundColor White
Write-Host "a sua máquina de desenvolvimento original." -ForegroundColor White
Write-Host ""
Write-Host "Comandos disponíveis:" -ForegroundColor Yellow
Write-Host "  python $TargetToolkitDir\gamedev_toolkit.py --help" -ForegroundColor Gray
Write-Host ""

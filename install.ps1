<#
.SYNOPSIS
Instalacao global OPCIONAL do Maestro em Codex para VS Code (Windows).
.DESCRIPTION
No proprio repositorio, basta abrir a pasta no VS Code. -Global copia skills para ~/.agents/skills e
subagentes para ~/.codex/agents. Nao sobrescreve arquivos existentes sem -Force, nem altera config.toml.
.EXAMPLE
.\install.ps1 -Global
#>
param(
    [switch]$Global,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'

if (-not $Global) {
    Write-Host 'Para usar neste projeto: abra a pasta no VS Code e use o Codex; nao precisa instalar.'
    Write-Host 'Para instalar globalmente: .\install.ps1 -Global'
    Write-Host 'Para substituir arquivos Maestro existentes: .\install.ps1 -Global -Force'
    return
}

$userHome = [Environment]::GetFolderPath('UserProfile')
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $userHome '.codex' }
$skillsTarget = Join-Path $userHome '.agents\skills'
$agentsTarget = Join-Path $codexHome 'agents'
$toolkitTarget = Join-Path $codexHome 'maestro'
New-Item -ItemType Directory -Force -Path $skillsTarget, $agentsTarget, $toolkitTarget | Out-Null

function Copy-ItemSafe {
    param([string]$Source, [string]$Target)
    if (Test-Path -LiteralPath $Target) {
        if (-not $Force) {
            Write-Host "[PULADO] Ja existe: $Target (use -Force se desejar substituir)" -ForegroundColor Yellow
            return
        }
        Remove-Item -LiteralPath $Target -Recurse -Force
    }
    Copy-Item -LiteralPath $Source -Destination $Target -Recurse -Force
    Write-Host "[OK] $Target" -ForegroundColor Green
}

Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot '.agents\skills') -Directory | ForEach-Object {
    if (Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md')) {
        Copy-ItemSafe -Source $_.FullName -Target (Join-Path $skillsTarget $_.Name)
    }
}
Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot '.codex\agents') -Filter '*.toml' -File | ForEach-Object {
    Copy-ItemSafe -Source $_.FullName -Target (Join-Path $agentsTarget $_.Name)
}

$resources = @(
    @{ source = 'templates'; target = 'templates' },
    @{ source = 'scripts'; target = 'scripts' },
    @{ source = '.agents\orchestrator'; target = 'orchestrator' },
    @{ source = '.agents\workflows'; target = 'workflows' },
    @{ source = '.agents\subagents'; target = 'subagents' },
    @{ source = '.agents\skills'; target = 'skills' }
)
foreach ($item in $resources) {
    $source = Join-Path $PSScriptRoot $item.source
    if (Test-Path -LiteralPath $source) {
        Copy-ItemSafe -Source $source -Target (Join-Path $toolkitTarget $item.target)
    }
}

New-Item -ItemType Directory -Force -Path (Join-Path $toolkitTarget '.agents') | Out-Null
Copy-ItemSafe -Source (Join-Path $PSScriptRoot '.agents\knowledge') -Target (Join-Path $toolkitTarget '.agents\knowledge')

Write-Host 'Instalacao global finalizada. Nem AGENTS.md pessoal nem config.toml foram alterados.' -ForegroundColor Cyan
Write-Host 'Reabra o chat do Codex e utilize $maestro.' -ForegroundColor Cyan

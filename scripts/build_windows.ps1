$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Building AMS2 AI Creator for Windows..."

pyinstaller --noconfirm AMS2-AI-Creator.spec

Write-Host "Build complete: dist/AMS2-AI-Creator/"

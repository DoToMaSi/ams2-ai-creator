$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Building AMS2 AI Creator for Windows..."
Write-Host ""
Write-Host "Generating multi-size application icon..."
python scripts/build_icon.py

pyinstaller --noconfirm AMS2-AI-Creator.spec

Write-Host "Build complete: dist/AMS2-AI-Creator/"

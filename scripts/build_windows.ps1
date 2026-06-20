$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Building AMS2 AI Creator for Windows..."
Write-Host ""
Write-Host "Generating Windows-compatible application icon..."
python scripts/build_icon.py

pyinstaller --noconfirm AMS2-AI-Creator.spec

Write-Host "Applying icon to executable..."
python scripts/build_icon.py --apply-exe

Write-Host "Build complete: dist/AMS2-AI-Creator/"
Write-Host "If Explorer still shows the old icon, rename the .exe or restart Explorer."

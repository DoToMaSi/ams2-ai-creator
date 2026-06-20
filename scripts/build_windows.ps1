$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Building AMS2 AI Creator for Windows..."

pyinstaller `
  --name AMS2-AI-Creator `
  --windowed `
  --onedir `
  --noconfirm `
  --add-data "ams2_ai/data;ams2_ai/data" `
  main.py

Write-Host "Build complete: dist/AMS2-AI-Creator/"

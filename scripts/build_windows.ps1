$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Building AMS2 AI Creator for Windows..."
Write-Host ""
Write-Host "Generating Windows-compatible application icon..."
python scripts/build_icon.py

pyinstaller --noconfirm --clean AMS2-AI-Creator.spec

Write-Host "Creating release archive..."
if (Test-Path "dist/AMS2-AI-Creator-windows.zip") {
    Remove-Item "dist/AMS2-AI-Creator-windows.zip" -Force
}
Compress-Archive -Path "dist/AMS2-AI-Creator" -DestinationPath "dist/AMS2-AI-Creator-windows.zip"

Write-Host "Build complete: dist/AMS2-AI-Creator/"
Write-Host "Archive: dist/AMS2-AI-Creator-windows.zip"

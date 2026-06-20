$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Building AMS2 Creator for Windows..."
Write-Host ""
Write-Host "Generating Windows-compatible application icon..."
python scripts/build_icon.py

pyinstaller --noconfirm --clean AMS2-Creator.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path "dist/AMS2-Creator")) {
    throw "Expected output directory not found: dist/AMS2-Creator"
}

Write-Host "Creating release archive..."
if (Test-Path "dist/AMS2-Creator-windows.zip") {
    Remove-Item "dist/AMS2-Creator-windows.zip" -Force
}
Compress-Archive -Path "dist/AMS2-Creator" -DestinationPath "dist/AMS2-Creator-windows.zip"

Write-Host "Build complete: dist/AMS2-Creator/"
Write-Host "Archive: dist/AMS2-Creator-windows.zip"

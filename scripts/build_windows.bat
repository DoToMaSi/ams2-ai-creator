@echo off
setlocal

cd /d "%~dp0\.."

echo Building AMS2 AI Creator for Windows...
echo.

python -m PyInstaller --noconfirm AMS2-AI-Creator.spec

if errorlevel 1 (
  echo.
  echo Build failed.
  exit /b 1
)

echo.
echo Build complete: dist\AMS2-AI-Creator\
echo Run: dist\AMS2-AI-Creator\AMS2-AI-Creator.exe
endlocal

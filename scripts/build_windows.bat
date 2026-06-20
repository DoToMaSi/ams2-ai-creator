@echo off
setlocal

cd /d "%~dp0\.."

echo Building AMS2 AI Creator for Windows...
echo.

python -m PyInstaller ^
  --name AMS2-AI-Creator ^
  --windowed ^
  --onedir ^
  --noconfirm ^
  --add-data "ams2_ai/data;ams2_ai/data" ^
  main.py

if errorlevel 1 (
  echo.
  echo Build failed.
  exit /b 1
)

echo.
echo Build complete: dist\AMS2-AI-Creator\
echo Run: dist\AMS2-AI-Creator\AMS2-AI-Creator.exe
endlocal

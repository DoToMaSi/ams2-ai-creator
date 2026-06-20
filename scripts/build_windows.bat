@echo off
setlocal

cd /d "%~dp0\.."

echo Building AMS2 AI Creator for Windows...
echo.

echo Generating Windows-compatible application icon...
python scripts\build_icon.py
if errorlevel 1 (
  echo.
  echo Icon generation failed.
  exit /b 1
)

python -m PyInstaller --noconfirm AMS2-AI-Creator.spec
if errorlevel 1 (
  echo.
  echo Build failed.
  exit /b 1
)

echo Applying icon to executable...
python scripts\build_icon.py --apply-exe
if errorlevel 1 (
  echo.
  echo Failed to apply icon to executable.
  exit /b 1
)

echo.
echo Build complete: dist\AMS2-AI-Creator\
echo Run: dist\AMS2-AI-Creator\AMS2-AI-Creator.exe
echo If Explorer still shows the old icon, rename the .exe or restart Explorer.
endlocal

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

python -m PyInstaller --noconfirm --clean AMS2-AI-Creator.spec
if errorlevel 1 (
  echo.
  echo Build failed.
  exit /b 1
)

echo Creating release archive...
powershell -NoProfile -Command "Compress-Archive -Path 'dist\AMS2-AI-Creator' -DestinationPath 'dist\AMS2-AI-Creator-windows.zip' -Force"
if errorlevel 1 (
  echo.
  echo Failed to create zip archive.
  exit /b 1
)

echo.
echo Build complete: dist\AMS2-AI-Creator\
echo Archive: dist\AMS2-AI-Creator-windows.zip
echo Run: dist\AMS2-AI-Creator\AMS2-AI-Creator.exe
endlocal

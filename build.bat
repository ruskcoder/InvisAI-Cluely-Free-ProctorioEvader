@echo off
echo Building InvisAI executable...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

pyinstaller main.spec

echo.
if exist "dist\InvisAI.exe" (
    echo Build completed successfully!
    echo Executable created at: dist\InvisAI.exe
    echo.
    echo You can now run the executable without Python installed.
) else (
    echo Build failed! Check the output above for errors.
)

pause

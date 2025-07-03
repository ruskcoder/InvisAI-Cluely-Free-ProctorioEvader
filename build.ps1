Write-Host "Building InvisAI executable..." -ForegroundColor Green
Write-Host ""

# Clean previous builds
if (Test-Path "dist") {
    Write-Host "Removing previous dist directory..." -ForegroundColor Yellow
    Remove-Item -Path "dist" -Recurse -Force
}

if (Test-Path "build") {
    Write-Host "Removing previous build directory..." -ForegroundColor Yellow
    Remove-Item -Path "build" -Recurse -Force
}

Write-Host "Running PyInstaller..." -ForegroundColor Cyan
pyinstaller main.spec

Write-Host ""
if (Test-Path "dist\InvisAI.exe") {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Executable created at: dist\InvisAI.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the executable without Python installed." -ForegroundColor Green
} else {
    Write-Host "Build failed! Check the output above for errors." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

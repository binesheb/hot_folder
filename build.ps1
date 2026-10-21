$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv\\Scripts\\python.exe")) {
    Write-Error "Virtual environment not found. Create it and install requirements.txt first."
}

$Python = Resolve-Path ".venv\\Scripts\\python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed; refusing to package." }

& $Python -m PyInstaller --noconfirm --clean --windowed --name HotFolder main.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

Write-Host "Build complete: dist\\HotFolder\\HotFolder.exe"
Write-Host "Note: install SumatraPDF and a compatible printer driver on the target PC."

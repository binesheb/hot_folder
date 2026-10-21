$ErrorActionPreference = "Stop"

# Prefer the developer's virtual environment; use the active Python on CI/clean build agents.
$Python = "python"
if (Test-Path ".venv\Scripts\python.exe") {
    $Python = (Resolve-Path ".venv\Scripts\python.exe").Path
}

& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
& $Python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
& $Python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed; refusing to package." }

& $Python -m PyInstaller --noconfirm --clean --windowed --name HotFolder main.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

Write-Host "Build complete: dist\HotFolder\HotFolder.exe"
Write-Host "Note: install SumatraPDF and a compatible printer driver on the target PC."

# create_venv.ps1
# Creates a virtual environment named .venv in the current folder

python -m venv .venv -ArgumentList '--clear'
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create venv. Ensure 'python' is on PATH and points to Python 3."
} else {
    Write-Host "Virtual environment '.venv' created. To activate, run:\n  .\\.venv\\Scripts\\Activate.ps1"
}

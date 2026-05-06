Steps to create and activate the virtual environment (.venv)

Windows PowerShell (recommended):

```powershell
# create venv (runs the provided script)
.\create_venv.ps1

# activate
.\.venv\Scripts\Activate.ps1

# install required packages
pip install -r requirements.txt
```

Windows (cmd.exe):

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

Unix / WSL / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Notes:
- If you don't have a `requirements.txt` yet, create one with the libraries you need (e.g. `sentence-transformers`, `numpy`, `faiss-cpu` (if supported), `sqlite3` is built-in).
- If `python` isn't on PATH, use `py -3` on Windows or the full Python executable path.

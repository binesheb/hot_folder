# Hot Folder

A small Windows desktop utility concept for automatically printing files that appear in a selected folder.

## Current status

This repository contains a 2023 PyQt5 prototype. It is not yet release-ready: the current implementation needs a non-blocking folder watcher, safe handling for partially copied files, printer selection/error reporting, and packaging before unattended use.

## Architecture

- **PyQt5** provides the desktop interface.
- **Windows Shell printing** is used to hand a new file to its registered application/printer.
- The selected folder is intended to be watched for newly added files.

## Running the prototype

The source currently lives in `source_code` and should be treated as experimental. A dependency manifest is provided so the prototype can be installed reproducibly without relying on undeclared packages:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The current monitoring loop runs on the UI thread and the checked-in file is incomplete, so do not rely on this prototype for unattended printing yet.

## Updates

### Automatic updates

Automatic self-updating is **not enabled** yet. If a future packaged Windows release adds an update checker, its automatic update source must be the repository's GitHub **`main` branch only**. It must not pull from feature/development branches, must validate the candidate build before replacement, and should require user confirmation before installing because printer automation can affect physical output.

### Manual update

For a Git checkout, update only from `origin/main`:

```bash
git switch main
git fetch origin main --prune
git pull --ff-only origin main
python -m pip install -r requirements.txt
```

To stay on a known revision:

```bash
git checkout <commit>
```

To roll back, check out a previously known-good commit.

## Dependency policy

`requirements.txt` is the source of truth for the prototype's Python dependencies. Dependencies should remain on maintained release lines; deprecated or unmaintained packages must be replaced with compatible supported alternatives and validated before release.

## Versioning and releases

The project follows Semantic Versioning once runnable releases exist:

- **MAJOR** — incompatible workflow or architecture changes.
- **MINOR** — backwards-compatible features.
- **PATCH** — bug fixes, safety fixes, and documentation/maintenance changes.

See `CHANGELOG.md` for release notes.

## Next steps

1. Finish and validate the monitoring loop without blocking the GUI.
2. Wait for files to become stable before printing.
3. Add printer selection, status reporting, and retry/error handling.
4. Rename `source_code` to a normal Python entry point and add a Windows packaging workflow.
5. Add tests for file detection and print-job state handling before enabling an update checker.

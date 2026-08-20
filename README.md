# Hot Folder

A small Windows desktop utility concept for automatically printing files that appear in a selected folder.

## Current status

This repository contains a 2023 PyQt5 prototype. It is not yet release-ready: the current implementation needs a non-blocking folder watcher, safe handling for partially copied files, printer selection/error reporting, and packaging before unattended use.

## Architecture

- **PyQt5** provides the desktop interface.
- **Windows Shell printing** is used to hand a new file to its registered application/printer.
- The selected folder is intended to be watched for newly added files.

## Running the prototype

The source currently lives in `source_code` and should be treated as experimental. A future cleanup should rename it to a normal Python entry point and add a dependency manifest.

Typical dependencies are:

```text
PyQt5
pywin32
```

Because the current monitoring loop runs on the UI thread and the checked-in file is incomplete, do not rely on this prototype for unattended printing yet.

## Updates

### Automatic updates

Automatic self-updating is **not enabled** yet. A future packaged Windows release should check GitHub Releases for a newer signed/versioned build, show the release notes, and require user confirmation before installing.

### Manual update

For a Git checkout:

```bash
git fetch --tags --prune
git pull --ff-only
```

To stay on a known revision:

```bash
git checkout <tag-or-commit>
```

To roll back, check out a previously known-good tag or commit.

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
4. Add `requirements.txt` or `pyproject.toml` and a Windows packaging workflow.
5. Add tests for file detection and print-job state handling before enabling an update checker.

# Changelog

Notable changes are documented here. Dates use ISO 8601.

## Unreleased
- Archive successfully submitted PDFs under the watched root's `Completed/` folder while preserving the original relative directory structure.
- Exclude the archive from input scanning and avoid overwriting archived files on name collisions.

- Defined the Windows EXE-first product direction and later Windows Service/control-app architecture.
- Added product requirements, architecture, roadmap, testing checklist, and example configuration.
- Added a desktop MVP with rule parsing, recursive polling, a stable-file gate, Windows printer enumeration, and PDF submission via SumatraPDF.
- Added initial unit tests and a Windows PyInstaller build script.
- Documented that command submission does not confirm physical print completion and that persistent restart-safe job tracking remains future work.

## 0.1.0 — Prototype baseline

- Initial PyQt5 hot-folder concept with basic polling and shell-print handoff.

# Hot Folder

**Windows hot-folder printing for rule-based document output.**

Hot Folder watches a configured root directory and its subfolders. When a supported document arrives in a rule folder such as `A4_Simplex`, `A4_Duplex`, or `A5-Duplex`, the app waits until the file is stable and submits it to the configured Windows printer with the folder's paper-size and duplex rules.

Repository: https://github.com/binesheb/hot_folder

## Project status

The project is in active development. The initial delivery target is a **Windows desktop EXE**. The design separates folder monitoring, print rules, job state, and printer execution so a later Windows Service and a separate service-control application can reuse the core engine.

**Do not use unattended production printing until the acceptance checklist in [TESTING.md](TESTING.md) passes on the target printer.** The GitHub source is not itself a signed, tested release binary.

## Initial scope

- Select one root folder; monitor configured rule subfolders recursively.
- Recognize names such as `A4_Simplex`, `A4_Duplex`, `A5-Duplex` (case-insensitive; underscore and hyphen accepted).
- Configure a designated Windows printer.
- Start/stop monitoring and show job status in a desktop window.
- Wait for copied files to stop changing before submitting them.
- Avoid duplicate submission during one app run; log outcomes and errors.
- After a successful renderer submission, move the source file to `Completed/`, preserving its rule-folder and nested folder structure. Failed jobs remain in the input folder.
- Never scan the `Completed/` archive as input. Existing archive files are not overwritten; collisions receive a numbered filename.
- Initial print adapter targets PDF files using SumatraPDF's command-line interface. Other formats require a tested adapter; they are not silently sent through an unpredictable file association.
- Package as a Windows EXE using PyInstaller.

## Folder convention

```text
D:\\PrintQueue\\
  A4_Simplex\\
    invoice-001.pdf
  A4_Duplex\\
    report-002.pdf
  A5-Duplex\\
    label-003.pdf
```

Rule syntax: `<PAPER>_<SIDEDNESS>` or `<PAPER>-<SIDEDNESS>`. Initial paper sizes: A4, A5. Initial sidedness: Simplex, Duplex. For duplex, printer driver defaults determine edge binding unless a supported explicit setting is added. Unknown folders are ignored.

## Development setup (Windows)

1. Install Python 3.11 or 3.12 (64-bit) and a working Windows printer driver.
2. Install SumatraPDF and note the full path to `SumatraPDF.exe`.
3. Clone the repository and open PowerShell in its root.
4. Create a virtual environment and install dependencies:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. Run the desktop app: `python main.py`.
6. Configure the root, printer, and SumatraPDF executable in the app. Use a test printer or harmless test pages first.

## Build the EXE

Run on Windows, not Linux/macOS:

```powershell
.\.venv\Scripts\Activate.ps1
.\build.ps1
```

The output is placed under `dist\\HotFolder\\` (one-folder distribution). The build script deliberately starts with a folder distribution because it is easier to diagnose missing printer/PDF dependencies. A single-file EXE can be considered after acceptance testing.

## Documentation

- [PRD.md](PRD.md) — requirements and acceptance criteria
- [ARCHITECTURE.md](ARCHITECTURE.md) — desktop-to-service migration boundary
- [TESTING.md](TESTING.md) — automated and manual checks
- [ROADMAP.md](ROADMAP.md) — delivery stages
- [config.example.json](config.example.json) — example settings
- [CHANGELOG.md](CHANGELOG.md) — change history
- [UPDATE.md](UPDATE.md) — update and rollback notes

## Configuration and operations

Configuration is stored in `%LOCALAPPDATA%\\HotFolder\\config.json`; logs are written to `%LOCALAPPDATA%\\HotFolder\\hotfolder.log`. The app starts stopped and never deletes source files.

A successful renderer command means **submitted to the Windows print pipeline**, not proof that paper physically came out. Printer names and paper/duplex behavior vary by driver, so verify the actual output on every target printer. Network shares require appropriate access for the interactive user and, later, the Windows service identity.

Automatic updates are not enabled. Release updates must be reviewed, versioned, and sourced from `main`/tagged releases only.

## License

No license has been declared yet. Do not assume the code is open-source licensed until a LICENSE file is added.

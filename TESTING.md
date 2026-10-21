# Testing and release checklist

## Automated tests

Run on any development machine:

```powershell
python -m unittest discover -s tests -v
```

The unit tests cover folder-name parsing and nearest-rule resolution without needing a printer.

## Windows manual tests

Use a harmless test PDF and a test printer or print queue that is safe to exercise.

1. Start app with a valid root; verify it starts stopped.
2. Choose a valid printer and SumatraPDF path; start monitoring.
3. Copy a PDF into `A4_Simplex`; verify it waits until the copy is stable and submits once.
4. Repeat for `A4_Duplex` and `A5-Duplex`; verify actual paper and sidedness.
5. Copy a large PDF slowly; ensure no partial document is submitted.
6. Copy a TXT/PNG/DOCX file; verify it is skipped and logged in the PDF-only MVP.
7. Put a PDF in an unrecognized folder; verify it is not printed.
8. Temporarily disconnect/rename the root; verify a visible error and recovery after restoration.
9. Configure an invalid renderer/printer; verify a clear error without crashing.
10. Stop monitoring while files are pending; verify no new submission after stop.
11. Restart app and observe duplicate behavior. Until a persistent ledger is implemented, restart-safe exactly-once behavior is not guaranteed.
12. Test a network share using the actual user identity intended for deployment.

## Build check (Windows)

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
.\build.ps1
```

Check `dist\\HotFolder\\` on a clean Windows machine with printer driver and SumatraPDF installed. Verify logs and configuration paths are writable without administrator rights.

## Release checklist

- [ ] Automated tests pass.
- [ ] Build succeeds on supported Windows/Python versions.
- [ ] EXE starts on a clean machine.
- [ ] Printer selection works with the target model.
- [ ] Real A4/A5 and simplex/duplex output verified.
- [ ] Copy-in-progress and network interruption tested.
- [ ] Logs avoid document contents and secrets.
- [ ] Version, changelog, release notes, and rollback steps included.
- [ ] Binary is scanned and signed before enterprise distribution.

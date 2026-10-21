# Product Requirements Document — Hot Folder

- **Product:** Hot Folder
- **Repository:** `binesheb/hot_folder`
- **Document status:** Initial product baseline
- **Target platform:** Windows 10/11, 64-bit (verify supported OS versions during release testing)
- **Initial delivery:** Desktop EXE; later Windows Service plus service-control UI

## 1. Problem

Staff save or copy documents into folders and must manually choose paper size, simplex/duplex, and printer. Manual handling is slow and error-prone. Hot Folder applies a predictable print rule based on the destination subfolder.

## 2. Goals

1. Monitor a designated root and its rule subfolders.
2. Translate folder names into print settings.
3. Submit stable supported files to a designated printer.
4. Make monitoring and print-job status visible and diagnosable.
5. Keep the core engine independent from the desktop UI so it can later run as a Windows Service.

## 3. Non-goals for initial EXE

- Cloud printing or remote administration.
- OCR, document conversion, editing, or content inspection.
- Guaranteeing physical delivery of paper (printer/driver feedback is outside the basic shell/CLI submission boundary).
- Silent self-updates.
- Running as a service in the first milestone.
- Printing arbitrary file types without a dedicated, tested print adapter.

## 4. Users and primary workflow

An operator configures a root folder, selects a Windows printer and PDF renderer, then starts monitoring. Users copy a PDF into a rule folder. The app waits until the file is stable, validates the rule, submits a print job, and records the result. The source file remains untouched.

## 5. Folder rules

Initial canonical examples:

| Folder name | Paper | Sides |
|---|---|---|
| `A4_Simplex` | A4 | One-sided |
| `A4_Duplex` | A4 | Two-sided |
| `A5-Duplex` | A5 | Two-sided |

Parsing is case-insensitive and accepts underscore or hyphen between paper and sidedness. Initial supported paper names are A4 and A5; sidedness values are Simplex and Duplex. Unknown folder names must not print automatically. Rule folders may exist directly under the root or in descendants; the nearest matching rule folder governs a file. Conflicting nested rule folders must be documented and tested.

## 6. Functional requirements

- **FR-01 Root selection:** Choose a local or accessible network root folder.
- **FR-02 Rule discovery:** Discover recognized rule folders below the root.
- **FR-03 Printer mapping:** Let an operator choose the Windows printer; validate that the selected printer exists.
- **FR-04 Stable-file gate:** A candidate must remain unchanged for a configurable period and be readable before submission.
- **FR-05 Supported formats:** Initial release supports PDF only via a configured SumatraPDF executable. Unsupported formats are logged and skipped.
- **FR-06 Job state:** Track discovered, waiting-for-stability, submitted, and failed states in the UI/log.
- **FR-07 Duplicate protection:** Do not repeatedly submit the same file merely because polling sees it again. Persistence across restarts is a release gate before unattended operation.
- **FR-08 Lifecycle:** Start/stop monitoring without closing the application.
- **FR-09 Diagnostics:** Record timestamp, filename, matched rule, printer, and submission outcome. Do not log document contents.
- **FR-10 Error handling:** A missing root, inaccessible file, missing renderer, unknown rule, or printer error must not crash monitoring.
- **FR-11 Packaging:** Build a Windows EXE distribution and document installation.
- **FR-12 Service readiness:** Keep business logic separate from UI; later service must support install/start/stop/status and a separate control UI.
- **FR-13 Completed archive:** Move only successfully submitted files into the root-level `Completed/` folder while preserving relative paths. Never scan that archive as an input queue.
- **FR-14 Archive safety:** Never overwrite an existing archived file; use a numbered collision name. If the move fails, keep the source and log the archive error.

## 7. Non-functional requirements

- UI remains responsive during monitoring and print submission.
- No source file deletion or mutation.
- Conservative retry policy; never automatically retry an ambiguous submission without duplicate-risk handling.
- Configuration is local and recoverable; logs rotate or have a documented retention policy before production.
- App starts in a safe stopped state unless an explicit, tested auto-start setting is enabled.
- Clear distinction between command submission and confirmed physical printing.
- Minimal privileges; no administrator rights unless the installation method requires them.

## 8. Configuration

Configuration should include root folder, polling interval, stability duration, supported extensions, rule definitions, default printer, renderer path, and logging level. UI changes should be validated before saving. Example: `config.example.json`.

## 9. Acceptance criteria

1. A4_Simplex PDF submits to the selected printer using A4 and simplex settings.
2. A4_Duplex PDF submits with A4 and duplex settings on a verified duplex-capable printer.
3. A5-Duplex PDF submits using A5 and duplex settings.
4. A file still being copied is not submitted until stable.
5. Unknown folders and unsupported extensions are not printed.
6. Repeated polling does not create repeated jobs during the same run.
7. Missing root/renderer/printer errors are visible and monitoring can recover.
8. Stop halts new submissions without corrupting the UI.
9. Automated rule tests pass; packaging can be built on Windows.
10. Target printer tests verify real output before a production release.

## 10. Risks and decisions

- Printer drivers interpret paper and duplex options differently. Validate every supported model/driver combination.
- SumatraPDF command-line print settings and executable discovery must be verified against the installed version.
- Exactly-once physical printing cannot be guaranteed by this app alone; Windows spooler/printer failures can leave ambiguous outcomes.
- Windows services run in a different security/session context from desktop applications. A future service must explicitly configure printer access, network share credentials/permissions, logs, and IPC.
- Binding duplex orientation (long-edge/short-edge) should become an explicit rule setting rather than relying on driver defaults.

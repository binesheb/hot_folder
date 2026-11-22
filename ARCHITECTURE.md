# Architecture

## Current target: Windows desktop EXE

```text
PyQt5 Desktop UI
  | configure / start / stop / show status
  v
Application Controller
  |---- Config store (JSON in %LOCALAPPDATA%)
  |---- Folder scanner (polling; stable-file gate)
  |---- Rule parser (A4_Simplex, A4_Duplex, A5-Duplex)
  |---- Job ledger / logging
  v
Print adapter
  |---- PDF adapter: SumatraPDF CLI
  v
Windows print spooler -> selected printer/driver
```

## Design boundaries

- **Rule parser:** Pure Python; no UI or Windows dependency; unit-testable.
- **Folder scanner:** Finds files and their nearest recognized rule folder. Uses polling for predictable behavior on local and network paths.
- **Stability gate:** Checks file size and modification time over a configurable interval and confirms the file is readable.
- **Print adapter:** Owns platform-specific submission. Initial supported adapter is PDF through SumatraPDF. It must return a structured submission result, not claim physical completion.
- **Job ledger:** Tracks each file's observed signature and submission status to reduce duplicate output. Persistent ledger is required before unattended service deployment.
- **UI:** Configuration, start/stop, status and recent logs only. Avoid putting rule logic in widgets.

## Rule resolution

Given a path under the root, walk from its parent toward the root and choose the nearest directory whose name parses as a valid rule. If no rule folder is found, skip and log. The root itself is not a rule folder unless explicitly configured later.

## Print settings

Rule fields are paper size and sidedness. Map those to the renderer's supported command-line arguments; validate exact syntax against the installed renderer. A configured printer name is passed explicitly. Driver behavior remains a target-printer acceptance test.

## Future service deployment

```text
Windows Service (engine; non-interactive)
  |---- Config + persistent job ledger
  |---- Folder scanner / queue / print adapter
  |---- structured logs
  |---- authenticated local IPC (named pipe or loopback API)
              ^
              |
Separate Service Control App (desktop UI)
  | install / start / stop / status / config / logs
```

Do not try to display a desktop UI directly from a Windows service. Services run in Session 0. The service and controller should communicate over a deliberately secured local IPC boundary, validate caller permissions, and keep credentials out of config/logs. Network share and printer access must be tested under the actual service identity.

## Reliability notes

- Command accepted by the renderer/spooler != printed pages confirmed.
- A timeout during submission can produce an ambiguous outcome; don't blindly retry.
- Persistent idempotency should use canonical path plus file signature and job state, with a manual reprint action for operators.
- Store logs and configuration under a documented per-user or ProgramData path; service deployment should use ProgramData with restrictive ACLs.

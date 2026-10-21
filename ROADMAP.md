# Roadmap

## Milestone 1 — Desktop MVP (current)
- [x] Identify and retain the existing repository/prototype.
- [x] Define the folder-rule convention and initial product requirements.
- [ ] Separate the prototype into maintainable modules.
- [ ] Add stable-file handling and recursive rule resolution.
- [ ] Add explicit printer selection and PDF print adapter.
- [ ] Add automated tests for rule parsing and file discovery.
- [ ] Add Windows build script and packaging validation.
- [ ] Verify actual A4/A5 simplex/duplex output on target printers.

## Milestone 2 — Reliability
- [ ] Persistent job ledger and restart-safe duplicate protection.
- [ ] Bounded retry policy and operator-controlled reprint.
- [ ] Log rotation, diagnostics export, and health state.
- [ ] Configuration validation and recovery.
- [ ] Signed release artifact and installation/uninstallation documentation.

## Milestone 3 — Windows Service
- [ ] Run engine as a Windows Service under a least-privilege identity.
- [ ] Handle service start/stop/shutdown and recovery behavior.
- [ ] Verify network shares and printers under service identity.
- [ ] Add persistent queue and structured event logging.

## Milestone 4 — Service Control Application
- [ ] Separate Windows desktop controller for service lifecycle.
- [ ] Secure local IPC with authorization.
- [ ] View status, recent jobs, logs, and configuration.
- [ ] Installer that can install/update/uninstall the service and controller.
- [ ] Upgrade/rollback and migration tests.

## Release gates
- No unattended deployment until target-printer acceptance tests pass.
- No production service until persistent job state, permissions, logging, and duplicate/ambiguous-submission handling are tested.
- No auto-update until signed/versioned releases and rollback are in place.

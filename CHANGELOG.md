# Changelog

All notable changes to this project will be documented in this file.

The project intends to follow [Semantic Versioning](https://semver.org/) once runnable releases are established.

## [Unreleased]

### Fixed

- Ignore directories detected in the hot folder instead of attempting to send them to the registered print handler.
- Moved folder polling onto a Qt timer so the prototype no longer blocks the PyQt5 UI thread while monitoring.

## [0.1.1] - 2026-08-20

### Changed

- Documented the prototype architecture and current implementation limitations.
- Added safe manual update, revision pinning, and rollback guidance.
- Defined the future opt-in automatic update model using versioned GitHub Releases.
- Recorded packaging, reliability, and test prerequisites before unattended printing or automatic updates.

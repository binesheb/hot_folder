"""Hot Folder desktop application (Windows).

Initial implementation: rule parsing, recursive polling, stable-file gate, and PDF
submission through SumatraPDF. Submission status is not proof of physical printing.
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QTextEdit, QVBoxLayout,
    QWidget,
)

APP_NAME = "Hot Folder"
PAPER_SIZES = {"A4", "A5"}
SIDES = {"SIMPLEX", "DUPLEX"}
RULE_RE = re.compile(r"^(A4|A5)[_-](SIMPLEX|DUPLEX)$", re.IGNORECASE)
LOG = logging.getLogger(APP_NAME)


@dataclass(frozen=True)
class PrintRule:
    paper: str
    sides: str


def parse_rule(folder_name: str) -> Optional[PrintRule]:
    """Parse A4_Simplex, A4-Duplex, A5-Duplex etc.; return None for unknown names."""
    match = RULE_RE.fullmatch(folder_name.strip())
    if not match:
        return None
    paper, sides = match.group(1).upper(), match.group(2).upper()
    if paper not in PAPER_SIZES or sides not in SIDES:
        return None
    return PrintRule(paper=paper, sides=sides.lower())


def find_rule_for_path(file_path: Path, root: Path) -> Optional[PrintRule]:
    """Use the nearest recognized ancestor folder between the file and root."""
    try:
        parent = file_path.resolve().parent
        root_resolved = root.resolve()
        parent.relative_to(root_resolved)
    except (OSError, ValueError):
        return None
    current = parent
    while current != root_resolved:
        rule = parse_rule(current.name)
        if rule:
            return rule
        if current.parent == current:
            break
        current = current.parent
    return None


def default_config_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "HotFolder"
    return Path.home() / ".hotfolder"


def configure_logging(config_dir: Path) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(config_dir / "hotfolder.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


class PdfPrinter:
    """Submits PDF jobs through SumatraPDF's documented command-line interface."""

    def __init__(self, executable: str):
        self.executable = executable.strip()

    def submit(self, path: Path, printer: str, rule: PrintRule) -> tuple[bool, str]:
        if not self.executable or not Path(self.executable).is_file():
            return False, "SumatraPDF.exe was not found; configure its full path."
        if not printer:
            return False, "Select a Windows printer first."
        if path.suffix.lower() != ".pdf":
            return False, "Only PDF files are supported by this initial adapter."

        # SumatraPDF supports paper selection and duplex flags in -print-settings.
        settings = f"paper={rule.paper}"
        if rule.sides == "duplex":
            settings += ",duplex"
        command = [
            self.executable, "-silent", "-print-to", printer,
            "-print-settings", settings, str(path),
        ]
        try:
            completed = subprocess.run(
                command, capture_output=True, text=True, timeout=120, check=False
            )
        except subprocess.TimeoutExpired:
            return False, "PDF submission timed out; outcome may be ambiguous. Check the spooler before retrying."
        except OSError as exc:
            return False, f"Could not start PDF renderer: {exc}"
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            return False, f"PDF renderer exited with code {completed.returncode}. {detail}"
        return True, "Submitted to Windows print pipeline (physical output not confirmed)."


class HotFolderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hot Folder")
        self.resize(760, 520)
        self.config_dir = default_config_dir()
        configure_logging(self.config_dir)
        self.config_path = self.config_dir / "config.json"
        self.config = self.load_config()
        self.seen: set[tuple[str, int, int]] = set()
        self.pending: dict[str, tuple[int, int, float]] = {}
        self.running = False

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        form = QFormLayout()

        root_row = QHBoxLayout()
        self.root_edit = QLineEdit(self.config.get("root_folder", ""))
        browse = QPushButton("Browse…")
        browse.clicked.connect(self.choose_root)
        root_row.addWidget(self.root_edit)
        root_row.addWidget(browse)
        form.addRow("Watched root", root_row)

        printer_row = QHBoxLayout()
        self.printer_combo = QComboBox()
        self.printer_combo.setEditable(False)
        refresh = QPushButton("Refresh printers")
        refresh.clicked.connect(self.load_printers)
        printer_row.addWidget(self.printer_combo)
        printer_row.addWidget(refresh)
        form.addRow("Destination printer", printer_row)

        pdf_row = QHBoxLayout()
        self.pdf_edit = QLineEdit(self.config.get("sumatra_pdf_path", ""))
        pdf_browse = QPushButton("Browse…")
        pdf_browse.clicked.connect(self.choose_pdf_renderer)
        pdf_row.addWidget(self.pdf_edit)
        pdf_row.addWidget(pdf_browse)
        form.addRow("SumatraPDF.exe", pdf_row)
        layout.addLayout(form)

        controls = QHBoxLayout()
        self.start_button = QPushButton("Start monitoring")
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_monitoring)
        save_button = QPushButton("Save settings")
        save_button.clicked.connect(self.save_config)
        controls.addWidget(self.start_button)
        controls.addWidget(self.stop_button)
        controls.addWidget(save_button)
        layout.addLayout(controls)

        self.status = QLabel("Status: Stopped")
        layout.addWidget(self.status)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scan)
        self.load_printers()
        self.restore_printer()
        self.append_log(f"Configuration directory: {self.config_dir}")
        self.append_log("Initial adapter supports PDF files only. Unknown folders are skipped.")

    def load_config(self) -> dict:
        defaults = {
            "root_folder": "",
            "poll_interval_ms": 1000,
            "stable_seconds": 3,
            "printer_name": "",
            "sumatra_pdf_path": r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
            "supported_extensions": [".pdf"],
        }
        try:
            if self.config_path.is_file():
                saved = json.loads(self.config_path.read_text(encoding="utf-8"))
                if isinstance(saved, dict):
                    defaults.update(saved)
        except (OSError, json.JSONDecodeError) as exc:
            LOG.exception("Could not load config")
            QMessageBox.warning(self, APP_NAME, f"Could not read config; using defaults.\n{exc}")
        return defaults

    def append_log(self, message: str) -> None:
        LOG.info(message)
        self.log_view.append(f"{time.strftime('%H:%M:%S')}  {message}")

    def load_printers(self) -> None:
        current = self.printer_combo.currentText()
        self.printer_combo.clear()
        try:
            import win32print
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            names = sorted({item[2] for item in win32print.EnumPrinters(flags)})
        except Exception as exc:
            names = []
            self.append_log(f"Could not enumerate Windows printers: {exc}")
        self.printer_combo.addItems(names)
        wanted = current or self.config.get("printer_name", "")
        index = self.printer_combo.findText(wanted)
        if index >= 0:
            self.printer_combo.setCurrentIndex(index)
        if not names:
            self.append_log("No Windows printers found. Install/configure a printer and refresh.")

    def restore_printer(self) -> None:
        wanted = self.config.get("printer_name", "")
        index = self.printer_combo.findText(wanted)
        if index >= 0:
            self.printer_combo.setCurrentIndex(index)

    def choose_root(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select watched root", self.root_edit.text())
        if selected:
            self.root_edit.setText(selected)

    def choose_pdf_renderer(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, "Select SumatraPDF.exe", self.pdf_edit.text(), "Executable (*.exe)"
        )
        if selected:
            self.pdf_edit.setText(selected)

    def save_config(self) -> bool:
        root = self.root_edit.text().strip()
        if root and not Path(root).is_dir():
            QMessageBox.warning(self, APP_NAME, "The watched root must be an existing directory.")
            return False
        self.config.update({
            "root_folder": root,
            "printer_name": self.printer_combo.currentText(),
            "sumatra_pdf_path": self.pdf_edit.text().strip(),
            "poll_interval_ms": max(500, int(self.config.get("poll_interval_ms", 1000))),
            "stable_seconds": max(2, int(self.config.get("stable_seconds", 3))),
            "supported_extensions": [".pdf"],
        })
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(json.dumps(self.config, indent=2), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, APP_NAME, f"Could not save configuration: {exc}")
            return False
        self.append_log("Settings saved.")
        return True

    def start_monitoring(self) -> None:
        if not self.save_config():
            return
        root = Path(self.config["root_folder"])
        if not root.is_dir():
            QMessageBox.warning(self, APP_NAME, "Choose an existing watched root folder.")
            return
        if not self.config["printer_name"]:
            QMessageBox.warning(self, APP_NAME, "Choose a destination printer.")
            return
        if not Path(self.config["sumatra_pdf_path"]).is_file():
            QMessageBox.warning(self, APP_NAME, "Choose a valid SumatraPDF.exe path.")
            return
        self.pending.clear()
        self.seen.clear()
        self.running = True
        self.timer.start(int(self.config["poll_interval_ms"]))
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status.setText("Status: Monitoring")
        self.append_log(f"Monitoring started: {root}")

    def stop_monitoring(self) -> None:
        self.timer.stop()
        self.running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status.setText("Status: Stopped")
        self.append_log("Monitoring stopped.")

    def scan(self) -> None:
        root = Path(self.config["root_folder"])
        if not root.is_dir():
            self.status.setText("Status: Root folder unavailable")
            self.append_log("Watched root is unavailable; monitoring will retry.")
            return
        now = time.monotonic()
        active_paths: set[str] = set()
        try:
            for folder, dirs, filenames in os.walk(root):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for filename in filenames:
                    path = Path(folder) / filename
                    active_paths.add(str(path))
                    if path.suffix.lower() != ".pdf":
                        continue
                    rule = find_rule_for_path(path, root)
                    if rule is None:
                        continue
                    try:
                        stat = path.stat()
                        signature = (stat.st_size, stat.st_mtime_ns)
                    except OSError:
                        continue
                    key = (str(path.resolve()), signature[0], signature[1])
                    if key in self.seen:
                        continue
                    previous = self.pending.get(str(path))
                    if previous is None or previous[:2] != signature:
                        self.pending[str(path)] = (signature[0], signature[1], now)
                        continue
                    if now - previous[2] < float(self.config.get("stable_seconds", 3)):
                        continue
                    # A read-open check catches some in-progress/locked copies.
                    try:
                        with path.open("rb") as stream:
                            stream.read(1)
                    except OSError:
                        continue
                    self.pending.pop(str(path), None)
                    self.submit_file(path, rule, key)
        except OSError as exc:
            self.append_log(f"Folder scan error: {exc}")

        for path in list(self.pending):
            if path not in active_paths:
                self.pending.pop(path, None)

    def submit_file(self, path: Path, rule: PrintRule, key: tuple[str, int, int]) -> None:
        printer = self.printer_combo.currentText()
        adapter = PdfPrinter(self.pdf_edit.text().strip())
        ok, message = adapter.submit(path, printer, rule)
        # Mark both successful and failed attempts during this run to avoid duplicate
        # output from a tight polling loop. Operator can restart after diagnosing failure.
        self.seen.add(key)
        label = "SUBMITTED" if ok else "FAILED"
        self.append_log(f"{label}: {path.name} | {rule.paper} {rule.sides} | {printer} | {message}")
        self.status.setText(f"Status: {label} — {path.name}")

    def closeEvent(self, event) -> None:
        self.stop_monitoring()
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    window = HotFolderWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())

"""
User-level paths configuration for calibration-statistics-tool.

Everything the tool creates lives in one visible folder (the "home" folder):

    ~/Documents/calibration-tool/          (override with the CST_HOME env var)
        paths.json      settings: output base + default input directories
        config/         editable limits / diagram configs (seeded on first run)
        templates/      PPTX templates (seeded on first run)
        logs/           log files
        output*/        generated reports and diagrams

Versions up to 1.0.23 kept paths.json, config/, templates/ and logs/ in
%APPDATA%\\calibration-statistics-tool (Linux: ~/.config/...).  On first run
those files are copied to the new location; the old folder is left untouched.
"""
from __future__ import annotations
import json
import os
import shutil

_APP_NAME = 'calibration-statistics-tool'


def _get_app_dir() -> str:
    override = os.environ.get('CST_HOME')
    if override:
        return os.path.abspath(os.path.expanduser(override))
    return os.path.join(os.path.expanduser('~'), 'Documents', 'calibration-tool')


def _get_legacy_app_dir() -> str:
    if os.name == 'nt':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.environ.get('XDG_CONFIG_HOME',
                              os.path.join(os.path.expanduser('~'), '.config'))
    return os.path.join(base, _APP_NAME)


APP_DIR: str = _get_app_dir()
LEGACY_APP_DIR: str = _get_legacy_app_dir()
PATHS_FILE: str = os.path.join(APP_DIR, 'paths.json')

_DEFAULT_OUTPUT_BASE = APP_DIR
_DEFAULTS: dict = {
    'output_base': _DEFAULT_OUTPUT_BASE,
    # Input directories: leave empty to use the OS default (home dir).
    # Set these once to the folders where your measurement files live.
    'input_protocol_dir': '',
    'input_ptu_dir': '',
    'input_tx_ant_dir': '',
}


def _copy_missing(src_dir: str, dst_dir: str) -> None:
    """Copy files from src_dir that do not exist in dst_dir yet (never overwrites)."""
    if not os.path.isdir(src_dir):
        return
    os.makedirs(dst_dir, exist_ok=True)
    for fname in os.listdir(src_dir):
        src = os.path.join(src_dir, fname)
        dst = os.path.join(dst_dir, fname)
        if os.path.isfile(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)


def _migrate_legacy_settings() -> None:
    """One-time copy of settings and user-edited config from the old AppData folder."""
    if os.path.normcase(LEGACY_APP_DIR) == os.path.normcase(APP_DIR):
        return
    if not os.path.isdir(LEGACY_APP_DIR):
        return
    try:
        if not os.path.isfile(PATHS_FILE):
            legacy_paths = os.path.join(LEGACY_APP_DIR, 'paths.json')
            if os.path.isfile(legacy_paths):
                os.makedirs(APP_DIR, exist_ok=True)
                shutil.copy2(legacy_paths, PATHS_FILE)
        _copy_missing(os.path.join(LEGACY_APP_DIR, 'config'), os.path.join(APP_DIR, 'config'))
        _copy_missing(os.path.join(LEGACY_APP_DIR, 'templates'), os.path.join(APP_DIR, 'templates'))
    except OSError:
        pass  # migration is best-effort; defaults are seeded afterwards


def _load() -> dict:
    """Load paths.json, writing defaults if the file does not exist yet."""
    if not os.path.isfile(PATHS_FILE):
        os.makedirs(APP_DIR, exist_ok=True)
        with open(PATHS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_DEFAULTS, f, indent=2)
        return dict(_DEFAULTS)

    with open(PATHS_FILE, 'r', encoding='utf-8') as f:
        data: dict = json.load(f)

    # Back-fill any keys added in newer versions
    changed = False
    for key, default_val in _DEFAULTS.items():
        if key not in data:
            data[key] = default_val
            changed = True
    if changed:
        with open(PATHS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    return data


_migrate_legacy_settings()
_config = _load()

# ── Derived paths ────────────────────────────────────────────────────────────
config_dir: str = os.path.join(APP_DIR, 'config')
"""Editable config files (YAML limits, JSON stats config) — seeded on first run."""

templates_dir: str = os.path.join(APP_DIR, 'templates')
"""PPTX report templates — seeded on first run."""


def _copy_defaults_if_missing() -> None:
    """Copy bundled config/assets to the home folder the first time the tool runs.

    Files that already exist are never overwritten, so user edits survive upgrades.
    """
    _here = os.path.dirname(os.path.abspath(__file__))
    _copy_missing(os.path.join(_here, 'config'), config_dir)
    _copy_missing(os.path.join(_here, 'assets'), templates_dir)
    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)


_copy_defaults_if_missing()

# ── Public values ────────────────────────────────────────────────────────────
output_base: str = _config['output_base']
"""Root directory for all generated output sub-folders."""

log_dir: str = os.path.join(APP_DIR, 'logs')
"""Log files always go to <home folder>/logs/."""

input_protocol_dir: str = _config['input_protocol_dir']
"""Default directory for the Protocol Files / Protocol Directory dialogs."""

input_ptu_dir: str = _config['input_ptu_dir']
"""Default directory for the PTU-2 Files dialog."""

input_tx_ant_dir: str = _config['input_tx_ant_dir']
"""Default directory for the Tx-Ant. Diag. Files dialog."""


def reload() -> None:
    """Re-read paths.json from disk (call after the user edits it via the GUI)."""
    global _config, output_base, input_protocol_dir, input_ptu_dir, input_tx_ant_dir
    _config = _load()
    output_base = _config['output_base']
    input_protocol_dir = _config['input_protocol_dir']
    input_ptu_dir = _config['input_ptu_dir']
    input_tx_ant_dir = _config['input_tx_ant_dir']


def save(output_base_path: str) -> None:
    """Persist a new output_base to paths.json."""
    global output_base
    output_base = output_base_path
    _config['output_base'] = output_base_path
    os.makedirs(APP_DIR, exist_ok=True)
    with open(PATHS_FILE, 'w', encoding='utf-8') as f:
        json.dump(_config, f, indent=2)

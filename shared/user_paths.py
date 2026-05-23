"""
User-level paths configuration for calibration-statistics-tool.

On first run this module creates:
    Windows : %APPDATA%\\calibration-statistics-tool\\paths.json
    Linux   : ~/.config/calibration-statistics-tool/paths.json

Edit that file once to tell the tool where to write output.
The GUI (future: Settings dialog) can also update it at runtime.
"""
from __future__ import annotations
import json
import os

_APP_NAME = 'calibration-statistics-tool'


def _get_app_dir() -> str:
    if os.name == 'nt':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.environ.get('XDG_CONFIG_HOME',
                              os.path.join(os.path.expanduser('~'), '.config'))
    return os.path.join(base, _APP_NAME)


APP_DIR: str = _get_app_dir()
PATHS_FILE: str = os.path.join(APP_DIR, 'paths.json')

_DEFAULT_OUTPUT_BASE = os.path.join(os.path.expanduser('~'), 'Documents', 'calibration-tool')
_DEFAULTS: dict = {
    'output_base': _DEFAULT_OUTPUT_BASE,
}


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


_config = _load()

# ── Public values ────────────────────────────────────────────────────────────
output_base: str = _config['output_base']
"""Root directory for all generated output sub-folders."""

log_dir: str = os.path.join(APP_DIR, 'logs')
"""Log files always go to AppData/calibration-statistics-tool/logs/."""


def reload() -> None:
    """Re-read paths.json from disk (call after the user edits it via the GUI)."""
    global _config, output_base
    _config = _load()
    output_base = _config['output_base']


def save(output_base_path: str) -> None:
    """Persist a new output_base to paths.json."""
    global output_base
    output_base = output_base_path
    _config['output_base'] = output_base_path
    os.makedirs(APP_DIR, exist_ok=True)
    with open(PATHS_FILE, 'w', encoding='utf-8') as f:
        json.dump(_config, f, indent=2)

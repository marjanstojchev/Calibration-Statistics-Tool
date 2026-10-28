"""user_paths: single visible home folder + one-time migration from the old AppData folder."""
import json
import os
import subprocess
import sys

CODE = (
    "import json, calibration_statistics_tool.shared.user_paths as up;"
    "print(json.dumps({k: getattr(up, k) for k in "
    "['APP_DIR','PATHS_FILE','config_dir','templates_dir','log_dir','output_base']}))"
)


def _run(tmp_path, legacy_files=None, home_files=None):
    home = tmp_path / "home"
    appdata = tmp_path / "appdata"
    legacy = appdata / "calibration-statistics-tool"
    for rel, text in (legacy_files or {}).items():
        p = legacy / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    for rel, text in (home_files or {}).items():
        p = home / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    env = dict(os.environ, CST_HOME=str(home), APPDATA=str(appdata),
               XDG_CONFIG_HOME=str(appdata))
    out = subprocess.run([sys.executable, "-c", CODE], env=env, capture_output=True,
                         text=True, check=True).stdout.strip().splitlines()[-1]
    return home, legacy, json.loads(out)


def test_everything_lives_under_home_folder(tmp_path):
    home, legacy, paths = _run(tmp_path)
    assert paths["APP_DIR"] == str(home)
    assert paths["output_base"] == str(home)
    for key in ("PATHS_FILE", "config_dir", "templates_dir", "log_dir"):
        assert paths[key].startswith(str(home))
    assert (home / "paths.json").is_file()
    assert any((home / "config").glob("*.yaml"))
    assert any((home / "templates").glob("*.pptx"))
    assert not legacy.exists()


def test_legacy_settings_and_edited_config_are_migrated(tmp_path):
    legacy_paths = json.dumps({"output_base": "D:/out", "input_protocol_dir": "D:/prot",
                               "input_ptu_dir": "", "input_tx_ant_dir": ""})
    home, legacy, paths = _run(tmp_path, legacy_files={
        "paths.json": legacy_paths,
        "config/CalLimits.yaml": "edited: true\n",
    })
    assert paths["output_base"] == "D:/out"
    assert json.loads((home / "paths.json").read_text())["input_protocol_dir"] == "D:/prot"
    assert (home / "config" / "CalLimits.yaml").read_text() == "edited: true\n"
    assert (legacy / "paths.json").is_file()  # old folder is left untouched


def test_existing_home_files_are_not_overwritten(tmp_path):
    home, legacy, paths = _run(
        tmp_path,
        legacy_files={"config/CalLimits.yaml": "legacy\n"},
        home_files={"config/CalLimits.yaml": "current\n"},
    )
    assert (home / "config" / "CalLimits.yaml").read_text() == "current\n"

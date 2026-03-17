"""
MainView — View layer for the Calibration Statistics Tool GUI (PST-47).

Wraps the module-level widget declarations in pyside_qtgui.py behind a class
boundary.  All widgets are accessible as attributes (delegated via
__getattr__), so existing code that uses `qt.<widget>` keeps working by
pointing `qt` at a MainView instance instead of the raw module.

Presentation-only helpers (pure Qt widget updates, no business logic) belong
here.  Logic that decides *what* to display lives in the controllers.
"""

from __future__ import annotations

import pyside_qtgui as _qt  # importing triggers QApplication + widget setup


class MainView:
    """Qt View layer — delegates attribute access to pyside_qtgui module."""

    def __init__(self) -> None:
        self._qt = _qt

    # ------------------------------------------------------------------ #
    # Attribute delegation — all module-level widgets are accessible as
    # view.<widget_name> transparently.
    # ------------------------------------------------------------------ #

    def __getattr__(self, name: str):
        try:
            return getattr(self._qt, name)
        except AttributeError:
            raise AttributeError(f"MainView has no attribute '{name}'")

    # ------------------------------------------------------------------ #
    # Application lifecycle
    # ------------------------------------------------------------------ #

    def show(self) -> None:
        """Show the main application window."""
        self._qt.mainWidget.show()

    def exec_(self) -> int:
        """Start the Qt event loop and return exit code."""
        return self._qt.app.exec_()

    # ------------------------------------------------------------------ #
    # Parse-protocol stat label helpers
    # ------------------------------------------------------------------ #

    def set_loaded_protocols_label(self, count: int) -> None:
        self._qt.parseProtLoadedProtLabel.setText(
            self._qt.parseProtLoadedProtStr + str(count)
        )

    def set_ptu2_files_label(self, count: int) -> None:
        self._qt.parseProtPtu2FilesLabel.setText(
            self._qt.parseProtPtu2FilesStr + str(count)
        )

    def set_tx_ant_diag_files_label(self, count: int) -> None:
        self._qt.parseProtTxAntDiagFilesLabel.setText(
            self._qt.parseProtTxAntDiagFilesStr + str(count)
        )

    def set_sep_par_ptu2_files_label(self, count: int) -> None:
        self._qt.parseProtSepParPtu2FilesLabel.setText(
            self._qt.parseProtSepParPtu2FilesStr + str(count)
        )

    def set_sep_par_tx_ant_diag_files_label(self, count: int) -> None:
        self._qt.parseProtSepParTxAntDiagFilesLabel.setText(
            self._qt.parseProtSepParTxAntDiagFilesStr + str(count)
        )

    def set_progress_label(self, text: str) -> None:
        self._qt.parseProtProgresLabel.setText(text)

    def set_progress_bar(self, value: int) -> None:
        self._qt.parseProtProgresBar.setValue(value)

    # ------------------------------------------------------------------ #
    # Table helpers
    # ------------------------------------------------------------------ #

    def clear_table(self, table) -> None:
        """Remove all rows from a QTableWidget."""
        table.setRowCount(0)

    def clear_all_parse_tables(self) -> None:
        """Clear all parse-protocol tables."""
        for table in (
            self._qt.parseProtSelProtTable,
            self._qt.parseProtAccProtTable,
            self._qt.parseProtAddPtu2ParsedTable,
            self._qt.parseProtAddPtu2FailedTable,
            self._qt.parseProtAddTxAntDiagParsedTable,
            self._qt.parseProtAddTxAntDiagFailedTable,
            self._qt.parseProtStatsParsedTable,
            self._qt.parseProtStatsFailedTable,
        ):
            table.setRowCount(0)

    # ------------------------------------------------------------------ #
    # Read helpers for widget state (used by controllers to read UI values)
    # ------------------------------------------------------------------ #

    def get_burn_in_cal_mode(self) -> int:
        """Return checked button ID from the BurnIn/Cal radio group."""
        return self._qt.parseProtBurnInCalGroup.checkedId()

    def get_include_burn_in_start(self) -> bool:
        return self._qt.parseProtBurnStartCheckBox.isChecked()

    def get_use_sensor_muster(self) -> int:
        return 1 if self._qt.parseProtSensorMusterCheckBox.isChecked() else 0

    def get_sensor_muster_list(self) -> list[str]:
        raw = self._qt.parseProtSensorMusterLEdit.text().strip()
        return raw.split() if raw else []

    def get_img_gen_mode(self) -> int:
        return self._qt.sysDiagPlotSetupImgGenGroup.checkedId()

    def get_script_mode(self) -> int:
        return self._qt.sysDiagPlotSetupScriptModeGroup.checkedId()

    def get_three_graph_layout(self) -> bool:
        return self._qt.sysDiagPlotSetup3GraphLayoutImgCheckBox.isChecked()

    def get_image_dpi(self) -> int | None:
        from shared import safeparse as sp
        text = self._qt.sysDiagPlotSetupImageDpiLEdit.text()
        if sp.checkInt(text):
            return int(text)
        return None

    def get_x_scale_auto(self) -> bool:
        return self._qt.sysDiagPlotSetupScalingAutoCheckBox.isChecked()

    def get_x_scale_az(self) -> float | None:
        from shared import safeparse as sp
        text = self._qt.sysDiagPlotSetupScalingXScaleAzLEdit.text()
        if sp.checkDecimal(text):
            return float(text)
        return None

    def get_x_scale_el(self) -> float | None:
        from shared import safeparse as sp
        text = self._qt.sysDiagPlotSetupScalingXScaleElLEdit.text()
        if sp.checkDecimal(text):
            return float(text)
        return None

    def get_y_limits_mode(self) -> int:
        return self._qt.sysDiagPlotSetupScalingYLimitsGroup.checkedId()

    def get_diff_phase_diff_scaling(self) -> float | None:
        from shared import safeparse as sp
        text = self._qt.sysDiagPlotSetupScalingDiffPhDiffLEdit.text()
        if sp.checkDecimal(text):
            return float(text)
        return None

    def get_ideal_phase_diff(self) -> bool:
        return self._qt.sysDiagPlotSetupGraphConfIdealCurveCheckBox.isChecked()

    # ------------------------------------------------------------------ #
    # Sensor muster enable / disable
    # ------------------------------------------------------------------ #

    def set_sensor_muster_enabled(self, enabled: bool) -> None:
        self._qt.parseProtSensorMusterLEdit.setEnabled(enabled)
        self._qt.parseProtSensorMusterLabel.setEnabled(enabled)

    # ------------------------------------------------------------------ #
    # Parse-protocol stats counter labels (ratio format)
    # ------------------------------------------------------------------ #

    def set_loaded_prot_ratio_label(self, accepted: int, filtered: int) -> None:
        """Display accepted / (accepted + filtered) for the loaded protocols label."""
        self._qt.parseProtLoadedProtLabel.setText(
            self._qt.parseProtLoadedProtStr + f'{accepted} / {accepted + filtered}'
        )

    def set_eol_error_label(self, count, total=None) -> None:
        suffix = str(count) if total is None else f'{count} / {total}'
        self._qt.parseProtEolErrorLabel.setText(self._qt.parseProtEolErrorStr + suffix)

    def set_abort_crit_label(self, count, total=None) -> None:
        suffix = str(count) if total is None else f'{count} / {total}'
        self._qt.parseProtAbbortCritLabel.setText(self._qt.parseProtAbbortCritStr + suffix)

    def set_meas_limits_label(self, count, total=None) -> None:
        suffix = str(count) if total is None else f'{count} / {total}'
        self._qt.parseProtMeasLimitsExcLabel.setText(self._qt.parseProtMeasLimitsExcStr + suffix)

    def set_parsed_loaded_label(self, parsed, total=None) -> None:
        suffix = str(parsed) if total is None else f'{parsed} / {total}'
        self._qt.parseProtParsedLoadedProtLabel.setText(
            self._qt.parseProtParsedLoadedProtStr + suffix
        )

    # ------------------------------------------------------------------ #
    # Progress bar operations
    # ------------------------------------------------------------------ #

    def reset_progress_bar(self) -> None:
        self._qt.parseProtProgresBar.reset()

    def set_progress_bar_range(self, max_val: int) -> None:
        self._qt.parseProtProgresBar.setRange(0, max_val)

    def set_progress_bar_format(self, fmt: str) -> None:
        self._qt.parseProtProgresBar.setFormat(fmt)

    def get_progress_bar_value(self) -> int:
        return self._qt.parseProtProgresBar.value()

    # ------------------------------------------------------------------ #
    # File path label helpers (sets both text and tooltip)
    # ------------------------------------------------------------------ #

    def set_burn_in_limits_file(self, path: str) -> None:
        self._qt.parseProtProtDataInFileBurnInLabel.setText(path)
        self._qt.parseProtProtDataInFileBurnInLabel.setToolTip(path)

    def set_cal_limits_file(self, path: str) -> None:
        self._qt.parseProtProtDataInFileCalLabel.setText(path)
        self._qt.parseProtProtDataInFileCalLabel.setToolTip(path)

    def set_burn_in_lim_groups_file(self, path: str) -> None:
        self._qt.parseProtProtDataLimGroupsBurnInLabel.setText(path)
        self._qt.parseProtProtDataLimGroupsBurnInLabel.setToolTip(path)

    def set_cal_lim_groups_file(self, path: str) -> None:
        self._qt.parseProtProtDataLimGroupsCalLabel.setText(path)
        self._qt.parseProtProtDataLimGroupsCalLabel.setToolTip(path)

    def set_stats_input_conf_path(self, path: str) -> None:
        self._qt.statsInputConfPathLabel.setText(path)
        self._qt.statsInputConfPathLabel.setToolTip(path)

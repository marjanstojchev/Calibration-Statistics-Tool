"""PST-65 – Integration tests for sys_diag_tab (split from pyside_qtgui / main).

Run:
    py -m pytest tests/integration/test_sys_diag_tab_integration.py -v
"""
from __future__ import annotations

import importlib
import os
import sys

import pytest


@pytest.fixture(scope="session")
def mod():
    """Import sys_diag_tab exactly once per test session."""
    return importlib.import_module("calibration_statistics_tool.ui.tabs.sys_diag_tab")


# ===========================================================================
# 1. Tab widget & layout
# ===========================================================================
class TestTabWidget:
    def test_tab_is_qwidget(self, mod):
        from PySide6.QtWidgets import QWidget
        assert isinstance(mod.sysDiagTab, QWidget)

    def test_layout_attached_to_tab(self, mod):
        assert mod.sysDiagTab.layout() is mod.sysDiagLayout

    def test_start_button_text(self, mod):
        assert mod.sysDiagStartPushBtn.text() == "Start"


# ===========================================================================
# 2. Input Setup – Angle group has exactly 2 radio buttons with ids 0 and 1
# ===========================================================================
class TestInputSetupAngleGroup:
    def test_angle_group_has_two_buttons(self, mod):
        assert len(mod.sysDiagInputSetupAngleGroup.buttons()) == 2

    def test_angle_group_ids(self, mod):
        ids = {mod.sysDiagInputSetupAngleGroup.id(b)
               for b in mod.sysDiagInputSetupAngleGroup.buttons()}
        assert ids == {0, 1}


# ===========================================================================
# 3. Input Setup – Sensor Orientation defaults to Normal (id=0)
# ===========================================================================
class TestInputSetupSensorOrientGroup:
    def test_sensor_orient_has_two_buttons(self, mod):
        assert len(mod.sysDiagInputSetupSensorOrientGroup.buttons()) == 2

    def test_normal_radio_is_checked_by_default(self, mod):
        assert mod.sysDiagInputSetupSensorOrientRadio1.isChecked()

    def test_upside_down_radio_is_not_checked(self, mod):
        assert not mod.sysDiagInputSetupSensorOrientRadio2.isChecked()

    def test_sensor_orient_ids(self, mod):
        assert mod.sysDiagInputSetupSensorOrientGroup.id(mod.sysDiagInputSetupSensorOrientRadio1) == 0
        assert mod.sysDiagInputSetupSensorOrientGroup.id(mod.sysDiagInputSetupSensorOrientRadio2) == 1


# ===========================================================================
# 4. Input Setup – Chirp group: 4 buttons, non-exclusive, 1/2/3 checked
# ===========================================================================
class TestInputSetupChirpGroup:
    def test_chirp_group_has_four_buttons(self, mod):
        assert len(mod.sysDiagInputSetupChirpGroup.buttons()) == 4

    def test_chirp_group_is_non_exclusive(self, mod):
        assert not mod.sysDiagInputSetupChirpGroup.exclusive()

    def test_chirp0_unchecked_by_default(self, mod):
        assert not mod.sysDiagInputSetupChirp0CheckBox.isChecked()

    def test_chirp1_checked_by_default(self, mod):
        assert mod.sysDiagInputSetupChirp1CheckBox.isChecked()

    def test_chirp2_checked_by_default(self, mod):
        assert mod.sysDiagInputSetupChirp2CheckBox.isChecked()

    def test_chirp3_checked_by_default(self, mod):
        assert mod.sysDiagInputSetupChirp3CheckBox.isChecked()

    def test_chirp_group_ids(self, mod):
        ids = {mod.sysDiagInputSetupChirpGroup.id(b)
               for b in mod.sysDiagInputSetupChirpGroup.buttons()}
        assert ids == {0, 1, 2, 3}


# ===========================================================================
# 5. Input Setup – Diagram Config: desired-range validator (0-200)
# ===========================================================================
class TestInputSetupDiagConfigRangeValidator:
    def test_validator_range_bottom(self, mod):
        assert mod.sysDiagInputSetupDiagConfigDesRangeIntValidator.bottom() == 0

    def test_validator_range_top(self, mod):
        assert mod.sysDiagInputSetupDiagConfigDesRangeIntValidator.top() == 200

    def test_low_ledit_uses_correct_validator(self, mod):
        assert (mod.sysDiagInputSetupDiagConfigDesRangeLowLEdit.validator()
                is mod.sysDiagInputSetupDiagConfigDesRangeIntValidator)

    def test_high_ledit_uses_correct_validator(self, mod):
        assert (mod.sysDiagInputSetupDiagConfigDesRangeHighLEdit.validator()
                is mod.sysDiagInputSetupDiagConfigDesRangeIntValidator)

    def test_low_ledit_max_length(self, mod):
        assert mod.sysDiagInputSetupDiagConfigDesRangeLowLEdit.maxLength() == 3

    def test_high_ledit_max_length(self, mod):
        assert mod.sysDiagInputSetupDiagConfigDesRangeHighLEdit.maxLength() == 3


# ===========================================================================
# 6. Plot Setup – Script mode defaults to Presentation (id=0)
# ===========================================================================
class TestPlotSetupScriptMode:
    def test_presentation_is_checked_by_default(self, mod):
        assert mod.sysDiagPlotSetupScriptModeRadio1.isChecked()

    def test_plot_window_is_not_checked(self, mod):
        assert not mod.sysDiagPlotSetupScriptModeRadio2.isChecked()

    def test_script_mode_radio1_id_is_0(self, mod):
        assert mod.sysDiagPlotSetupScriptModeGroup.id(mod.sysDiagPlotSetupScriptModeRadio1) == 0

    def test_script_mode_radio2_id_is_1(self, mod):
        assert mod.sysDiagPlotSetupScriptModeGroup.id(mod.sysDiagPlotSetupScriptModeRadio2) == 1


# ===========================================================================
# 7. Plot Setup – Image DPI validator (0-500) and line edit wiring
# ===========================================================================
class TestPlotSetupImageDpiValidator:
    def test_image_dpi_validator_bottom(self, mod):
        assert mod.sysDiagPlotSetupImageDpiIntValidator.bottom() == 0

    def test_image_dpi_validator_top(self, mod):
        assert mod.sysDiagPlotSetupImageDpiIntValidator.top() == 500

    def test_image_dpi_ledit_uses_correct_validator(self, mod):
        assert (mod.sysDiagPlotSetupImageDpiLEdit.validator()
                is mod.sysDiagPlotSetupImageDpiIntValidator)

    def test_image_dpi_ledit_max_length(self, mod):
        assert mod.sysDiagPlotSetupImageDpiLEdit.maxLength() == 3


# ===========================================================================
# 8. Plot Setup – X-Scale validator (0-150) wired to both Az and El line edits
# ===========================================================================
class TestPlotSetupXScaleValidator:
    def test_x_scale_validator_bottom(self, mod):
        assert mod.sysDiagPlotSetupScalingXScaleIntValidator.bottom() == 0

    def test_x_scale_validator_top(self, mod):
        assert mod.sysDiagPlotSetupScalingXScaleIntValidator.top() == 150

    def test_az_ledit_uses_x_scale_validator(self, mod):
        assert (mod.sysDiagPlotSetupScalingXScaleAzLEdit.validator()
                is mod.sysDiagPlotSetupScalingXScaleIntValidator)

    def test_el_ledit_uses_x_scale_validator(self, mod):
        assert (mod.sysDiagPlotSetupScalingXScaleElLEdit.validator()
                is mod.sysDiagPlotSetupScalingXScaleIntValidator)


# ===========================================================================
# 9. Graph Configuration group: checkbox count and non-exclusivity
# ===========================================================================
class TestGraphConfigGroup:
    def test_checkbox_count_matches_graph_config(self, mod):
        assert len(mod.sysDiagPlotSetupGraphConfGroup.buttons()) == len(mod.graphConfig)

    def test_group_is_non_exclusive(self, mod):
        assert not mod.sysDiagPlotSetupGraphConfGroup.exclusive()

    def test_checkbox_labels_cover_all_graph_config_keys(self, mod):
        labels = {b.text() for b in mod.sysDiagPlotSetupGraphConfGroup.buttons()}
        for key in mod.graphConfig:
            expected = mod.graphStringMapping(key)
            assert expected in labels, f"Checkbox for '{key}' → '{expected}' not found"


# ===========================================================================
# 10. Plot Window – Graph Type combo populated from plotWindowConfigGraphList
# ===========================================================================
class TestPlotWindowGraphTypeCombo:
    def test_combo_count_matches_list(self, mod):
        assert (mod.sysDiagPlotWindowGraphTypeComboBox.count()
                == len(mod.plotWindowConfigGraphList))

    def test_combo_items_match_list(self, mod):
        cb = mod.sysDiagPlotWindowGraphTypeComboBox
        for i, expected in enumerate(mod.plotWindowConfigGraphList):
            assert cb.itemText(i) == expected

    def test_combo_default_index_is_0(self, mod):
        assert mod.sysDiagPlotWindowGraphTypeComboBox.currentIndex() == 0


# ===========================================================================
# 11. Plot Window – Ant Type validator (0-999)
# ===========================================================================
class TestPlotWindowAntTypeValidator:
    def test_ant_type_validator_bottom(self, mod):
        assert mod.sysDiagPlotWindowAntTypValidator.bottom() == 0

    def test_ant_type_validator_top(self, mod):
        assert mod.sysDiagPlotWindowAntTypValidator.top() == 999

    def test_ant_type_ledit_uses_correct_validator(self, mod):
        assert (mod.sysDiagPlotWindowAntTypLEdit.validator()
                is mod.sysDiagPlotWindowAntTypValidator)

    def test_ant_type_ledit_max_length(self, mod):
        assert mod.sysDiagPlotWindowAntTypLEdit.maxLength() == 3


# ===========================================================================
# 12. Plot Window – Diagram Number validator (0-200)
# ===========================================================================
class TestPlotWindowDiagNumValidator:
    def test_diag_num_validator_bottom(self, mod):
        assert mod.sysDiagPlotWindowDiagNumValidator.bottom() == 0

    def test_diag_num_validator_top(self, mod):
        assert mod.sysDiagPlotWindowDiagNumValidator.top() == 200

    def test_diag_num_ledit_uses_correct_validator(self, mod):
        assert (mod.sysDiagPlotWindowDiagNumLEdit.validator()
                is mod.sysDiagPlotWindowDiagNumValidator)

    def test_diag_num_ledit_max_length(self, mod):
        assert mod.sysDiagPlotWindowDiagNumLEdit.maxLength() == 3


# ===========================================================================
# 13. BUG #1 – RxChannel line edit must use sysDiagPlotWindowRxChValidator (0-11)
#     CURRENTLY FAILS: wired to sysDiagPlotSetupImageDpiIntValidator (0-500)
# ===========================================================================
class TestRxChannelValidator:
    def test_rx_ch_validator_bottom(self, mod):
        assert mod.sysDiagPlotWindowRxChValidator.bottom() == 0

    def test_rx_ch_validator_top(self, mod):
        assert mod.sysDiagPlotWindowRxChValidator.top() == 11

    def test_rx_ch_ledit_uses_correct_validator(self, mod):
        """REGRESSION: was sysDiagPlotSetupImageDpiIntValidator (range 0-500)."""
        assert (mod.sysDiagPlotWindowRxChLEdit.validator()
                is mod.sysDiagPlotWindowRxChValidator), (
            "sysDiagPlotWindowRxChLEdit must use sysDiagPlotWindowRxChValidator (0-11), "
            "not sysDiagPlotSetupImageDpiIntValidator (0-500)"
        )

    def test_rx_ch_ledit_not_wired_to_image_dpi_validator(self, mod):
        assert (mod.sysDiagPlotWindowRxChLEdit.validator()
                is not mod.sysDiagPlotSetupImageDpiIntValidator)

    def test_rx_ch_ledit_max_length(self, mod):
        assert mod.sysDiagPlotWindowRxChLEdit.maxLength() == 2


# ===========================================================================
# 14. Plot Window – All Graphs combos: populated and correct defaults
# ===========================================================================
class TestPlotWindowAllGraphsCombos:
    @pytest.mark.parametrize("attr, expected_index", [
        ("sysDiagPlotWindowAllGraphsComboBox1", 0),
        ("sysDiagPlotWindowAllGraphsComboBox2", 8),
        ("sysDiagPlotWindowAllGraphsComboBox3", 6),
    ])
    def test_combo_default_index(self, mod, attr, expected_index):
        assert getattr(mod, attr).currentIndex() == expected_index

    @pytest.mark.parametrize("attr", [
        "sysDiagPlotWindowAllGraphsComboBox1",
        "sysDiagPlotWindowAllGraphsComboBox2",
        "sysDiagPlotWindowAllGraphsComboBox3",
    ])
    def test_combo_populated(self, mod, attr):
        assert getattr(mod, attr).count() == len(mod.plotWindowConfigGraphList)

    def test_all_graphs_mode_unchecked_by_default(self, mod):
        assert not mod.sysDiagPlotWindowAllGraphsCheckBox.isChecked()

    @pytest.mark.parametrize("attr", [
        "sysDiagPlotWindowAllGraphsCheckBox1",
        "sysDiagPlotWindowAllGraphsCheckBox2",
        "sysDiagPlotWindowAllGraphsCheckBox3",
    ])
    def test_graph_checkboxes_checked_by_default(self, mod, attr):
        assert getattr(mod, attr).isChecked()


# ===========================================================================
# 15. BUG #2 – Two-Graph combos must have items populated (addItems was missing)
#     CURRENTLY FAILS: all four combos have count() == 0
# ===========================================================================
class TestTwoGraphCombos:
    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfTwoGraphComboBox11",
        "sysDiagSlideConfTwoGraphComboBox12",
        "sysDiagSlideConfTwoGraphComboBox21",
        "sysDiagSlideConfTwoGraphComboBox22",
    ])
    def test_combo_is_populated(self, mod, attr):
        """REGRESSION: .addItems() was never called — combos were empty."""
        cb = getattr(mod, attr)
        assert cb.count() == len(mod.plotWindowConfigGraphList), (
            f"{attr}: expected {len(mod.plotWindowConfigGraphList)} items, got {cb.count()}"
        )

    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfTwoGraphComboBox11",
        "sysDiagSlideConfTwoGraphComboBox12",
        "sysDiagSlideConfTwoGraphComboBox21",
        "sysDiagSlideConfTwoGraphComboBox22",
    ])
    def test_combo_items_match_list(self, mod, attr):
        cb = getattr(mod, attr)
        for i, expected in enumerate(mod.plotWindowConfigGraphList):
            assert cb.itemText(i) == expected

    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfTwoGraphCheckBox1",
        "sysDiagSlideConfTwoGraphCheckBox2",
    ])
    def test_two_graph_checkboxes_checked_by_default(self, mod, attr):
        assert getattr(mod, attr).isChecked()


# ===========================================================================
# 16. Four-Graph combos – populated and default index 0
# ===========================================================================
class TestFourGraphCombos:
    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfFourGraphComboBox1",
        "sysDiagSlideConfFourGraphComboBox2",
        "sysDiagSlideConfFourGraphComboBox3",
    ])
    def test_combo_populated(self, mod, attr):
        assert getattr(mod, attr).count() == len(mod.plotWindowConfigGraphList)

    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfFourGraphComboBox1",
        "sysDiagSlideConfFourGraphComboBox2",
        "sysDiagSlideConfFourGraphComboBox3",
    ])
    def test_combo_default_index_is_0(self, mod, attr):
        assert getattr(mod, attr).currentIndex() == 0

    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfFourGraphCheckBox1",
        "sysDiagSlideConfFourGraphCheckBox2",
        "sysDiagSlideConfFourGraphCheckBox3",
    ])
    def test_checkboxes_checked_by_default(self, mod, attr):
        assert getattr(mod, attr).isChecked()


# ===========================================================================
# 17. Three-Graph combos – populated and default index 0
# ===========================================================================
class TestThreeGraphCombos:
    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfThreeGraphComboBox1",
        "sysDiagSlideConfThreeGraphComboBox2",
        "sysDiagSlideConfThreeGraphComboBox3",
    ])
    def test_combo_populated(self, mod, attr):
        assert getattr(mod, attr).count() == len(mod.plotWindowConfigGraphList)

    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfThreeGraphComboBox1",
        "sysDiagSlideConfThreeGraphComboBox2",
        "sysDiagSlideConfThreeGraphComboBox3",
    ])
    def test_combo_default_index_is_0(self, mod, attr):
        assert getattr(mod, attr).currentIndex() == 0

    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfThreeGraphCheckBox1",
        "sysDiagSlideConfThreeGraphCheckBox2",
        "sysDiagSlideConfThreeGraphCheckBox3",
    ])
    def test_checkboxes_checked_by_default(self, mod, attr):
        assert getattr(mod, attr).isChecked()


# ===========================================================================
# 18. All-Slides combos: populated and correct defaults
# ===========================================================================
class TestAllSlidesCombos:
    @pytest.mark.parametrize("attr, expected_index", [
        ("sysDiagSlideConfGeneralAllSlidesComboBox1", 0),
        ("sysDiagSlideConfGeneralAllSlidesComboBox2", 8),
        ("sysDiagSlideConfGeneralAllSlidesComboBox3", 6),
    ])
    def test_combo_default_index(self, mod, attr, expected_index):
        assert getattr(mod, attr).currentIndex() == expected_index

    @pytest.mark.parametrize("attr", [
        "sysDiagSlideConfGeneralAllSlidesComboBox1",
        "sysDiagSlideConfGeneralAllSlidesComboBox2",
        "sysDiagSlideConfGeneralAllSlidesComboBox3",
    ])
    def test_combo_populated(self, mod, attr):
        assert getattr(mod, attr).count() == len(mod.plotWindowConfigGraphList)

    def test_all_graphs_slide_checkbox_checked_by_default(self, mod):
        assert mod.sysDiagSlideConfGeneralAllGraphsSlideCheckBox.isChecked()


# ===========================================================================
# 19. BUG #3 – SensorNumSlide must use its own validator, NOT ImageDpi
#     CURRENTLY FAILS: wired to sysDiagPlotSetupImageDpiIntValidator
# ===========================================================================
class TestSensorNumSlideValidator:
    def test_sensor_num_slide_validator_bottom(self, mod):
        assert mod.sysDiagSlideConfGeneralSensorNumSlideIntValidator.bottom() == 0

    def test_sensor_num_slide_validator_top(self, mod):
        assert mod.sysDiagSlideConfGeneralSensorNumSlideIntValidator.top() == 500

    def test_sensor_num_slide_ledit_uses_correct_validator(self, mod):
        """REGRESSION: was sysDiagPlotSetupImageDpiIntValidator (wrong object)."""
        assert (mod.sysDiagSlideConfGeneralSensorNumSlideLEdit.validator()
                is mod.sysDiagSlideConfGeneralSensorNumSlideIntValidator), (
            "sysDiagSlideConfGeneralSensorNumSlideLEdit must use "
            "sysDiagSlideConfGeneralSensorNumSlideIntValidator, "
            "not sysDiagPlotSetupImageDpiIntValidator"
        )

    def test_sensor_num_slide_ledit_not_wired_to_image_dpi_validator(self, mod):
        assert (mod.sysDiagSlideConfGeneralSensorNumSlideLEdit.validator()
                is not mod.sysDiagPlotSetupImageDpiIntValidator)

    def test_sensor_num_slide_ledit_max_length(self, mod):
        assert mod.sysDiagSlideConfGeneralSensorNumSlideLEdit.maxLength() == 3


# ===========================================================================
# 20. graphStringMapping – exhaustive contract for all 9 keys
# ===========================================================================
class TestGraphStringMapping:
    @pytest.mark.parametrize("key, expected", [
        ("level",            "Level [dB]"),
        ("avgLevel",         "Avg. Level [dB]"),
        ("normLevel",        "Norm. Level [dB]"),
        ("avgNormLevel",     "Avg. Norm. Level [dB]"),
        ("phaseDiff",        "Phase Diff. [°]"),
        ("avgPhaseDiff",     "Avg. Phase Diff. [°]"),
        ("diffPhaseDiff",    "Diff. of Phase Diff. [°]"),
        ("avgDiffPhaseDiff", "Avg. Diff. of Phase Diff. [°]"),
        ("corrPhaseDiff",    "Corr. Phase Diff. [°]"),
    ])
    def test_known_key_returns_correct_string(self, mod, key, expected):
        assert mod.graphStringMapping(key) == expected

    def test_unknown_key_returns_empty_string(self, mod):
        assert mod.graphStringMapping("nonexistent") == ""

    def test_all_graph_config_keys_have_non_empty_mapping(self, mod):
        for key in mod.graphConfig:
            assert mod.graphStringMapping(key) != "", f"No mapping for key '{key}'"


# ===========================================================================
# 21. boolMapping – exhaustive contract
# ===========================================================================
class TestBoolMapping:
    def test_true_returns_1(self, mod):
        assert mod.boolMapping(True) == 1

    def test_false_returns_0(self, mod):
        assert mod.boolMapping(False) == 0

    def test_int_1_returns_true(self, mod):
        assert mod.boolMapping(1) is True

    def test_int_0_returns_false(self, mod):
        assert mod.boolMapping(0) is False

    def test_invalid_int_raises_value_error(self, mod):
        with pytest.raises(ValueError):
            mod.boolMapping(2)

    def test_string_raises_type_error(self, mod):
        with pytest.raises(TypeError):
            mod.boolMapping("yes")

    def test_none_raises_type_error(self, mod):
        with pytest.raises(TypeError):
            mod.boolMapping(None)

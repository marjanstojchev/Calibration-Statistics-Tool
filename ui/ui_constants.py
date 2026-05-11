"""PST-60: Shared UI constants and style strings.

Pure-Python values only — no Qt objects — so this module is safe to import
before QApplication is created.

All theme colours, style strings, and layout constants are now defined in
``ui_theme.py`` and re-exported here for full backward compatibility.
The only values *owned* by this module are the matplotlib ``color_list`` /
``color_list_rev`` (they are plot-specific and unrelated to Qt theming).
"""

# ---------------------------------------------------------------------------
# Matplotlib plot color sequences  (not Qt-related — kept here)
# ---------------------------------------------------------------------------

color_list = [
    'b', 'r', 'g', 'm', 'k', 'c', 'orange', 'midnightblue',
    'maroon', 'springgreen', 'purple', 'dimgrey', 'teal',
    'yellow', 'thistle', 'lime', 'darkgoldenrod', 'rosybrown',
    'lightcoral', 'darkred', 'teal', 'navy', 'mediumslateblue',
    'khaki', 'indigo', 'palevioletred', 'yellowgreen',
    'palegreen', 'olivedrab', 'tomato',
]

color_list_rev = list(reversed(color_list))

# ---------------------------------------------------------------------------
# Re-export everything from ui_theme so that
#   ``from ui_constants import *``
# in tabs / widgets continues to work without modification.
# ---------------------------------------------------------------------------
from ui_theme import (  # noqa: E402, F401 — intentional star-like re-export
    # Layout / spacing
    PROGRESS_BAR_H_SIZE,
    PUSH_BTN_H_SIZE,
    PUSH_BTN_V_SIZE,
    LEDIT_BTN_H_SIZE,
    LEDIT_BTN_PATH_H_SIZE,
    LABEL_PATH_H_SIZE,
    LEDIT_BTN_V_SIZE,
    H_LAYOUT_SPACING,
    V_LAYOUT_SPACING,
    GRID_LAYOUT_SPACING,
    PARSE_PROT_TABLE_ROWS,
    STATS_TABLE_ROWS,
    LIM_GROUPS_TABLE_ROWS,
    V_LINE_WIDTH,
    H_LINE_HEIGHT,
    MARGINS_MAIN,
    MARGINS_TAB,
    MARGINS_GROUPBOX,
    MAX_LOG_ROWS,
    # Window chrome
    WINDOW_TITLE,
    WINDOW_MIN_W,
    WINDOW_MIN_H,
    WINDOW_DEF_W,
    WINDOW_DEF_H,
    # Style strings
    QSS,
    THEME_QSS,
    antPatTableStyle,
    slideSymbolStyle,
    plotFrameStyle,
    lineStyle,
    dialogLEditErrorStyle,
    dialogLEditCorrectStyle,
    dialogLabelErrorStyle,
    dialogLabelCorrectStyle,
    # Color palette (available to any consumer)
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BG_ALT_ROW,
    BG_HOVER, BG_SELECTION,
    ACCENT, ACCENT_HOVER, ACCENT_PRESSED, ACCENT_DISABLED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DISABLED, TEXT_ON_ACCENT, TEXT_HEADER,
    BORDER, BORDER_FOCUS, BORDER_HOVER,
    COLOR_INFO, COLOR_DEBUG, COLOR_WARNING, COLOR_ERROR, COLOR_CRITICAL,
    COLOR_INFO_BG, COLOR_DEBUG_BG, COLOR_WARNING_BG,
    COLOR_ERROR_BG, COLOR_CRITICAL_BG,
    LOG_LEVEL_BG_COLORS, LOG_LEVEL_FG_COLORS,
    # Public API
    apply_theme,
    configure_hidpi,
    dpi_scale,
)

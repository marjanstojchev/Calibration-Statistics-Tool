"""ui/ui_theme.py — Professional dark-navy theme for the Calibration Statistics Tool.

Design aesthetic: Deep navy / charcoal engineering tool, inspired by JetBrains IDE
dark themes (Darcula / New UI) and the Fusion dark style.  All values are pure
Python primitives — no Qt objects — so this module is safe to import *before*
QApplication is created.

Typical usage in ``MainView.__init__()``:

    from ui_theme import apply_theme, WINDOW_TITLE, WINDOW_MIN_W, WINDOW_MIN_H

    apply_theme(self.app)                          # global QSS cascade
    self.mainWidget.setWindowTitle(WINDOW_TITLE)
    self.mainWidget.setMinimumSize(WINDOW_MIN_W, WINDOW_MIN_H)
"""
from __future__ import annotations

# ============================================================================
# § 1  COLOR PALETTE
# ============================================================================
# ---------- Backgrounds ------------------------------------------------------
BG_PRIMARY       = "#1a1f2e"   # Deep navy — root window / tab content area
BG_SECONDARY     = "#232b3e"   # Panel / frame surfaces
BG_TERTIARY      = "#2b3450"   # GroupBox interior, QLineEdit, QComboBox fields
BG_ALT_ROW       = "#1e2840"   # Alternating table-row (even darker stripe)
BG_HOVER         = "#2e3d58"   # General hover highlight
BG_SELECTION     = "#1a4680"   # Selected row / item (deep blue)

# ---------- Accent (interactive) ---------------------------------------------
ACCENT           = "#3d8ef0"   # Primary accent — active tab, focus ring, btn
ACCENT_HOVER     = "#5da5ff"   # Hovered accent
ACCENT_PRESSED   = "#2d6fcc"   # Pressed / active accent
ACCENT_DISABLED  = "#1e3a60"   # Disabled accent state

# ---------- Text -------------------------------------------------------------
TEXT_PRIMARY     = "#d6e4f7"   # High-contrast main text
TEXT_SECONDARY   = "#7a98be"   # Subdued / hint / label text
TEXT_DISABLED    = "#3d526e"   # Disabled state text
TEXT_ON_ACCENT   = "#ffffff"   # Text placed on accent-coloured surfaces
TEXT_HEADER      = "#9bbbd8"   # Table / GroupBox header labels

# ---------- Borders ----------------------------------------------------------
BORDER           = "#374a6a"   # Default widget border
BORDER_FOCUS     = "#3d8ef0"   # Focused widget border (matches ACCENT)
BORDER_HOVER     = "#4d6488"   # Hovered widget border

# ---------- Semantic / Status ------------------------------------------------
COLOR_INFO       = "#b8d4f5"   # INFO log — soft sky-blue text
COLOR_DEBUG      = "#7ab2f0"   # DEBUG log — medium blue text
COLOR_WARNING    = "#f5a623"   # WARNING log — amber text
COLOR_ERROR      = "#ff6b6b"   # ERROR log — rose-red text
COLOR_CRITICAL   = "#ff2d2d"   # CRITICAL log — bright red text

COLOR_INFO_BG    = "#1a2a42"   # INFO row background tint
COLOR_DEBUG_BG   = "#1a2a42"   # DEBUG row background tint
COLOR_WARNING_BG = "#3a2806"   # WARNING row amber tint
COLOR_ERROR_BG   = "#3a0c0c"   # ERROR row red tint
COLOR_CRITICAL_BG = "#560808"  # CRITICAL row deep-red tint

# ---------- Tab bar ----------------------------------------------------------
TAB_ACTIVE_BG    = "#2b3a58"   # Active tab pill
TAB_INACTIVE_BG  = "#1a1f2e"   # Inactive tab
TAB_HOVER_BG     = "#232e48"   # Hovered inactive tab
TAB_ACTIVE_TEXT  = "#d6e4f7"   # Active tab label
TAB_INACTIVE_TEXT = "#6a8ab0"  # Inactive tab label

# ---------- Scrollbar --------------------------------------------------------
SCROLLBAR_TRACK        = "#1a1f2e"
SCROLLBAR_HANDLE       = "#374a6a"
SCROLLBAR_HANDLE_HOVER = "#4d6890"

# ============================================================================
# § 2  LAYOUT / SPACING CONSTANTS  (replaces legacy ui_constants values)
# ============================================================================
PROGRESS_BAR_H_SIZE    = 260
PUSH_BTN_H_SIZE        = 128   # Horizontal min for fixed-size buttons
PUSH_BTN_V_SIZE        = 28    # Vertical size for fixed-size buttons
LEDIT_BTN_H_SIZE       = 112   # Small line-edit
LEDIT_BTN_PATH_H_SIZE  = 300   # Wide path line-edit
LABEL_PATH_H_SIZE      = 340   # Path-label display width
LEDIT_BTN_V_SIZE       = 24    # Line-edit vertical size
H_LAYOUT_SPACING       = 10
V_LAYOUT_SPACING       = 10
GRID_LAYOUT_SPACING    = 10
PARSE_PROT_TABLE_ROWS  = 20
STATS_TABLE_ROWS       = 7
LIM_GROUPS_TABLE_ROWS  = 10
V_LINE_WIDTH           = 1
H_LINE_HEIGHT          = 1

# Uniform content margins (left, top, right, bottom)
MARGINS_MAIN           = (10, 10, 10, 10)
MARGINS_TAB            = (8, 8, 8, 8)
MARGINS_GROUPBOX       = (8, 18, 8, 8)

# ============================================================================
# § 3  WINDOW CHROME
# ============================================================================
WINDOW_TITLE   = "Calibration Statistics Tool"
WINDOW_MIN_W   = 1280
WINDOW_MIN_H   = 800
WINDOW_DEF_W   = 1440
WINDOW_DEF_H   = 900

# ============================================================================
# § 4  PER-WIDGET INLINE STYLE STRINGS
#      (compatible drop-ins for the legacy ui_constants style variables)
# ============================================================================

antPatTableStyle = f"""
QFrame#Frame {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
QFrame#SubFrame1 {{
    background-color: {BG_SECONDARY};
    border: none;
    border-radius: 6px;
}}
QFrame#SubFrame2 {{
    background-color: {BG_TERTIARY};
    border: none;
    border-radius: 6px;
}}
"""

slideSymbolStyle = f"""
QFrame {{
    background-color: {BG_TERTIARY};
    border: 1px solid {BORDER};
    border-radius: 5px;
}}
"""

plotFrameStyle = f"""
QFrame#PlotFrame {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background-color: {BG_SECONDARY};
}}
"""

lineStyle = f"""
QFrame {{
    background-color: {BORDER};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}
"""

# Dialog validation field styles
dialogLEditErrorStyle = f"""
QLineEdit {{
    border: 1px solid {COLOR_ERROR};
    background-color: {COLOR_ERROR_BG};
}}
"""

dialogLEditCorrectStyle = f"""
QLineEdit {{
    border: 1px solid {BORDER};
    background-color: {BG_TERTIARY};
}}
"""

dialogLabelErrorStyle = f"""
QLabel {{
    color: {COLOR_ERROR};
}}
"""

dialogLabelCorrectStyle = f"""
QLabel {{
    color: {TEXT_PRIMARY};
}}
"""

# ============================================================================
# § 5  LOG LEVEL COLOR MAPS  (consumed by QTableLogHandler in widgets.py)
# ============================================================================

LOG_LEVEL_BG_COLORS: dict[str, str] = {
    "NOTSET":   BG_SECONDARY,
    "DEBUG":    COLOR_DEBUG_BG,
    "INFO":     COLOR_INFO_BG,
    "WARNING":  COLOR_WARNING_BG,
    "ERROR":    COLOR_ERROR_BG,
    "CRITICAL": COLOR_CRITICAL_BG,
}

LOG_LEVEL_FG_COLORS: dict[str, str] = {
    "NOTSET":   TEXT_SECONDARY,
    "DEBUG":    COLOR_DEBUG,
    "INFO":     COLOR_INFO,
    "WARNING":  COLOR_WARNING,
    "ERROR":    COLOR_ERROR,
    "CRITICAL": COLOR_CRITICAL,
}

# ============================================================================
# § 6  COMPREHENSIVE QSS STYLESHEET
# ============================================================================

THEME_QSS = f"""
/* =========================================================================
   CALIBRATION STATISTICS TOOL — Professional Dark Theme
   Palette: Deep Navy / Charcoal  ·  Accent: Engineering Blue
   Inspired by: JetBrains Darcula · Fusion Dark · VS Code Dark+
   ========================================================================= */

/* ── Global reset ──────────────────────────────────────────────────────── */
* {{
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
    font-size: 9pt;
    color: {TEXT_PRIMARY};
    outline: none;
    box-sizing: border-box;
}}

/* ── Root widget & main window ─────────────────────────────────────────── */
QMainWindow,
QWidget {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
}}

/* ── Modal dialogs ─────────────────────────────────────────────────────── */
QDialog {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
}}

/* =========================================================================
   TAB WIDGET
   ========================================================================= */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-top: 2px solid {ACCENT};
    background-color: {BG_PRIMARY};
    top: -1px;
}}

QTabWidget::tab-bar {{
    alignment: left;
}}

QTabBar::tab {{
    background-color: {TAB_INACTIVE_BG};
    color: {TAB_INACTIVE_TEXT};
    border: 1px solid {BORDER};
    border-bottom: none;
    padding: 6px 18px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 118px;
}}

QTabBar::tab:hover:!selected {{
    background-color: {TAB_HOVER_BG};
    color: {TEXT_PRIMARY};
    border-color: {BORDER_HOVER};
}}

QTabBar::tab:selected {{
    background-color: {TAB_ACTIVE_BG};
    color: {TAB_ACTIVE_TEXT};
    border-color: {ACCENT};
    border-bottom: 2px solid {TAB_ACTIVE_BG};
    font-weight: bold;
    padding-bottom: 7px;
}}

/* Tab scroll buttons (shown when there are too many tabs) */
QTabBar::scroller {{
    width: 20px;
}}
QTabBar QToolButton {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 3px;
    color: {TEXT_SECONDARY};
}}
QTabBar QToolButton:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

/* =========================================================================
   PUSH BUTTONS
   ========================================================================= */
QPushButton {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 14px;
    min-height: 24px;
    min-width: 72px;
}}

QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: {BORDER_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton:pressed {{
    background-color: {ACCENT_PRESSED};
    border-color: {ACCENT};
    color: {TEXT_ON_ACCENT};
    padding-top: 5px;
    padding-bottom: 3px;
}}

QPushButton:disabled {{
    background-color: {BG_PRIMARY};
    border-color: {BORDER};
    color: {TEXT_DISABLED};
}}

QPushButton:checked {{
    background-color: {ACCENT_PRESSED};
    border-color: {ACCENT};
    color: {TEXT_ON_ACCENT};
}}

/* Primary action variant — set property role="primary" on the widget */
QPushButton[role="primary"] {{
    background-color: {ACCENT};
    color: {TEXT_ON_ACCENT};
    border: none;
    font-weight: bold;
}}
QPushButton[role="primary"]:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton[role="primary"]:pressed {{
    background-color: {ACCENT_PRESSED};
}}
QPushButton[role="primary"]:disabled {{
    background-color: {ACCENT_DISABLED};
    color: {TEXT_DISABLED};
}}

/* =========================================================================
   LINE EDITS
   ========================================================================= */
QLineEdit {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 2px 7px;
    min-height: 22px;
    selection-background-color: {BG_SELECTION};
    selection-color: {TEXT_PRIMARY};
}}

QLineEdit:focus {{
    border-color: {BORDER_FOCUS};
    background-color: {BG_SECONDARY};
}}

QLineEdit:disabled {{
    background-color: {BG_PRIMARY};
    color: {TEXT_DISABLED};
    border-color: {BORDER};
}}

QLineEdit:read-only {{
    background-color: {BG_SECONDARY};
    color: {TEXT_SECONDARY};
    border-color: {BORDER};
}}

/* =========================================================================
   COMBO BOX
   ========================================================================= */
QComboBox {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 2px 7px;
    min-height: 22px;
    selection-background-color: {BG_SELECTION};
}}

QComboBox:hover {{
    border-color: {BORDER_HOVER};
}}

QComboBox:focus {{
    border-color: {BORDER_FOCUS};
}}

QComboBox:disabled {{
    background-color: {BG_PRIMARY};
    color: {TEXT_DISABLED};
    border-color: {BORDER};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid {BORDER};
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    background-color: {BG_SECONDARY};
}}

QComboBox::down-arrow {{
    width: 8px;
    height: 8px;
    border-left:   4px solid transparent;
    border-right:  4px solid transparent;
    border-top:    5px solid {TEXT_SECONDARY};
    margin-right:  3px;
}}

QComboBox::down-arrow:hover {{
    border-top-color: {TEXT_PRIMARY};
}}

QComboBox QAbstractItemView {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    selection-background-color: {BG_SELECTION};
    selection-color: {TEXT_PRIMARY};
    outline: none;
    padding: 2px;
}}

/* =========================================================================
   LABELS
   ========================================================================= */
QLabel {{
    color: {TEXT_PRIMARY};
    background-color: transparent;
    padding: 1px 0px;
}}

QLabel:disabled {{
    color: {TEXT_DISABLED};
}}

/* =========================================================================
   GROUP BOX
   ========================================================================= */
QGroupBox {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 5px;
    margin-top: 16px;
    padding-top: 6px;
    color: {TEXT_HEADER};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: -1px;
    padding: 2px 8px;
    background-color: {BG_SECONDARY};
    color: {ACCENT};
    border-radius: 3px;
    font-size: 8pt;
    font-weight: bold;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}

/* =========================================================================
   CHECK BOXES
   ========================================================================= */
QCheckBox {{
    color: {TEXT_PRIMARY};
    spacing: 7px;
    background-color: transparent;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background-color: {BG_TERTIARY};
}}

QCheckBox::indicator:hover {{
    border-color: {BORDER_HOVER};
    background-color: {BG_HOVER};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}

QCheckBox::indicator:checked:hover {{
    background-color: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}

QCheckBox::indicator:indeterminate {{
    background-color: {ACCENT_DISABLED};
    border-color: {ACCENT};
}}

QCheckBox:disabled {{
    color: {TEXT_DISABLED};
}}

QCheckBox::indicator:disabled {{
    background-color: {BG_PRIMARY};
    border-color: {BORDER};
}}

/* =========================================================================
   RADIO BUTTONS
   ========================================================================= */
QRadioButton {{
    color: {TEXT_PRIMARY};
    spacing: 7px;
    background-color: transparent;
}}

QRadioButton::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {BORDER};
    border-radius: 7px;
    background-color: {BG_TERTIARY};
}}

QRadioButton::indicator:hover {{
    border-color: {BORDER_HOVER};
    background-color: {BG_HOVER};
}}

QRadioButton::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}

QRadioButton::indicator:checked:hover {{
    background-color: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}

QRadioButton:disabled {{
    color: {TEXT_DISABLED};
}}

QRadioButton::indicator:disabled {{
    background-color: {BG_PRIMARY};
    border-color: {BORDER};
}}

/* =========================================================================
   PROGRESS BAR
   ========================================================================= */
QProgressBar {{
    background-color: {BG_TERTIARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT_PRIMARY};
    font-weight: bold;
    font-size: 8pt;
    min-height: 18px;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0.0 {ACCENT_PRESSED},
        stop: 0.6 {ACCENT},
        stop: 1.0 {ACCENT_HOVER}
    );
    border-radius: 3px;
    margin: 1px;
}}

/* =========================================================================
   TABLE WIDGET
   ========================================================================= */
QTableWidget {{
    background-color: {BG_SECONDARY};
    alternate-background-color: {BG_ALT_ROW};
    color: {TEXT_PRIMARY};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 4px;
    selection-background-color: {BG_SELECTION};
    selection-color: {TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 3px 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {BG_SELECTION};
    color: {TEXT_PRIMARY};
}}

QTableWidget::item:hover:!selected {{
    background-color: {BG_HOVER};
}}

/* ── Table header ───────────────────────────────────────────────────────── */
QHeaderView {{
    background-color: {BG_TERTIARY};
    color: {TEXT_HEADER};
    border: none;
}}

QHeaderView::section {{
    background-color: {BG_TERTIARY};
    color: {TEXT_HEADER};
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 2px solid {ACCENT};
    padding: 5px 9px;
    font-weight: bold;
    font-size: 8pt;
    letter-spacing: 0.2px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 4px;
}}

QHeaderView::section:last {{
    border-right: none;
    border-top-right-radius: 4px;
}}

QHeaderView::section:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QHeaderView::section:checked {{
    background-color: {ACCENT_PRESSED};
    color: {TEXT_ON_ACCENT};
}}

QHeaderView::section:vertical {{
    border-right: 2px solid {ACCENT};
    border-bottom: 1px solid {BORDER};
}}

/* Corner button (top-left overlap of header and vertical header) */
QTableCornerButton::section {{
    background-color: {BG_TERTIARY};
    border: 1px solid {BORDER};
    border-top-left-radius: 4px;
}}

/* =========================================================================
   SCROLL BARS
   ========================================================================= */
QScrollBar:vertical {{
    background-color: {SCROLLBAR_TRACK};
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {SCROLLBAR_HANDLE};
    min-height: 28px;
    border-radius: 5px;
    margin: 1px 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {SCROLLBAR_HANDLE_HOVER};
}}

QScrollBar::handle:vertical:pressed {{
    background-color: {ACCENT};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {SCROLLBAR_TRACK};
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {SCROLLBAR_HANDLE};
    min-width: 28px;
    border-radius: 5px;
    margin: 2px 1px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {SCROLLBAR_HANDLE_HOVER};
}}

QScrollBar::handle:horizontal:pressed {{
    background-color: {ACCENT};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
    background: none;
}}

/* =========================================================================
   FRAMES  (bare QFrames: transparent by default, only separators get color)
   ========================================================================= */
QFrame {{
    border: none;
    background-color: transparent;
}}

/* Horizontal / Vertical separator lines */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    background-color: {BORDER};
    border: none;
    max-width:  1px;
    max-height: 1px;
}}

/* =========================================================================
   TOOL TIP
   ========================================================================= */
QToolTip {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_FOCUS};
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 8pt;
    opacity: 230;
}}

/* =========================================================================
   STATUS BAR  (bottom chrome strip)
   ========================================================================= */
QStatusBar {{
    background-color: {BG_TERTIARY};
    color: {TEXT_SECONDARY};
    border-top: 1px solid {BORDER};
    font-size: 8pt;
    padding: 2px 6px;
}}

QStatusBar::item {{
    border: none;
}}

QStatusBar QLabel {{
    color: {TEXT_SECONDARY};
    font-size: 8pt;
    padding: 0px 4px;
}}

/* =========================================================================
   SPLITTER
   ========================================================================= */
QSplitter::handle {{
    background-color: {BORDER};
}}

QSplitter::handle:hover {{
    background-color: {ACCENT};
}}

QSplitter::handle:horizontal {{
    width: 3px;
}}

QSplitter::handle:vertical {{
    height: 3px;
}}

/* =========================================================================
   DIALOG BUTTON BOX
   ========================================================================= */
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}

/* =========================================================================
   MENU BAR  (prepared for future menu bar addition)
   ========================================================================= */
QMenuBar {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {BORDER};
    padding: 2px 4px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 4px 12px;
    border-radius: 3px;
}}

QMenuBar::item:selected {{
    background-color: {BG_HOVER};
}}

QMenu {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    padding: 4px 0px;
    border-radius: 4px;
}}

QMenu::item {{
    padding: 5px 28px 5px 14px;
    border-radius: 3px;
}}

QMenu::item:selected {{
    background-color: {BG_SELECTION};
}}

QMenu::separator {{
    height: 1px;
    background: {BORDER};
    margin: 3px 10px;
}}

/* =========================================================================
   TOOL BAR  (prepared for potential future toolbar)
   ========================================================================= */
QToolBar {{
    background-color: {BG_SECONDARY};
    border-bottom: 1px solid {BORDER};
    spacing: 4px;
    padding: 2px;
}}

QToolBar QToolButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    color: {TEXT_PRIMARY};
    padding: 4px 8px;
}}

QToolBar QToolButton:hover {{
    background-color: {BG_HOVER};
    border-color: {BORDER_HOVER};
}}

QToolBar QToolButton:pressed {{
    background-color: {ACCENT_PRESSED};
    border-color: {ACCENT};
    color: {TEXT_ON_ACCENT};
}}

/* =========================================================================
   MATPLOTLIB NAVIGATION TOOLBAR  (embedded in PlotFrame / PlotFrameSysDia)
   ========================================================================= */
NavigationToolbar2QT {{
    background-color: {BG_SECONDARY};
    border-top: 1px solid {BORDER};
    spacing: 2px;
}}

NavigationToolbar2QT QToolButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    color: {TEXT_SECONDARY};
    padding: 3px 5px;
}}

NavigationToolbar2QT QToolButton:hover {{
    background-color: {BG_HOVER};
    border-color: {BORDER_HOVER};
    color: {TEXT_PRIMARY};
}}

NavigationToolbar2QT QToolButton:checked {{
    background-color: {ACCENT_PRESSED};
    border-color: {ACCENT};
    color: {TEXT_ON_ACCENT};
}}
"""

# ============================================================================
# § 7  PUBLIC API
# ============================================================================

def apply_theme(app) -> None:
    """Apply the global THEME_QSS stylesheet to a QApplication instance.

    Call this immediately after ``QApplication`` is created — before any
    widgets are shown.  The stylesheet cascades automatically to all child
    widgets.

    Args:
        app: The ``QApplication`` instance (``self.app`` inside MainView).
    """
    app.setStyleSheet(THEME_QSS)


# Backward-compat alias so ``from ui_theme import QSS`` still works if needed
QSS = THEME_QSS

"""PST-60: Shared UI constants and style strings.

Pure-Python values only — no Qt objects — so this module is safe to import
before QApplication is created.
"""

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
# Style sheets
# ---------------------------------------------------------------------------

QSS = '''
 QTabWidget{
 background-color: cyan;
}
.QPushButton{
    background-color: cyan;
    margin: 0px;
    padding: 0px;

}

'''

antPatTableStyle = '''
.QFrame#Frame {
    background-color: white;
    border-style: solid;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;


}
.QFrame#SubFrame1 {
    background-color: white;
    border-style: none;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;


}

.QFrame#SubFrame2 {
    background-color: lavender;
    border-style: none;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;


}
'''

slideSymbolStyle = '''
.QFrame{
    background-color: lavender;
    border-style: solid;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;


}

'''

plotFrameStyle = '''
.PlotFrame#PlotFrame{
    border-style: solid;
    border-color: grey;
    border-width: 2px;
    border-radius: 10px;

}

'''

lineStyle = '''
.QFrame{
   /* background-color: silver; */
   background-color: lightgrey;

}
'''

# ---------------------------------------------------------------------------
# Size / spacing constants
# ---------------------------------------------------------------------------

PROGRESS_BAR_H_SIZE   = 250
PUSH_BTN_H_SIZE       = 120
PUSH_BTN_V_SIZE       = 30
LEDIT_BTN_H_SIZE      = 100
LEDIT_BTN_PATH_H_SIZE = 280
LABEL_PATH_H_SIZE     = 320
LEDIT_BTN_V_SIZE      = 20
H_LAYOUT_SPACING      = 12
V_LAYOUT_SPACING      = 12
GRID_LAYOUT_SPACING   = 12
PARSE_PROT_TABLE_ROWS = 20
STATS_TABLE_ROWS      = 7
LIM_GROUPS_TABLE_ROWS = 10
V_LINE_WIDTH          = 1
H_LINE_HEIGHT         = 1

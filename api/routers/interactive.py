"""System Diagrams Interactive tab — REST API router.

The desktop tab renders interactive matplotlib plots inside a Qt window.
For the web UI the same underlying data is exposed as JSON so any JS
charting library (Chart.js, Plotly, etc.) can render it client-side.

Workflow
--------
1. POST /fill   – reads parsed PTU2 data and returns available protocols
                  and parameter combinations (antenna type × graph type ×
                  diagram × RX channel).
2. GET  /state  – returns the last fill result without re-computing.
3. DELETE /clear – resets the fill state.

Note: the On/Off toggle and live-plot-update from the desktop tab require
the full Qt signal pipeline and matplotlib figure objects.  Those are not
supported here.  Instead, the web UI fetches the full parameter list and
renders selected series directly in the browser.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

# Module-level fill state
_fill_state: Dict[str, Any] = {
    "filled": False,
    "protocol_count": 0,
    "parameter_count": 0,
    "protocols": [],
    "parameters": [],
}

# Graph types exposed in the interactive table (matches graphInterList in the module)
_GRAPH_TYPES = [
    "level",
    "avgLevel",
    "normLevel",
    "avgNormLevel",
    "phaseDiff",
    "avgPhaseDiff",
    "diffPhaseDiff",
    "corrPhaseDiff",
]


@router.get("/state")
def get_state():
    """Return the current fill state (result of the last POST /fill)."""
    return _fill_state


@router.post("/fill")
def fill():
    """Populate interactive table data from already-parsed PTU2 data.

    Returns the list of unique protocols (date/tuner/sensor) and all
    available parameter combinations (antenna type × graph type × diagram
    number × RX channel) so the web UI can build its selection tables.

    Requires /api/protocols/parse to have been called first.
    """
    from shared import data_processing as dp
    import shared.load_protocols as lp

    parsed_data = getattr(lp, 'sysDiagParsedDataList', [])
    if not parsed_data:
        raise HTTPException(status_code=422, detail="No parsed data. Run /api/protocols/parse first.")

    antenna_types: List[int] = dp.getAntennaTypesList(parsed_data)
    if not antenna_types:
        raise HTTPException(status_code=422, detail="No antenna types found in parsed data.")

    # ---- Protocols (unique date/tuner/sensor rows, same as the Protocol table) ----
    protocols: List[Dict[str, str]] = []
    seen: set = set()
    for ant_type in antenna_types:
        ptu2_list = dp.getPtu2ListPerAntennaType(ant_type, parsed_data)
        for ptu2 in ptu2_list:
            key = (
                str(ptu2.fileTitle.dateAndTime),
                str(ptu2.fileTitle.tuner),
                str(ptu2.fileTitle.sensor),
            )
            if key not in seen:
                seen.add(key)
                protocols.append({
                    "date_time": key[0],
                    "tuner":     key[1],
                    "sensor":    key[2],
                    "label":     f"{key[0]}_{key[1]}_{key[2]}",
                })

    # ---- Parameters (graph type × diagram × RX channel) ----
    nof_rx_ch: int = parsed_data[0].antennaInfo.nofAntennas if parsed_data else 1

    parameters: List[Dict[str, Any]] = []
    for ant_type in antenna_types:
        diagram_list: List[int] = dp.getDiagramList(ant_type, parsed_data)
        for graph_type in _GRAPH_TYPES:
            for diag_num in diagram_list:
                for rx_ch in range(nof_rx_ch):
                    parameters.append({
                        "antenna_type": ant_type,
                        "graph_type":   graph_type,
                        "diagram_num":  diag_num,
                        "rx_channel":   rx_ch,
                        "label": f"{graph_type}_AntType{ant_type}_Diag{diag_num}_RxCh{rx_ch}",
                    })

    _fill_state.update({
        "filled":          True,
        "protocol_count":  len(protocols),
        "parameter_count": len(parameters),
        "protocols":       protocols,
        "parameters":      parameters,
    })

    return _fill_state


@router.delete("/clear")
def clear():
    """Clear the interactive fill state."""
    _fill_state.update({
        "filled":          False,
        "protocol_count":  0,
        "parameter_count": 0,
        "protocols":       [],
        "parameters":      [],
    })
    return {"status": "cleared"}

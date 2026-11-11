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
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from api.session import NO_DATA_MESSAGE, Session, exclusive, get_session

router = APIRouter()


def _empty_state() -> Dict[str, Any]:
    return {
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
def get_state(session: Session = Depends(get_session)):
    """Return the current fill state (result of the last POST /fill)."""
    return session.state.get("interactive") or _empty_state()


@router.post("/fill")
def fill(session: Session = Depends(get_session)):
    """Populate interactive table data from the PTU2 data loaded in this session.

    Returns the list of unique protocols (date/tuner/sensor) and all
    available parameter combinations (antenna type × graph type × diagram
    number × RX channel) so the web UI can build its selection tables.
    """
    from shared import data_processing as dp

    with exclusive(session, "interactive"):
        parsed_data = session.sys_diag_list
        if not parsed_data:
            raise HTTPException(status_code=422, detail=NO_DATA_MESSAGE)

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

        state = {
            "filled":          True,
            "protocol_count":  len(protocols),
            "parameter_count": len(parameters),
            "protocols":       protocols,
            "parameters":      parameters,
        }
        session.state["interactive"] = state
        return state


@router.delete("/clear")
def clear(session: Session = Depends(get_session)):
    """Clear the interactive fill state."""
    with exclusive(session, "interactive"):
        session.state["interactive"] = _empty_state()
    return {"status": "cleared"}

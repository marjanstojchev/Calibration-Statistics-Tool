from fastapi import APIRouter
import shared.load_protocols as lp

router = APIRouter()


@router.get("/")
def get_protocol_stats():
    """Return counts of parsed protocols and PTU2 files currently in memory."""
    parsed = getattr(lp, 'sysDiagParsedDataList', [])
    tx_parsed = getattr(lp, 'txAntDiagParsedDataList', [])
    return {
        "sys_diag_ptu2_loaded": len(parsed),
        "tx_ant_diag_loaded": len(tx_parsed),
    }


@router.delete("/clear")
def clear_stats():
    """Alias for DELETE /api/protocols/clear for backwards compatibility.

    The desktop UI has both 'Clear Data' (Parse Protocols tab) and
    'Clear Statistics Data' (Statistics tab) buttons. In the API,
    clearing parsed data also clears statistics, so both map to the same action.
    """
    lp.sysDiagParsedDataList = []
    lp.txAntDiagParsedDataList = []
    return {
        "status": "cleared",
        "sys_diag_ptu2_loaded": 0,
        "tx_ant_diag_loaded": 0,
    }
from fastapi import APIRouter, Depends

from api.routers.protocols import _clear
from api.session import Session, get_session

router = APIRouter()


@router.get("/")
def get_protocol_stats(session: Session = Depends(get_session)):
    """Return counts of the protocols and PTU2 / TxAnt files loaded in this session."""
    return {
        "protocols_loaded": len(session.protocol_paths),
        "sys_diag_ptu2_loaded": len(session.sys_diag_list),
        "tx_ant_diag_loaded": len(session.tx_diag_list),
    }


@router.delete("/clear")
def clear_stats(session: Session = Depends(get_session)):
    """Alias for DELETE /api/protocols/clear for backwards compatibility.

    The desktop UI has both 'Clear Data' (Parse Protocols tab) and
    'Clear Statistics Data' (Statistics tab) buttons. In the API,
    clearing parsed data also clears statistics, so both map to the same action.
    """
    _clear(session)
    return {
        "status": "cleared",
        "sys_diag_ptu2_loaded": 0,
        "tx_ant_diag_loaded": 0,
    }

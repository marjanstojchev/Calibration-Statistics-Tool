from fastapi import APIRouter, Depends

from api.session import Session, get_session, store

router = APIRouter()


@router.get("")
def session_info(session: Session = Depends(get_session)):
    """State of the caller's session: loaded file counts and the running operation (if any)."""
    return session.summary()


@router.delete("")
def delete_session(session: Session = Depends(get_session)):
    """Delete the caller's whole workspace (uploads, outputs, logs). Refused with 409 while an operation runs."""
    store.delete(session.id)
    return {"status": "deleted"}

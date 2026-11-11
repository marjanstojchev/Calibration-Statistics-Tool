from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import asyncio
import logging

import logconfig
from api.session import LOG_KINDS, Session, emit_active_log, get_session

router = APIRouter()


class StreamLogHandler(logging.Handler):
    """Hands every record to the session that currently owns the engine."""

    def __init__(self, kind: str):
        super().__init__()
        self.kind = kind

    def emit(self, record):
        try:
            emit_active_log(self.kind, self.format(record))
        except Exception:
            self.handleError(record)


for _kind, _logger in (
    ("system_diagrams", logconfig.antSysDiagLogger),
    ("tx_diagrams", logconfig.txAntDiagLogger),
    ("antenna_patterns", logconfig.antPatLogger),
    ("main_load_data", logconfig.mainLoadDataLogger),
):
    _handler = StreamLogHandler(_kind)
    _handler.setFormatter(logconfig.logFormatter)
    _logger.logger.addHandler(_handler)


async def log_stream_generator(session: Session, kind: str):
    """Generate Server-Sent Events from the log buffer of one session."""
    last_total = 0
    while True:
        session.touch()
        total = session.log_totals[kind]
        if total > last_total:
            buffer = list(session.log_buffers[kind])
            # Lines that already rotated out of the buffer cannot be sent anymore
            new_count = min(total - last_total, len(buffer))
            for line in buffer[len(buffer) - new_count:]:
                # SSE data must stay on one line; a multi-line message would end the event early
                yield "".join(f"data: {part}\n" for part in line.splitlines() or [""]) + "\n"
            last_total = total
        await asyncio.sleep(0.5)  # Poll interval


def _stream(session: Session, kind: str) -> StreamingResponse:
    return StreamingResponse(log_stream_generator(session, kind), media_type="text/event-stream")


@router.get("/stream/system-diagrams")
async def stream_system_diagrams_logs(session: Session = Depends(get_session)):
    """Stream Antenna System Diagrams logs in real-time (SSE)."""
    return _stream(session, "system_diagrams")


@router.get("/stream/tx-diagrams")
async def stream_tx_diagrams_logs(session: Session = Depends(get_session)):
    """Stream TX Antenna Diagrams logs in real-time (SSE)."""
    return _stream(session, "tx_diagrams")


@router.get("/stream/antenna-patterns")
async def stream_antenna_patterns_logs(session: Session = Depends(get_session)):
    """Stream Antenna Patterns logs in real-time (SSE)."""
    return _stream(session, "antenna_patterns")


@router.get("/stream/main-load-data")
async def stream_main_load_data_logs(session: Session = Depends(get_session)):
    """Stream Main Load Data parser logs in real-time (SSE)."""
    return _stream(session, "main_load_data")


@router.get("/system-diagrams")
def get_system_diagrams_logs(session: Session = Depends(get_session)):
    """Get buffered Antenna System Diagrams logs."""
    return list(session.log_buffers["system_diagrams"])


@router.get("/tx-diagrams")
def get_tx_diagrams_logs(session: Session = Depends(get_session)):
    """Get buffered TX Antenna Diagrams logs."""
    return list(session.log_buffers["tx_diagrams"])


@router.get("/antenna-patterns")
def get_antenna_patterns_logs(session: Session = Depends(get_session)):
    """Get buffered Antenna Patterns logs."""
    return list(session.log_buffers["antenna_patterns"])


@router.get("/main-load-data")
def get_main_load_data_logs(session: Session = Depends(get_session)):
    """Get buffered Main Load Data parser logs."""
    return list(session.log_buffers["main_load_data"])


@router.get("/all")
def get_all_logs(session: Session = Depends(get_session)):
    """Get all buffered logs of this session."""
    return {kind: list(session.log_buffers[kind]) for kind in LOG_KINDS}

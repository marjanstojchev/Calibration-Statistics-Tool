from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import logconfig
import os
import asyncio
import logging
from collections import deque
from typing import Dict

router = APIRouter()

# In-memory log buffers per logger (thread-safe deque)
log_buffers: Dict[str, deque] = {
    "system_diagrams": deque(maxlen=1000),
    "tx_diagrams": deque(maxlen=1000),
    "antenna_patterns": deque(maxlen=1000),
    "main_load_data": deque(maxlen=1000)
}


class StreamLogHandler(logging.Handler):
    """Custom handler that captures logs to in-memory buffer."""
    def __init__(self, buffer_name: str):
        super().__init__()
        self.buffer_name = buffer_name
    
    def emit(self, record):
        try:
            msg = self.format(record)
            log_buffers[self.buffer_name].append(msg)
        except Exception:
            self.handleError(record)


# Attach stream handlers to all loggers
stream_handlers = {
    "system_diagrams": StreamLogHandler("system_diagrams"),
    "tx_diagrams": StreamLogHandler("tx_diagrams"),
    "antenna_patterns": StreamLogHandler("antenna_patterns"),
    "main_load_data": StreamLogHandler("main_load_data")
}

for name, handler in stream_handlers.items():
    handler.setFormatter(logconfig.logFormatter)

logconfig.antSysDiagLogger.logger.addHandler(stream_handlers["system_diagrams"])
logconfig.txAntDiagLogger.logger.addHandler(stream_handlers["tx_diagrams"])
logconfig.antPatLogger.logger.addHandler(stream_handlers["antenna_patterns"])
logconfig.mainLoadDataLogger.logger.addHandler(stream_handlers["main_load_data"])


def read_log(path: str) -> dict:
    """Read log file content (fallback for historical logs)."""
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf8') as f:
                return {"logs": f.read(), "path": path}
        except Exception as e:
            return {"error": f"Failed to read log: {str(e)}", "path": path}
    return {"logs": "", "path": path, "message": "Log file not found"}


async def log_stream_generator(buffer_name: str):
    """Generate Server-Sent Events from log buffer."""
    last_index = 0
    while True:
        buffer = log_buffers[buffer_name]
        if len(buffer) > last_index:
            # Send new logs
            for i in range(last_index, len(buffer)):
                yield f"data: {buffer[i]}\n\n"
            last_index = len(buffer)
        await asyncio.sleep(0.5)  # Poll interval


@router.get("/stream/system-diagrams")
async def stream_system_diagrams_logs():
    """Stream Antenna System Diagrams logs in real-time (SSE)."""
    return StreamingResponse(
        log_stream_generator("system_diagrams"),
        media_type="text/event-stream"
    )


@router.get("/stream/tx-diagrams")
async def stream_tx_diagrams_logs():
    """Stream TX Antenna Diagrams logs in real-time (SSE)."""
    return StreamingResponse(
        log_stream_generator("tx_diagrams"),
        media_type="text/event-stream"
    )


@router.get("/stream/antenna-patterns")
async def stream_antenna_patterns_logs():
    """Stream Antenna Patterns logs in real-time (SSE)."""
    return StreamingResponse(
        log_stream_generator("antenna_patterns"),
        media_type="text/event-stream"
    )


@router.get("/stream/main-load-data")
async def stream_main_load_data_logs():
    """Stream Main Load Data parser logs in real-time (SSE)."""
    return StreamingResponse(
        log_stream_generator("main_load_data"),
        media_type="text/event-stream"
    )


@router.get("/system-diagrams")
def get_system_diagrams_logs():
    """Get buffered Antenna System Diagrams logs."""
    return list(log_buffers["system_diagrams"])


@router.get("/tx-diagrams")
def get_tx_diagrams_logs():
    """Get buffered TX Antenna Diagrams logs."""
    return list(log_buffers["tx_diagrams"])


@router.get("/antenna-patterns")
def get_antenna_patterns_logs():
    """Get buffered Antenna Patterns logs."""
    return list(log_buffers["antenna_patterns"])


@router.get("/main-load-data")
def get_main_load_data_logs():
    """Get buffered Main Load Data parser logs."""
    return list(log_buffers["main_load_data"])


@router.get("/all")
def get_all_logs():
    """Get all buffered logs."""
    return {
        "system_diagrams": list(log_buffers["system_diagrams"]),
        "tx_diagrams": list(log_buffers["tx_diagrams"]),
        "antenna_patterns": list(log_buffers["antenna_patterns"]),
        "main_load_data": list(log_buffers["main_load_data"])
    }
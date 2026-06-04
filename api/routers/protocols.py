from fastapi import FastAPI, UploadFile, File, APIRouter, Depends

from shared.parse_controller import ParseController

import os
import tempfile

router = APIRouter()

def get_controller() -> ParseController:
    return ParseController()

@router.post("/upload")
async def upload_protocols(
    files: list[UploadFile] = File(...),
    controller: ParseController = Depends(get_controller)
):
    paths = []
    for f in files:
        # UploadFile.filename can be None, so normalize to a string first.
        filename = f.filename or ""
        suffix = os.path.splitext(filename)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(await f.read())
        tmp.close()
        paths.append(tmp.name)

    # hand paths to ParseController — same method your desktop app calls
    result = controller.build_prot_path_type_list(
        paths,
        burn_in_cal_mode=0,        # 0 = normal mode, not burn-in/cal
        include_burn_in_start=False
    )

    return {"protocols": result}   # serialize result to JSON → back to Streamlit
@router.get("/count")         # ← another endpoint on same router
def protocol_count():
    return {"count": 42}
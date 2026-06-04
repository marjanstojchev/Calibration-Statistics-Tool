from fastapi import FastAPI, UploadFile, File

from api.routers import protocols

app = FastAPI()

app.include_router(protocols.router, prefix="/api/protocols", tags=["protocols"])

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/api/parse")
async def parse_file(file: UploadFile = File(...)):
    contents = await file.read()
    # TODO: call your ParseController here
    return {"filename": file.filename, "size": len(contents)}

@app.post("/api/prot")
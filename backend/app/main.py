import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api import router
from .database import Base, engine

logging.basicConfig(level=logging.INFO,format='%(message)s'); log=logging.getLogger("channelbridge")
app=FastAPI(title="ChannelBridge API",version="1.0.0",description="Independent educational partner-integration simulator")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://localhost:4173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.on_event("startup")
def startup(): Base.metadata.create_all(engine)
@app.middleware("http")
async def observe(req:Request,call_next):
    rid=req.headers.get("x-request-id",str(uuid.uuid4()));start=time.perf_counter()
    try: res=await call_next(req)
    except Exception: log.exception("request_failed request_id=%s path=%s",rid,req.url.path);raise
    res.headers["X-Request-ID"]=rid;res.headers["X-Content-Type-Options"]="nosniff";res.headers["X-Frame-Options"]="DENY";log.info("request request_id=%s operation=%s status=%s duration_ms=%.2f",rid,req.url.path,res.status_code,(time.perf_counter()-start)*1000);return res
@app.get("/health")
def health():return {"status":"healthy","service":"channelbridge-api"}
@app.get("/ready")
def ready():return {"status":"ready"}
app.include_router(router)

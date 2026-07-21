from fastapi import FastAPI, Request

app=FastAPI(title="ChannelBridge internal webhook simulator")
events=[]
@app.post("/events",status_code=204)
async def receive(request:Request): events.append({"signature":bool(request.headers.get("x-channelbridge-signature")),"size":len(await request.body())})
@app.get("/events")
def list_events():return events[-100:]
@app.get("/health")
def health():return {"status":"healthy"}


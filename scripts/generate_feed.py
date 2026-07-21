#!/usr/bin/env python3
import argparse,json
from datetime import datetime,timezone
def generate(count:int,invalid_every:int=0):
    programs=[]
    for n in range(count):
        bad=invalid_every and n%invalid_every==0
        programs.append({"content_id":f"GEN-MOV-{n:06d}" if not bad else "BAD ID","type":"movie","title":f"The Quiet Meridian {n}","description":"A deterministic fictional program generated for local performance testing.","language":"en-US","territories":["XX" if bad else "US"],"artwork":{"url":"https://example.invalid/generated.jpg","width":1920,"height":1080},"availability":[{"territory":"US","starts_at":"2026-08-01T00:00:00Z","ends_at":"2027-08-01T00:00:00Z"}]})
    return {"feed_version":"1.0","partner_id":"generated-benchmark","generated_at":datetime.now(timezone.utc).isoformat(),"programs":programs}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--records",type=int,default=1000);p.add_argument("--invalid-every",type=int,default=0);p.add_argument("--output",default="generated-feed.json");a=p.parse_args();open(a.output,"w").write(json.dumps(generate(a.records,a.invalid_every)));print(a.output)


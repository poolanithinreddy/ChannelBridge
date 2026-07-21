import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

from defusedxml import ElementTree as ET


@dataclass
class Finding:
    code:str; category:str; severity:str; message:str; fix:str; row:int|None=None; field:str|None=None; content_id:str|None=None
    @property
    def fingerprint(self): return hashlib.sha256(f"v1|{self.code}|{self.content_id or self.row}|{self.field}".encode()).hexdigest()

LANGUAGES={"en","en-US","en-GB","es","es-MX","fr","fr-CA","de","ja","ko"}
TERRITORIES={"US","CA","GB","MX","FR","DE","JP","KR","AU","NZ"}
def issue(code,cat,sev,msg,fix,row=None,field=None,cid=None): return Finding(code,cat,sev,msg,fix,row,field,cid)
def parse_feed(data: bytes, fmt: str):
    if fmt=="json": return json.loads(data.decode("utf-8"))
    root=ET.fromstring(data)
    if root.tag!="channelbridge_feed": raise ValueError("Unexpected XML root; expected channelbridge_feed")
    programs=[]
    for p in root.findall("./programs/program"):
        item: dict[str, object] = {
            c.tag: c.text
            for c in p
            if c.tag not in ("territories", "availability", "artwork")
        }
        item["territories"]=[x.text for x in p.findall("./territories/territory")]
        art=p.find("artwork"); item["artwork"]={c.tag:c.text for c in art} if art is not None else None
        item["availability"]=[{c.tag:c.text for c in w} for w in p.findall("./availability/window")]
        programs.append(item)
    return {"feed_version":root.get("version"),"partner_id":root.findtext("partner_id"),"programs":programs}
def validate(payload: dict)->list[Finding]:
    out=[]; seen=set(); programs=payload.get("programs") or []
    if payload.get("feed_version")!="1.0": out.append(issue("SCHEMA_UNSUPPORTED","file_schema","error","Only ChannelBridge feed version 1.0 is supported.","Set feed_version to 1.0.",field="feed_version"))
    if not payload.get("partner_id"): out.append(issue("FEED_PARTNER_REQUIRED","file_schema","error","Feed partner_id is missing.","Add the fictional partner slug.",field="partner_id"))
    for n,p in enumerate(programs,1):
        cid=str(p.get("content_id") or "").strip() or None
        def add(code,cat,sev,msg,fix,field): out.append(issue(code,cat,sev,msg,fix,n,field,cid))
        if not cid: add("ID_REQUIRED","identifiers","error","This record has no content ID.","Add a stable content_id such as NSM-MOV-001.","content_id")
        elif not re.fullmatch(r"[A-Za-z0-9._-]+",cid): add("ID_CHARACTERS","identifiers","error","The content ID contains unsupported characters.","Use letters, numbers, dots, underscores, or hyphens.","content_id")
        elif cid in seen: add("ID_DUPLICATE_FEED","identifiers","error","This content ID occurs more than once in the feed.","Keep one record or assign a unique ID.","content_id")
        seen.add(cid)
        for f in ("title","description","type"):
            if not str(p.get(f) or "").strip(): add(f"META_{f.upper()}_REQUIRED","required_metadata","error",f"Required {f} is empty.",f"Provide a meaningful {f}.",f)
        lang=p.get("language")
        if lang not in LANGUAGES: add("LANG_UNSUPPORTED","language_territory","error",f"Language '{lang}' is not in the demo-supported set.","Use a documented BCP 47 tag such as en-US.","language")
        territories=p.get("territories") or []
        for terr in territories:
            if terr not in TERRITORIES: add("TERRITORY_INVALID","language_territory","error",f"Territory '{terr}' is unsupported or invalid.","Use a documented two-letter territory such as US.","territories")
        if len(territories)!=len(set(territories)): add("TERRITORY_DUPLICATE","language_territory","warning","A territory appears more than once.","Remove repeated territory entries.","territories")
        art=p.get("artwork")
        if not art: add("ARTWORK_MISSING","artwork","warning","Artwork is missing, reducing catalog quality.","Add HTTPS artwork metadata with 16:9 dimensions.","artwork")
        else:
            url=str(art.get("url") or ""); parsed=urlparse(url)
            if parsed.scheme!="https" or not parsed.hostname: add("ARTWORK_URL_INVALID","artwork","error","Artwork URL must be a valid HTTPS URL.","Provide an https:// URL; ChannelBridge does not fetch it.","artwork.url")
            try: w,h=int(art.get("width",0)),int(art.get("height",0))
            except (TypeError,ValueError): w=h=0
            if w<=0 or h<=0: add("ARTWORK_DIMENSIONS","artwork","error","Artwork dimensions are missing or invalid.","Provide positive numeric width and height.","artwork")
            elif abs(w/h-16/9)>.08: add("ARTWORK_ASPECT_RATIO","artwork","warning","Artwork is outside the recommended 16:9 ratio.","Use artwork near 1920×1080.","artwork")
        typ=p.get("type")
        if typ=="episode":
            for f in ("series_id","season_id","season_number","episode_number"):
                if not p.get(f): add(f"HIERARCHY_{f.upper()}_REQUIRED","series_hierarchy","error",f"Episode is missing {f}.",f"Add the episode's {f}.",f)
        if typ=="movie" and any(p.get(f) for f in ("series_id","season_id","season_number","episode_number")): add("HIERARCHY_MOVIE_EPISODE_FIELDS","series_hierarchy","error","A movie contains episodic hierarchy fields.","Remove series, season, and episode fields.","type")
        windows=p.get("availability") or []
        if not windows: add("AVAILABILITY_MISSING","dates_timezones","warning","No availability window is defined.","Add at least one future availability window.","availability")
        for window in windows:
            try:
                start=datetime.fromisoformat(str(window.get("starts_at","")).replace("Z","+00:00")); end=datetime.fromisoformat(str(window.get("ends_at","")).replace("Z","+00:00"))
                if end<=start: add("AVAILABILITY_ORDER","dates_timezones","error","Availability ends before or at its start.","Set ends_at later than starts_at.","availability")
            except ValueError: add("DATETIME_INVALID","dates_timezones","error","Availability contains an invalid ISO 8601 timestamp.","Use a timezone-aware value such as 2027-01-01T00:00:00Z.","availability")
    return out

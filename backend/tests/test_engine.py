import json

from app.services import backoff, sign
from app.validation.engine import parse_feed, validate


def valid():return {"feed_version":"1.0","partner_id":"northstar-media","programs":[{"content_id":"NSM-MOV-1","type":"movie","title":"Glass Atlas","description":"A fictional journey.","language":"en-US","territories":["US"],"artwork":{"url":"https://example.invalid/a.jpg","width":1920,"height":1080},"availability":[{"territory":"US","starts_at":"2026-01-01T00:00:00Z","ends_at":"2027-01-01T00:00:00Z"}]}]}
def test_valid_json_is_deterministic():
    data=json.dumps(valid()).encode();one=validate(parse_feed(data,"json"));two=validate(parse_feed(data,"json"));assert [x.fingerprint for x in one]==[x.fingerprint for x in two];assert one==[]
def test_actionable_validation():
    feed=valid();feed["programs"][0]["territories"]=["XX","XX"];feed["programs"][0]["availability"][0]["ends_at"]="2020-01-01T00:00:00Z";codes={x.code for x in validate(feed)};assert {"TERRITORY_INVALID","TERRITORY_DUPLICATE","AVAILABILITY_ORDER"}<=codes
def test_backoff_bounded_and_deterministic():assert backoff(20,4)<=301 and backoff(3,4)==backoff(3,4)
def test_webhook_signature():assert sign("secret",b"hello")=="sha256=88aab3ede8d3adf94d26ab90d3bafd4a2083070c3bcce9c014ee04a443847c0b"

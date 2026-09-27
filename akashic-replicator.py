#!/usr/bin/env python3
"""Replicate Cosmic UTM state events to the durable B612 Akashic node."""
import json, os, time
from pathlib import Path
from urllib.request import Request, urlopen

REMOTE=os.getenv("AKASHIC_REMOTE_URL","http://paper-uhef-worker.railway.internal:8080/akashic/b612")
TOKEN=os.getenv("AKASHIC_REPLICA_TOKEN","")
JOURNAL=Path(os.getenv("TM_OPERATION_JOURNAL","/data/cosmic-love-operations.jsonl"))
RESIDENTS=Path(os.getenv("RESIDENT_PATH","/data/residents.json"))
POLL=float(os.getenv("AKASHIC_REPLICA_POLL","1"))
SERVICE=os.getenv("RAILWAY_SERVICE_NAME","cosmic-love-infinity-tm")
DEPLOYMENT=os.getenv("RAILWAY_DEPLOYMENT_ID","")

def post(payload):
    if not TOKEN:return False
    body=json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode()
    req=Request(REMOTE,data=body,headers={"content-type":"application/json","authorization":"Bearer "+TOKEN},method="POST")
    try:
        with urlopen(req,timeout=5) as r:
            return 200 <= r.status < 300
    except Exception as e:
        print(json.dumps({"event":"akashic_replica_error","error":type(e).__name__},separators=(",",":")),flush=True)
        return False

def lines():
    try:return JOURNAL.read_text(encoding="utf-8").splitlines()
    except OSError:return []

sent=0
resident_stamp=None
while True:
    rows=lines()
    while sent < len(rows):
        try:record=json.loads(rows[sent])
        except ValueError:
            sent += 1;continue
        payload={"type":"cosmic_tm_commit","source_service":SERVICE,"source_deployment":DEPLOYMENT,"source_seq":sent,"record":record}
        if not post(payload):break
        sent += 1
    try:stamp=RESIDENTS.stat().st_mtime_ns
    except OSError:stamp=None
    if stamp is not None and stamp != resident_stamp:
        try:snapshot=json.loads(RESIDENTS.read_text(encoding="utf-8"))
        except (OSError,ValueError):snapshot={}
        if post({"type":"resident_snapshot","source_service":SERVICE,"source_deployment":DEPLOYMENT,"residents":snapshot}):resident_stamp=stamp
    time.sleep(max(.2,POLL))
